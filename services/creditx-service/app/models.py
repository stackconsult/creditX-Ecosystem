from pydantic import BaseModel
from typing import Optional


class ComplianceDocument(BaseModel):
    document_id: str
    customer_id: str
    status: str
    payload: dict
    created_at: str
    updated_at: Optional[str]
