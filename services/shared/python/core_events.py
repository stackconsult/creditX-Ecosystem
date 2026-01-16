"""
Enterprise Event Bus - Redis Streams Based
- Agent-to-agent communication via Dragonfly Streams
- Consumer groups for reliable delivery
- Dead letter queue for failed messages
- Event replay capability
"""
import json
import logging
import os
import asyncio
from typing import Any, Callable, Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standard event types for the ecosystem."""
    DOCUMENT_CREATED = "document.created"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_APPROVED = "document.approved"
    DOCUMENT_REJECTED = "document.rejected"
    
    THREAT_DETECTED = "threat.detected"
    THREAT_RESOLVED = "threat.resolved"
    THREAT_ESCALATED = "threat.escalated"
    
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    
    NOTIFICATION_REQUESTED = "notification.requested"
    NOTIFICATION_SENT = "notification.sent"
    
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"


@dataclass
class Event:
    """Standard event structure."""
    event_type: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    source_service: str = ""
    tenant_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    def to_stream_data(self) -> Dict[str, str]:
        """Convert to Redis Stream format (all values must be strings)."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": json.dumps(self.payload, default=str),
            "timestamp": self.timestamp,
            "source_service": self.source_service,
            "tenant_id": self.tenant_id or "",
            "correlation_id": self.correlation_id or "",
            "metadata": json.dumps(self.metadata, default=str),
        }
    
    @classmethod
    def from_stream_data(cls, data: Dict[bytes, bytes]) -> "Event":
        """Parse from Redis Stream format."""
        decoded = {k.decode(): v.decode() for k, v in data.items()}
        return cls(
            event_id=decoded.get("event_id", ""),
            event_type=decoded.get("event_type", ""),
            payload=json.loads(decoded.get("payload", "{}")),
            timestamp=decoded.get("timestamp", ""),
            source_service=decoded.get("source_service", ""),
            tenant_id=decoded.get("tenant_id") or None,
            correlation_id=decoded.get("correlation_id") or None,
            metadata=json.loads(decoded.get("metadata", "{}")),
        )


class EventBus:
    """
    Enterprise event bus using Dragonfly Streams.
    Supports pub/sub patterns with consumer groups for reliability.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        service_name: str = "unknown",
        max_connections: int = 20,
    ):
        self.host = host or os.getenv("CACHE_HOST", "dragonfly-cache.internal")
        self.port = port or int(os.getenv("CACHE_PORT", "6379"))
        self.service_name = service_name
        self.max_connections = max_connections
        
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._connected = False
        self._handlers: Dict[str, List[Callable]] = {}
        self._consumer_tasks: List[asyncio.Task] = []
    
    async def connect(self) -> None:
        """Initialize connection to Dragonfly."""
        if self._connected:
            return
        
        self._pool = ConnectionPool(
            host=self.host,
            port=self.port,
            max_connections=self.max_connections,
            decode_responses=False,
        )
        self._client = redis.Redis(connection_pool=self._pool)
        await self._client.ping()
        self._connected = True
        logger.info(f"EventBus connected to {self.host}:{self.port}")
    
    async def close(self) -> None:
        """Gracefully shutdown."""
        for task in self._consumer_tasks:
            task.cancel()
        
        if self._consumer_tasks:
            await asyncio.gather(*self._consumer_tasks, return_exceptions=True)
        
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.disconnect()
        
        self._connected = False
        logger.info("EventBus disconnected")
    
    async def publish(
        self,
        stream: str,
        event: Event,
        maxlen: int = 10000,
    ) -> str:
        """
        Publish event to a stream.
        Returns the message ID.
        """
        event.source_service = self.service_name
        
        try:
            message_id = await self._client.xadd(
                stream,
                event.to_stream_data(),
                maxlen=maxlen,
            )
            
            logger.debug(
                f"Published {event.event_type} to {stream}",
                extra={"event_id": event.event_id, "message_id": message_id}
            )
            
            return message_id.decode() if isinstance(message_id, bytes) else message_id
        
        except Exception as e:
            logger.error(f"Failed to publish to {stream}: {e}")
            raise
    
    async def subscribe(
        self,
        stream: str,
        handler: Callable[[Event], Any],
        group: Optional[str] = None,
        consumer: Optional[str] = None,
        batch_size: int = 10,
        block_ms: int = 5000,
    ) -> None:
        """
        Subscribe to a stream with optional consumer group.
        Handler is called for each event.
        """
        group = group or f"{self.service_name}-group"
        consumer = consumer or f"{self.service_name}-{uuid.uuid4().hex[:8]}"
        
        try:
            await self._client.xgroup_create(stream, group, id="0", mkstream=True)
            logger.info(f"Created consumer group {group} for {stream}")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
        
        async def consume():
            while True:
                try:
                    messages = await self._client.xreadgroup(
                        groupname=group,
                        consumername=consumer,
                        streams={stream: ">"},
                        count=batch_size,
                        block=block_ms,
                    )
                    
                    if not messages:
                        continue
                    
                    for stream_name, stream_messages in messages:
                        for message_id, data in stream_messages:
                            try:
                                event = Event.from_stream_data(data)
                                
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(event)
                                else:
                                    handler(event)
                                
                                await self._client.xack(stream, group, message_id)
                                
                            except Exception as e:
                                logger.error(
                                    f"Handler failed for {message_id}: {e}",
                                    extra={"stream": stream, "group": group}
                                )
                
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Consumer error: {e}")
                    await asyncio.sleep(1)
        
        task = asyncio.create_task(consume())
        self._consumer_tasks.append(task)
        logger.info(f"Subscribed to {stream} as {consumer} in group {group}")
    
    async def get_pending(
        self,
        stream: str,
        group: str,
        count: int = 100,
    ) -> List[Dict]:
        """Get pending messages that haven't been acknowledged."""
        pending = await self._client.xpending_range(
            stream, group, min="-", max="+", count=count
        )
        return [
            {
                "message_id": p["message_id"].decode(),
                "consumer": p["consumer"].decode(),
                "time_since_delivered": p["time_since_delivered"],
                "times_delivered": p["times_delivered"],
            }
            for p in pending
        ]
    
    async def claim_stale(
        self,
        stream: str,
        group: str,
        consumer: str,
        min_idle_ms: int = 60000,
        count: int = 10,
    ) -> List[Event]:
        """Claim stale messages from dead consumers."""
        messages = await self._client.xautoclaim(
            stream, group, consumer, min_idle_time=min_idle_ms, count=count
        )
        
        events = []
        if messages and len(messages) > 1:
            for message_id, data in messages[1]:
                if data:
                    events.append(Event.from_stream_data(data))
        
        return events
    
    async def replay(
        self,
        stream: str,
        start_id: str = "0",
        end_id: str = "+",
        count: int = 100,
    ) -> List[Event]:
        """Replay events from a stream."""
        messages = await self._client.xrange(
            stream, min=start_id, max=end_id, count=count
        )
        
        return [Event.from_stream_data(data) for _, data in messages]


_event_bus_instance: Optional[EventBus] = None


async def get_event_bus(service_name: str = "unknown") -> EventBus:
    """Get singleton event bus instance."""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus(service_name=service_name)
        await _event_bus_instance.connect()
    return _event_bus_instance
