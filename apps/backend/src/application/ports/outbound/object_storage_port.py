"""Object Storage 포트.

애플리케이션이 실제 스토리지가 OCI인지, 테스트용 인메모리인지
알 필요 없게 감싸는 인터페이스.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ObjectStoragePort(ABC):
    """참고자료 원본 파일을 저장하는 곳이 반드시 구현해야 하는 메서드."""

    @abstractmethod
    def upload(self, path: str, content: bytes, content_type: str) -> None:
        """path 위치에 content를 업로드한다."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, path: str) -> None:
        """path의 객체를 삭제한다. 이미 없어도 예외를 던지지 않는다."""
        raise NotImplementedError
