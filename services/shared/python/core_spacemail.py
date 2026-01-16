"""
Spacemail Integration - Enterprise Email Service
- HIPAA-ready transactional email
- Template-based notifications
- Delivery tracking and analytics
- Retry with exponential backoff
"""
import logging
import os
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

import httpx

from .core_resilience import retry_async, RetryConfig

logger = logging.getLogger(__name__)


class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(str, Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    BOUNCED = "bounced"
    FAILED = "failed"


@dataclass
class EmailRecipient:
    """Email recipient with optional metadata."""
    email: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"email": self.email}
        if self.name:
            result["name"] = self.name
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class EmailMessage:
    """Email message structure."""
    to: List[EmailRecipient]
    subject: str
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    cc: List[EmailRecipient] = field(default_factory=list)
    bcc: List[EmailRecipient] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    priority: EmailPriority = EmailPriority.NORMAL
    template_id: Optional[str] = None
    template_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "to": [r.to_dict() for r in self.to],
            "subject": self.subject,
            "priority": self.priority.value,
        }
        
        if self.html_body:
            result["html"] = self.html_body
        if self.text_body:
            result["text"] = self.text_body
        if self.from_email:
            result["from"] = {"email": self.from_email, "name": self.from_name}
        if self.reply_to:
            result["reply_to"] = self.reply_to
        if self.cc:
            result["cc"] = [r.to_dict() for r in self.cc]
        if self.bcc:
            result["bcc"] = [r.to_dict() for r in self.bcc]
        if self.headers:
            result["headers"] = self.headers
        if self.attachments:
            result["attachments"] = self.attachments
        if self.template_id:
            result["template_id"] = self.template_id
            result["template_data"] = self.template_data
        if self.tags:
            result["tags"] = self.tags
        if self.metadata:
            result["metadata"] = self.metadata
        
        return result


@dataclass
class SendResult:
    """Result of email send operation."""
    message_id: str
    status: EmailStatus
    accepted: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class SpacemailClient:
    """
    Enterprise Spacemail client for transactional email.
    Included in Spaceship Hyperlift Medium bundle.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        domain: Optional[str] = None,
        base_url: str = "https://api.spacemail.spaceship.com/v1",
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("SPACEMAIL_API_KEY", "")
        self.domain = domain or os.getenv("SPACEMAIL_DOMAIN", "mail.ecosystem.ai")
        self.base_url = base_url
        self.timeout = timeout
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def send(self, message: EmailMessage) -> SendResult:
        """
        Send an email message.
        Retries on transient failures.
        """
        client = await self._get_client()
        
        payload = message.to_dict()
        if not message.from_email:
            payload["from"] = {
                "email": f"noreply@{self.domain}",
                "name": "CreditX Ecosystem"
            }
        
        try:
            response = await client.post("/messages", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            result = SendResult(
                message_id=data.get("id", str(uuid.uuid4())),
                status=EmailStatus.QUEUED,
                accepted=data.get("accepted", [r.email for r in message.to]),
                rejected=data.get("rejected", []),
            )
            
            logger.info(
                "Email sent",
                extra={
                    "message_id": result.message_id,
                    "to": [r.email for r in message.to],
                    "subject": message.subject,
                }
            )
            
            return result
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Spacemail API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    async def send_template(
        self,
        template_id: str,
        to: List[EmailRecipient],
        data: Dict[str, Any],
        subject: Optional[str] = None,
        priority: EmailPriority = EmailPriority.NORMAL,
    ) -> SendResult:
        """Send email using a template."""
        message = EmailMessage(
            to=to,
            subject=subject or "",
            template_id=template_id,
            template_data=data,
            priority=priority,
        )
        return await self.send(message)
    
    async def get_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of a message."""
        client = await self._get_client()
        
        response = await client.get(f"/messages/{message_id}")
        response.raise_for_status()
        
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Spacemail service health."""
        if not self.api_key:
            return {"status": "unconfigured", "error": "SPACEMAIL_API_KEY not set"}
        
        try:
            client = await self._get_client()
            response = await client.get("/health")
            
            if response.status_code == 200:
                return {"status": "healthy"}
            else:
                return {"status": "degraded", "code": response.status_code}
        
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class NotificationTemplates:
    """Standard notification templates for the ecosystem."""
    
    COMPLIANCE_APPROVED = "compliance_approved"
    COMPLIANCE_REJECTED = "compliance_rejected"
    COMPLIANCE_REVIEW_REQUIRED = "compliance_review_required"
    
    THREAT_ALERT = "threat_alert"
    THREAT_RESOLVED = "threat_resolved"
    
    DEVICE_REPORTED = "device_reported"
    DEVICE_FOUND = "device_found"
    
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    AGENT_HITL_REQUIRED = "agent_hitl_required"


_spacemail_instance: Optional[SpacemailClient] = None


async def get_spacemail() -> SpacemailClient:
    """Get singleton Spacemail client."""
    global _spacemail_instance
    if _spacemail_instance is None:
        _spacemail_instance = SpacemailClient()
    return _spacemail_instance
