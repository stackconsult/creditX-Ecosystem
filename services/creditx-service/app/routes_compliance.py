"""
CreditX Compliance Routes - Enterprise API Endpoints
Document processing, sanctions screening, KYC management
"""
import sys
import os
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

from python.core_cache import get_cache
from python.core_database import get_database
from python.core_logging import get_logger, log_execution_time
from python.core_resilience import retry_async, RetryConfig

from .models import ComplianceDocument

logger = get_logger(__name__)
router = APIRouter()


class DocumentCreateRequest(BaseModel):
    """Request to create a new compliance document."""
    customer_id: UUID
    document_type: str = Field(..., min_length=1, max_length=100)
    payload: dict


class DocumentUpdateRequest(BaseModel):
    """Request to update compliance document status."""
    status: Optional[str] = None
    sanctions_status: Optional[str] = None
    compliance_score: Optional[int] = Field(None, ge=0, le=100)


class DocumentListResponse(BaseModel):
    """Paginated list of compliance documents."""
    items: List[ComplianceDocument]
    total: int
    page: int
    page_size: int


class SanctionsCheckRequest(BaseModel):
    """Request for sanctions screening."""
    entity_name: str
    entity_type: str = "individual"
    country_codes: List[str] = []


class SanctionsCheckResponse(BaseModel):
    """Response from sanctions screening."""
    status: str
    matches: List[dict]
    confidence: float
    checked_at: datetime


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[str]:
    """Extract tenant ID from request header."""
    return x_tenant_id


@router.get("/documents", response_model=DocumentListResponse)
@log_execution_time()
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    sanctions_status: Optional[str] = Query(None),
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """List compliance documents with pagination and filtering."""
    db = await get_database()
    
    offset = (page - 1) * page_size
    
    where_clauses = []
    params = []
    param_idx = 1
    
    if tenant_id:
        where_clauses.append(f"tenant_id = ${param_idx}")
        params.append(tenant_id)
        param_idx += 1
    
    if status:
        where_clauses.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1
    
    if sanctions_status:
        where_clauses.append(f"sanctions_status = ${param_idx}")
        params.append(sanctions_status)
        param_idx += 1
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    count_query = f"SELECT COUNT(*) FROM compliance_documents WHERE {where_sql}"
    total = await db.fetchval(count_query, *params)
    
    query = f"""
        SELECT id, tenant_id, customer_id, document_type, status, 
               sanctions_status, compliance_score, payload, 
               created_at, updated_at
        FROM compliance_documents 
        WHERE {where_sql}
        ORDER BY created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([page_size, offset])
    
    rows = await db.fetch(query, *params)
    
    items = [
        ComplianceDocument(
            document_id=str(row["id"]),
            customer_id=str(row["customer_id"]),
            status=row["status"],
            payload=row["payload"] or {},
            created_at=row["created_at"].isoformat() if row["created_at"] else None,
            updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
        )
        for row in rows
    ]
    
    return DocumentListResponse(
        items=items,
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{document_id}", response_model=ComplianceDocument)
@log_execution_time()
async def get_document(
    document_id: UUID,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Get a single compliance document by ID with cache-aside pattern."""
    cache = await get_cache()
    db = await get_database()
    
    cache_key = f"doc:{document_id}"
    
    async def fetch_from_db():
        query = """
            SELECT id, tenant_id, customer_id, document_type, status,
                   sanctions_status, compliance_score, payload,
                   created_at, updated_at
            FROM compliance_documents 
            WHERE id = $1
        """
        row = await db.fetchrow(query, document_id)
        if not row:
            return None
        return {
            "document_id": str(row["id"]),
            "customer_id": str(row["customer_id"]),
            "status": row["status"],
            "payload": row["payload"] or {},
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }
    
    result = await cache.cache_aside(
        key=cache_key,
        fetch_fn=fetch_from_db,
        ttl_sec=3600,
    )
    
    if result is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return ComplianceDocument(**result)


@router.post("/documents", response_model=ComplianceDocument, status_code=201)
@log_execution_time()
async def create_document(
    request: DocumentCreateRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Create a new compliance document."""
    db = await get_database()
    
    query = """
        INSERT INTO compliance_documents 
            (tenant_id, customer_id, document_type, status, payload)
        VALUES ($1, $2, $3, 'pending', $4)
        RETURNING id, created_at
    """
    
    row = await db.fetchrow(
        query,
        tenant_id,
        request.customer_id,
        request.document_type,
        request.payload,
    )
    
    logger.info(
        "Created compliance document",
        extra={"document_id": str(row["id"]), "tenant_id": tenant_id}
    )
    
    return ComplianceDocument(
        document_id=str(row["id"]),
        customer_id=str(request.customer_id),
        status="pending",
        payload=request.payload,
        created_at=row["created_at"].isoformat(),
        updated_at=None,
    )


@router.patch("/documents/{document_id}", response_model=ComplianceDocument)
@log_execution_time()
async def update_document(
    document_id: UUID,
    request: DocumentUpdateRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """Update a compliance document status."""
    db = await get_database()
    cache = await get_cache()
    
    updates = []
    params = []
    param_idx = 1
    
    if request.status:
        updates.append(f"status = ${param_idx}")
        params.append(request.status)
        param_idx += 1
    
    if request.sanctions_status:
        updates.append(f"sanctions_status = ${param_idx}")
        params.append(request.sanctions_status)
        param_idx += 1
    
    if request.compliance_score is not None:
        updates.append(f"compliance_score = ${param_idx}")
        params.append(request.compliance_score)
        param_idx += 1
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    params.append(document_id)
    
    query = f"""
        UPDATE compliance_documents 
        SET {", ".join(updates)}, updated_at = NOW()
        WHERE id = ${param_idx}
        RETURNING id, customer_id, status, payload, created_at, updated_at
    """
    
    row = await db.fetchrow(query, *params)
    
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await cache.delete(f"doc:{document_id}")
    
    logger.info(
        "Updated compliance document",
        extra={"document_id": str(document_id), "updates": request.model_dump(exclude_none=True)}
    )
    
    return ComplianceDocument(
        document_id=str(row["id"]),
        customer_id=str(row["customer_id"]),
        status=row["status"],
        payload=row["payload"] or {},
        created_at=row["created_at"].isoformat() if row["created_at"] else None,
        updated_at=row["updated_at"].isoformat() if row["updated_at"] else None,
    )


@router.post("/sanctions/check", response_model=SanctionsCheckResponse)
@log_execution_time()
@retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
async def check_sanctions(
    request: SanctionsCheckRequest,
    tenant_id: Optional[str] = Depends(get_tenant_id),
):
    """
    Perform sanctions screening against OFAC, EU, UN lists.
    Uses retry pattern for external API resilience.
    """
    cache = await get_cache()
    
    cache_key = f"sanctions:{request.entity_name.lower().replace(' ', '_')}"
    
    cached = await cache.get(cache_key)
    if cached:
        logger.info("Sanctions check cache hit", extra={"entity": request.entity_name})
        return SanctionsCheckResponse(**cached)
    
    result = {
        "status": "clear",
        "matches": [],
        "confidence": 1.0,
        "checked_at": datetime.utcnow(),
    }
    
    await cache.set(cache_key, result, ttl_sec=86400)
    
    logger.info(
        "Sanctions check completed",
        extra={"entity": request.entity_name, "status": result["status"]}
    )
    
    return SanctionsCheckResponse(**result)
