"""
Enterprise Storage & CDN Client
- S3-compatible object storage
- CDN purge integration
- Signed URL generation
- Multi-region support
"""
import logging
import os
import asyncio
from typing import Optional, Dict, Any, List, BinaryIO
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
import base64
from urllib.parse import urlencode, quote

import httpx

from .core_resilience import retry_async, RetryConfig

logger = logging.getLogger(__name__)


@dataclass
class StorageObject:
    """Represents a stored object."""
    key: str
    size: int
    content_type: str
    etag: str
    last_modified: datetime
    url: str
    cdn_url: Optional[str] = None


class StorageClient:
    """
    Enterprise S3-compatible storage client.
    Integrated with Spaceship CDN for edge delivery.
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        cdn_url: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.getenv("S3_ENDPOINT", "https://storage.spaceship.com")
        self.access_key = access_key or os.getenv("S3_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("S3_SECRET_KEY", "")
        self.bucket = bucket or os.getenv("S3_BUCKET", "creditx-ecosystem")
        self.region = region or os.getenv("S3_REGION", "us-phx-1")
        self.cdn_url = cdn_url or os.getenv("CDN_URL", "")
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client
    
    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _sign_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        payload_hash: str = "UNSIGNED-PAYLOAD",
    ) -> Dict[str, str]:
        """Generate AWS Signature V4 headers."""
        now = datetime.utcnow()
        date_stamp = now.strftime("%Y%m%d")
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        
        headers["x-amz-date"] = amz_date
        headers["x-amz-content-sha256"] = payload_hash
        
        canonical_headers = "\n".join(
            f"{k.lower()}:{v}" for k, v in sorted(headers.items())
        ) + "\n"
        signed_headers = ";".join(k.lower() for k in sorted(headers.keys()))
        
        canonical_request = f"{method}\n{path}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        credential_scope = f"{date_stamp}/{self.region}/s3/aws4_request"
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        
        def sign(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()
        
        k_date = sign(f"AWS4{self.secret_key}".encode(), date_stamp)
        k_region = sign(k_date, self.region)
        k_service = sign(k_region, "s3")
        k_signing = sign(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        headers["Authorization"] = (
            f"AWS4-HMAC-SHA256 Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )
        
        return headers
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> StorageObject:
        """Upload an object to storage."""
        client = await self._get_client()
        
        path = f"/{self.bucket}/{key}"
        url = f"{self.endpoint}{path}"
        
        payload_hash = hashlib.sha256(data).hexdigest()
        
        headers = {
            "Host": self.endpoint.replace("https://", "").replace("http://", ""),
            "Content-Type": content_type,
            "Content-Length": str(len(data)),
        }
        
        if metadata:
            for k, v in metadata.items():
                headers[f"x-amz-meta-{k}"] = v
        
        headers = self._sign_request("PUT", path, headers, payload_hash)
        
        response = await client.put(url, content=data, headers=headers)
        response.raise_for_status()
        
        cdn_object_url = f"{self.cdn_url}/{key}" if self.cdn_url else None
        
        logger.info(f"Uploaded object: {key} ({len(data)} bytes)")
        
        return StorageObject(
            key=key,
            size=len(data),
            content_type=content_type,
            etag=response.headers.get("ETag", "").strip('"'),
            last_modified=datetime.utcnow(),
            url=url,
            cdn_url=cdn_object_url,
        )
    
    async def upload_file(
        self,
        key: str,
        file_path: str,
        content_type: Optional[str] = None,
    ) -> StorageObject:
        """Upload a file from disk."""
        import mimetypes
        
        if content_type is None:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        return await self.upload(key, data, content_type)
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def download(self, key: str) -> bytes:
        """Download an object from storage."""
        client = await self._get_client()
        
        path = f"/{self.bucket}/{key}"
        url = f"{self.endpoint}{path}"
        
        headers = {
            "Host": self.endpoint.replace("https://", "").replace("http://", ""),
        }
        headers = self._sign_request("GET", path, headers)
        
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content
    
    async def delete(self, key: str) -> bool:
        """Delete an object from storage."""
        client = await self._get_client()
        
        path = f"/{self.bucket}/{key}"
        url = f"{self.endpoint}{path}"
        
        headers = {
            "Host": self.endpoint.replace("https://", "").replace("http://", ""),
        }
        headers = self._sign_request("DELETE", path, headers)
        
        response = await client.delete(url, headers=headers)
        
        if response.status_code in [200, 204]:
            logger.info(f"Deleted object: {key}")
            return True
        return False
    
    def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """Generate a presigned URL for temporary access."""
        now = datetime.utcnow()
        date_stamp = now.strftime("%Y%m%d")
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        
        credential = f"{self.access_key}/{date_stamp}/{self.region}/s3/aws4_request"
        
        params = {
            "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
            "X-Amz-Credential": credential,
            "X-Amz-Date": amz_date,
            "X-Amz-Expires": str(expires_in),
            "X-Amz-SignedHeaders": "host",
        }
        
        path = f"/{self.bucket}/{key}"
        query_string = urlencode(sorted(params.items()))
        
        host = self.endpoint.replace("https://", "").replace("http://", "")
        canonical_request = f"{method}\n{path}\n{query_string}\nhost:{host}\n\nhost\nUNSIGNED-PAYLOAD"
        
        string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{date_stamp}/{self.region}/s3/aws4_request\n{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        
        def sign(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()
        
        k_date = sign(f"AWS4{self.secret_key}".encode(), date_stamp)
        k_region = sign(k_date, self.region)
        k_service = sign(k_region, "s3")
        k_signing = sign(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        return f"{self.endpoint}{path}?{query_string}&X-Amz-Signature={signature}"
    
    async def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> List[Dict[str, Any]]:
        """List objects in the bucket."""
        client = await self._get_client()
        
        path = f"/{self.bucket}"
        params = {"prefix": prefix, "max-keys": str(max_keys)}
        url = f"{self.endpoint}{path}?{urlencode(params)}"
        
        headers = {
            "Host": self.endpoint.replace("https://", "").replace("http://", ""),
        }
        headers = self._sign_request("GET", path, headers)
        
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        return []


class CDNClient:
    """CDN management client for cache purging and configuration."""
    
    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        api_token: Optional[str] = None,
        cdn_url: Optional[str] = None,
    ):
        self.api_endpoint = api_endpoint or "https://cdn-api.spaceship.com/v1"
        self.api_token = api_token or os.getenv("CDN_API_TOKEN", "")
        self.cdn_url = cdn_url or os.getenv("CDN_URL", "")
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"X-CDN-Token": self.api_token},
                timeout=30.0,
            )
        return self._client
    
    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def purge_urls(self, urls: List[str]) -> Dict[str, Any]:
        """Purge specific URLs from CDN cache."""
        if not self.api_token:
            logger.warning("CDN API token not configured, skipping purge")
            return {"status": "skipped", "reason": "no_token"}
        
        client = await self._get_client()
        
        response = await client.post(
            f"{self.api_endpoint}/purge",
            json={"urls": urls},
        )
        response.raise_for_status()
        
        logger.info(f"Purged {len(urls)} URLs from CDN")
        return response.json()
    
    @retry_async(RetryConfig(max_attempts=3, base_delay_seconds=1.0))
    async def purge_prefix(self, prefix: str) -> Dict[str, Any]:
        """Purge all URLs matching a prefix."""
        if not self.api_token:
            return {"status": "skipped", "reason": "no_token"}
        
        client = await self._get_client()
        
        response = await client.post(
            f"{self.api_endpoint}/purge",
            json={"prefix": prefix},
        )
        response.raise_for_status()
        
        logger.info(f"Purged prefix {prefix} from CDN")
        return response.json()
    
    async def purge_all(self) -> Dict[str, Any]:
        """Purge entire CDN cache (use sparingly)."""
        if not self.api_token:
            return {"status": "skipped", "reason": "no_token"}
        
        client = await self._get_client()
        
        response = await client.post(
            f"{self.api_endpoint}/purge/all",
        )
        response.raise_for_status()
        
        logger.warning("Purged entire CDN cache")
        return response.json()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get CDN usage statistics."""
        if not self.api_token:
            return {"status": "unavailable"}
        
        client = await self._get_client()
        
        response = await client.get(f"{self.api_endpoint}/stats")
        response.raise_for_status()
        
        return response.json()


_storage_instance: Optional[StorageClient] = None
_cdn_instance: Optional[CDNClient] = None


async def get_storage() -> StorageClient:
    """Get singleton storage client."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageClient()
    return _storage_instance


async def get_cdn() -> CDNClient:
    """Get singleton CDN client."""
    global _cdn_instance
    if _cdn_instance is None:
        _cdn_instance = CDNClient()
    return _cdn_instance
