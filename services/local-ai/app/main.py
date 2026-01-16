"""
Local AI Service - Qwen Auto-Trainer
On-premise model serving and continuous fine-tuning
OpenAI-compatible API for seamless integration
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INFERENCE_COUNT = Counter("local_ai_inference_total", "Total inference requests")
INFERENCE_LATENCY = Histogram("local_ai_inference_latency_seconds", "Inference latency")
TRAINING_JOBS = Counter("local_ai_training_jobs_total", "Total training jobs", ["status"])


class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "qwen-2.5-7b"
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: Optional[int] = 2048
    stream: bool = False


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: Message
    finish_reason: str = "stop"


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: Usage


class TrainingRequest(BaseModel):
    dataset_path: str
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    output_name: str
    epochs: int = 3
    learning_rate: float = 2e-5
    batch_size: int = 4
    lora_rank: int = 16
    lora_alpha: int = 32


class TrainingJob(BaseModel):
    job_id: str
    status: str
    base_model: str
    output_name: str
    progress: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class ModelInfo(BaseModel):
    model_id: str
    base_model: str
    status: str
    loaded: bool
    parameters: int
    quantization: Optional[str] = None


_model = None
_tokenizer = None
_training_jobs: Dict[str, TrainingJob] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Local AI Service")
    
    if os.getenv("AUTO_LOAD_MODEL", "false").lower() == "true":
        await load_model("Qwen/Qwen2.5-7B-Instruct")
    
    yield
    
    logger.info("Shutting down Local AI Service")


app = FastAPI(
    title="Local AI Service - Qwen Auto-Trainer",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def load_model(model_id: str, quantization: Optional[str] = "4bit"):
    """Load a model into memory."""
    global _model, _tokenizer
    
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        import torch
        
        logger.info(f"Loading model: {model_id}")
        
        _tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        
        if quantization == "4bit":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            _model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            _model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                torch_dtype=torch.bfloat16,
                trust_remote_code=True,
            )
        
        logger.info(f"Model loaded successfully: {model_id}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


def run_training_job(job: TrainingJob, request: TrainingRequest):
    """Background training job execution."""
    try:
        from datasets import load_dataset
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            BitsAndBytesConfig,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
        import torch
        
        job.status = "running"
        job.started_at = datetime.utcnow().isoformat()
        TRAINING_JOBS.labels(status="started").inc()
        
        logger.info(f"Starting training job: {job.job_id}")
        
        tokenizer = AutoTokenizer.from_pretrained(request.base_model, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            request.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        model = prepare_model_for_kbit_training(model)
        
        lora_config = LoraConfig(
            r=request.lora_rank,
            lora_alpha=request.lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        model = get_peft_model(model, lora_config)
        
        dataset = load_dataset("json", data_files=request.dataset_path, split="train")
        
        output_dir = f"/models/finetuned/{request.output_name}"
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=request.epochs,
            per_device_train_batch_size=request.batch_size,
            gradient_accumulation_steps=4,
            learning_rate=request.learning_rate,
            logging_steps=10,
            save_steps=100,
            warmup_ratio=0.03,
            optim="paged_adamw_32bit",
            fp16=True,
            report_to="none",
        )
        
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            tokenizer=tokenizer,
            args=training_args,
            max_seq_length=2048,
        )
        
        trainer.train()
        
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        job.status = "completed"
        job.progress = 100.0
        job.completed_at = datetime.utcnow().isoformat()
        TRAINING_JOBS.labels(status="completed").inc()
        
        logger.info(f"Training job completed: {job.job_id}")
        
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.utcnow().isoformat()
        TRAINING_JOBS.labels(status="failed").inc()
        logger.error(f"Training job failed: {job.job_id} - {e}")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "local-ai", "model_loaded": _model is not None}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint."""
    models = [
        {
            "id": "qwen-2.5-7b",
            "object": "model",
            "owned_by": "local",
            "permission": [],
        }
    ]
    
    return {"object": "list", "data": models}


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint."""
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    INFERENCE_COUNT.inc()
    
    with INFERENCE_LATENCY.time():
        try:
            import torch
            
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            
            text = _tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            
            inputs = _tokenizer(text, return_tensors="pt").to(_model.device)
            
            with torch.no_grad():
                outputs = _model.generate(
                    **inputs,
                    max_new_tokens=request.max_tokens,
                    temperature=request.temperature,
                    do_sample=request.temperature > 0,
                    pad_token_id=_tokenizer.eos_token_id,
                )
            
            response_text = _tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True,
            )
            
            prompt_tokens = inputs.input_ids.shape[1]
            completion_tokens = outputs.shape[1] - prompt_tokens
            
            return ChatCompletionResponse(
                id=f"chatcmpl-{datetime.utcnow().timestamp()}",
                created=int(datetime.utcnow().timestamp()),
                model=request.model,
                choices=[
                    ChatCompletionChoice(
                        message=Message(role="assistant", content=response_text),
                    )
                ],
                usage=Usage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                ),
            )
        
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/models/load")
async def load_model_endpoint(model_id: str, quantization: Optional[str] = "4bit"):
    """Load a model into memory."""
    success = await load_model(model_id, quantization)
    if success:
        return {"status": "loaded", "model": model_id}
    raise HTTPException(status_code=500, detail="Failed to load model")


@app.post("/v1/training/start", response_model=TrainingJob)
async def start_training(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
):
    """Start a fine-tuning job."""
    import uuid
    
    job_id = str(uuid.uuid4())
    
    job = TrainingJob(
        job_id=job_id,
        status="queued",
        base_model=request.base_model,
        output_name=request.output_name,
    )
    
    _training_jobs[job_id] = job
    
    background_tasks.add_task(run_training_job, job, request)
    
    return job


@app.get("/v1/training/{job_id}", response_model=TrainingJob)
async def get_training_status(job_id: str):
    """Get training job status."""
    if job_id not in _training_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _training_jobs[job_id]


@app.get("/v1/training", response_model=List[TrainingJob])
async def list_training_jobs():
    """List all training jobs."""
    return list(_training_jobs.values())
