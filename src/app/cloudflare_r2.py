import uuid
from dataclasses import dataclass
from typing import Any

import aioboto3


@dataclass(frozen=True, slots=True)
class R2Config:
    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket_name: str

    @property
    def endpoint_url(self) -> str:
        return f"https://{self.account_id}.r2.cloudflarestorage.com"


class CloudflareR2Service:
    def __init__(self, cfg: R2Config):
        self._cfg = cfg
        self._session = aioboto3.session.Session()
        self._client = None

    async def _get_client(self):
        if self._client is None:
            async with self._session.client(
                    "s3",
                    endpoint_url=self._cfg.endpoint_url,
                    aws_access_key_id=self._cfg.access_key_id,
                    aws_secret_access_key=self._cfg.secret_access_key,
                    region_name="auto"
            ) as client:
                self._client = client
        return self._client

    @staticmethod
    def build_key(media_name: str, media_type: str, prefix: str = "") -> str:
        media_name = media_name.strip().lstrip("/")
        media_type = media_type.strip().lstrip(".")
        key = f"{media_name}-{uuid.uuid4()}.{media_type}" if media_type else media_name
        return f"{prefix.strip().strip('/')}/{key}".lstrip("/") if prefix else key

    async def upload_bytes(
            self,
            *,
            key: str,
            body: bytes,
            content_type: str,
    ) -> str:
        client = await self._get_client()
        kwargs: dict[str, Any] = {
            "Bucket": self._cfg.bucket_name,
            "Key": key,
            "Body": body,
            "ContentType": content_type,
        }
        await client.put_object(**kwargs)
        return f"https://pub-6e27f01380fe441daf5372813946fbcd.r2.dev/{key}"

    async def delete_file(self, *, key: str) -> None:
        client = await self._get_client()
        await client.delete_object(Bucket=self._cfg.bucket_name, Key=key)
