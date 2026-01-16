"""
FastVPN Integration - Secure Tunnel Access
- Zero-logging VPN for portfolio company access
- Site-to-site tunnels for enterprise clients
- Military-grade encryption
- Dynamic tunnel provisioning
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

import httpx

from .core_resilience import retry_async, RetryConfig

logger = logging.getLogger(__name__)


class TunnelType(str, Enum):
    """VPN tunnel types."""
    SITE_TO_SITE = "site_to_site"
    CLIENT_TO_SITE = "client_to_site"
    MESH = "mesh"


class TunnelStatus(str, Enum):
    """Tunnel connection status."""
    PENDING = "pending"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class EncryptionLevel(str, Enum):
    """Encryption strength levels."""
    STANDARD = "aes-128-gcm"
    HIGH = "aes-256-gcm"
    MILITARY = "chacha20-poly1305"


@dataclass
class TunnelConfig:
    """VPN tunnel configuration."""
    tunnel_id: str
    name: str
    tunnel_type: TunnelType
    encryption: EncryptionLevel = EncryptionLevel.MILITARY
    local_network: Optional[str] = None
    remote_network: Optional[str] = None
    allowed_ips: List[str] = field(default_factory=list)
    dns_servers: List[str] = field(default_factory=list)
    keepalive_interval: int = 25
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "tunnel_id": self.tunnel_id,
            "name": self.name,
            "type": self.tunnel_type.value,
            "encryption": self.encryption.value,
            "local_network": self.local_network,
            "remote_network": self.remote_network,
            "allowed_ips": self.allowed_ips,
            "dns_servers": self.dns_servers,
            "keepalive_interval": self.keepalive_interval,
            "metadata": self.metadata,
        }


@dataclass
class TunnelConnection:
    """Active tunnel connection."""
    tunnel_id: str
    status: TunnelStatus
    connected_at: Optional[str] = None
    local_ip: Optional[str] = None
    remote_ip: Optional[str] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    latency_ms: Optional[float] = None
    last_handshake: Optional[str] = None


@dataclass
class AccessToken:
    """Client access token for VPN connection."""
    token_id: str
    tunnel_id: str
    client_id: str
    expires_at: str
    config_data: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class FastVPNClient:
    """
    Enterprise FastVPN client for secure tunnel access.
    Included in Spaceship Hyperlift Medium bundle.
    
    Use cases:
    - Portfolio company secure access
    - Client on-site data sync
    - Secure agent communication to external systems
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.fastvpn.spaceship.com/v1",
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("FASTVPN_API_KEY", "")
        self.base_url = base_url
        self.timeout = timeout
        self.enabled = os.getenv("FASTVPN_ENABLED", "true").lower() == "true"
        
        self._client: Optional[httpx.AsyncClient] = None
        self._tunnels: Dict[str, TunnelConfig] = {}
        self._connections: Dict[str, TunnelConnection] = {}
    
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
    async def create_tunnel(
        self,
        name: str,
        tunnel_type: TunnelType = TunnelType.SITE_TO_SITE,
        local_network: Optional[str] = None,
        remote_network: Optional[str] = None,
        allowed_ips: Optional[List[str]] = None,
        encryption: EncryptionLevel = EncryptionLevel.MILITARY,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TunnelConfig:
        """
        Create a new VPN tunnel.
        Returns configuration for connecting.
        """
        tunnel_id = str(uuid.uuid4())
        
        config = TunnelConfig(
            tunnel_id=tunnel_id,
            name=name,
            tunnel_type=tunnel_type,
            encryption=encryption,
            local_network=local_network,
            remote_network=remote_network,
            allowed_ips=allowed_ips or [],
            metadata=metadata or {},
        )
        
        if not self.enabled or not self.api_key:
            self._tunnels[tunnel_id] = config
            logger.info(f"Created local tunnel config: {tunnel_id}")
            return config
        
        client = await self._get_client()
        
        response = await client.post("/tunnels", json=config.to_dict())
        response.raise_for_status()
        
        data = response.json()
        config.tunnel_id = data.get("tunnel_id", tunnel_id)
        
        self._tunnels[config.tunnel_id] = config
        logger.info(f"Created VPN tunnel: {config.tunnel_id}")
        
        return config
    
    async def connect_tunnel(self, tunnel_id: str) -> TunnelConnection:
        """Establish connection to a tunnel."""
        if tunnel_id not in self._tunnels:
            raise ValueError(f"Tunnel {tunnel_id} not found")
        
        connection = TunnelConnection(
            tunnel_id=tunnel_id,
            status=TunnelStatus.CONNECTING,
        )
        
        if not self.enabled or not self.api_key:
            connection.status = TunnelStatus.CONNECTED
            connection.connected_at = datetime.utcnow().isoformat() + "Z"
            connection.local_ip = "10.0.0.2"
            connection.remote_ip = "10.0.0.1"
            self._connections[tunnel_id] = connection
            return connection
        
        client = await self._get_client()
        
        response = await client.post(f"/tunnels/{tunnel_id}/connect")
        response.raise_for_status()
        
        data = response.json()
        connection.status = TunnelStatus(data.get("status", "connected"))
        connection.connected_at = data.get("connected_at")
        connection.local_ip = data.get("local_ip")
        connection.remote_ip = data.get("remote_ip")
        
        self._connections[tunnel_id] = connection
        logger.info(f"Connected to tunnel: {tunnel_id}")
        
        return connection
    
    async def disconnect_tunnel(self, tunnel_id: str) -> None:
        """Disconnect from a tunnel."""
        if tunnel_id in self._connections:
            self._connections[tunnel_id].status = TunnelStatus.DISCONNECTED
        
        if not self.enabled or not self.api_key:
            return
        
        client = await self._get_client()
        await client.post(f"/tunnels/{tunnel_id}/disconnect")
        
        logger.info(f"Disconnected from tunnel: {tunnel_id}")
    
    async def get_tunnel_status(self, tunnel_id: str) -> TunnelConnection:
        """Get current tunnel connection status."""
        if tunnel_id in self._connections:
            return self._connections[tunnel_id]
        
        if not self.enabled or not self.api_key:
            return TunnelConnection(tunnel_id=tunnel_id, status=TunnelStatus.DISCONNECTED)
        
        client = await self._get_client()
        
        response = await client.get(f"/tunnels/{tunnel_id}/status")
        response.raise_for_status()
        
        data = response.json()
        return TunnelConnection(
            tunnel_id=tunnel_id,
            status=TunnelStatus(data.get("status", "disconnected")),
            connected_at=data.get("connected_at"),
            local_ip=data.get("local_ip"),
            remote_ip=data.get("remote_ip"),
            bytes_sent=data.get("bytes_sent", 0),
            bytes_received=data.get("bytes_received", 0),
            latency_ms=data.get("latency_ms"),
            last_handshake=data.get("last_handshake"),
        )
    
    async def generate_client_token(
        self,
        tunnel_id: str,
        client_id: str,
        expires_hours: int = 24,
    ) -> AccessToken:
        """
        Generate a client access token for VPN connection.
        Used for portfolio company or client access.
        """
        token_id = str(uuid.uuid4())
        expires_at = datetime.utcnow().isoformat() + "Z"
        
        if not self.enabled or not self.api_key:
            return AccessToken(
                token_id=token_id,
                tunnel_id=tunnel_id,
                client_id=client_id,
                expires_at=expires_at,
                config_data="[Interface]\nPrivateKey=xxx\nAddress=10.0.0.2/32\n",
            )
        
        client = await self._get_client()
        
        response = await client.post(f"/tunnels/{tunnel_id}/tokens", json={
            "client_id": client_id,
            "expires_hours": expires_hours,
        })
        response.raise_for_status()
        
        data = response.json()
        
        return AccessToken(
            token_id=data.get("token_id", token_id),
            tunnel_id=tunnel_id,
            client_id=client_id,
            expires_at=data.get("expires_at", expires_at),
            config_data=data.get("config_data", ""),
        )
    
    async def list_tunnels(self) -> List[TunnelConfig]:
        """List all configured tunnels."""
        if not self.enabled or not self.api_key:
            return list(self._tunnels.values())
        
        client = await self._get_client()
        
        response = await client.get("/tunnels")
        response.raise_for_status()
        
        tunnels = []
        for data in response.json().get("tunnels", []):
            tunnels.append(TunnelConfig(
                tunnel_id=data["tunnel_id"],
                name=data["name"],
                tunnel_type=TunnelType(data["type"]),
                encryption=EncryptionLevel(data.get("encryption", "chacha20-poly1305")),
                local_network=data.get("local_network"),
                remote_network=data.get("remote_network"),
                allowed_ips=data.get("allowed_ips", []),
                metadata=data.get("metadata", {}),
            ))
        
        return tunnels
    
    async def health_check(self) -> Dict[str, Any]:
        """Check FastVPN service health."""
        if not self.enabled:
            return {"status": "disabled"}
        
        if not self.api_key:
            return {"status": "unconfigured", "error": "FASTVPN_API_KEY not set"}
        
        try:
            client = await self._get_client()
            response = await client.get("/health")
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "active_tunnels": len(self._connections),
                }
            else:
                return {"status": "degraded", "code": response.status_code}
        
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


_fastvpn_instance: Optional[FastVPNClient] = None


async def get_fastvpn() -> FastVPNClient:
    """Get singleton FastVPN client."""
    global _fastvpn_instance
    if _fastvpn_instance is None:
        _fastvpn_instance = FastVPNClient()
    return _fastvpn_instance
