import logging
from fastapi import FastAPI
from .routes_compliance import router as compliance_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="CreditX Service", version="2.0.0-dragonfly")


@app.get("/health/live")
async def live():
    return {"status": "ok"}


@app.get("/health/ready")
async def ready():
    return {"status": "ready"}


app.include_router(compliance_router)
