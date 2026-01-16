from fastapi import APIRouter, HTTPException
from .db import database
from .models import ComplianceDocument
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.python.core_cache import DragonflyCache
from pybreaker import CircuitBreaker, CircuitBreakerError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/creditx", tags=["creditx"])

cache = DragonflyCache()
cache_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)


@cache_breaker
async def _safe_cache_get(key: str):
    return await cache.get(key)


async def get_with_guard(key: str, fetch_fn, ttl_sec: int):
    try:
        cached = await _safe_cache_get(key)
        if cached is not None:
            return cached
    except CircuitBreakerError:
        logger.warning("Cache circuit OPEN, falling back to DB for %s", key)
        return await fetch_fn()

    value = await fetch_fn()
    await cache.set(key, value, ttl_sec)
    return value


@router.on_event("startup")
async def startup():
    await database.connect()
    await cache.connect()


@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await cache.close()


@router.get("/documents/{document_id}", response_model=ComplianceDocument)
async def get_document(document_id: str):
    async def fetch():
        row = await database.fetch_one(
            "SELECT * FROM compliance_documents WHERE document_id = :id",
            {"id": document_id},
        )
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        return dict(row)

    key = f"doc:{document_id}"
    result = await get_with_guard(key, fetch, ttl_sec=7 * 24 * 3600)
    return ComplianceDocument(**result)
