"""OCI Database 어댑터. DatabaseUsagePort의 실제 구현체.

Autonomous Database의 실제 사용 중인 스토리지 크기를 OCI Database
API로 직접 조회한다. actual_used_data_storage_size_in_tbs는 콘솔의
"Storage Used"와 같은 값이다(0번 섹션 ① 참고) — 반올림 문제가 있는
used_data_storage_size_in_tbs 대신 이 필드를 쓴다.
"""

from __future__ import annotations

import oci

from application.ports.outbound.database_usage_port import DatabaseUsagePort
from config.settings import settings


class OciDatabaseUsageAdapter(DatabaseUsagePort):
    def __init__(self) -> None:
        config = oci.config.from_file(profile_name=settings.oci_config_profile)
        self._client = oci.database.DatabaseClient(config)

    def get_used_bytes(self) -> int:
        response = self._client.get_autonomous_database(
            autonomous_database_id=settings.oci_autonomous_database_id
        )
        used_tbs = response.data.actual_used_data_storage_size_in_tbs or 0
        return int(used_tbs * 1024**4)


database_usage_adapter = OciDatabaseUsageAdapter()
