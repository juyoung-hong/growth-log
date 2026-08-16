"""OCI Object Storage 어댑터. ObjectStoragePort의 실제 구현체.

~/.oci/config(API Key 기반 인증)를 그대로 사용한다. namespace는 계정마다
고정값이라 최초 1회만 조회해서 캐시한다 — 매 요청마다 조회하면 낭비다.
"""

from __future__ import annotations

import oci

from application.ports.outbound.object_storage_port import ObjectStoragePort
from config.settings import settings


class OciObjectStorageAdapter(ObjectStoragePort):
    def __init__(self) -> None:
        config = oci.config.from_file(profile_name=settings.oci_config_profile)
        self._client = oci.object_storage.ObjectStorageClient(config)
        self._bucket_name = settings.oci_bucket_name
        self._namespace: str | None = None

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        self._client.put_object(
            namespace_name=self._get_namespace(),
            bucket_name=self._bucket_name,
            object_name=path,
            put_object_body=content,
            content_type=content_type,
        )

    def delete(self, path: str) -> None:
        try:
            self._client.delete_object(
                namespace_name=self._get_namespace(),
                bucket_name=self._bucket_name,
                object_name=path,
            )
        except oci.exceptions.ServiceError as e:
            if e.status != 404:
                raise

    def _get_namespace(self) -> str:
        if self._namespace is None:
            self._namespace = self._client.get_namespace().data
        return self._namespace


# 요청마다 새로 만들지 않고 앱 전체에서 하나만 쓴다 — session.py의 engine과 같은 이유.
object_storage_adapter = OciObjectStorageAdapter()
