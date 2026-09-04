"""API 응답의 datetime 필드를 KST 문자열로 바꾸는 공용 헬퍼.

Oracle TIMESTAMP 컬럼은 시간대 정보 없이 저장되므로, ORM이 읽어오는 값은
항상 naive datetime이다. 쓸 때 항상 UTC로 저장했으므로(datetime.now
(timezone.utc), 또는 서버 기본값 SYSTIMESTAMP가 UTC로 설정된 DB) 그 값이
UTC라는 걸 여기서 명시적으로 라벨 붙인 뒤 KST로 변환한다 — 이 replace가
없으면 파이썬이 naive datetime을 시스템 로컬 시간대로 잘못 해석해서
변환이 틀어진다(meeting.py의 scheduled_at에서 처음 정리한 것과 같은 문제).
"""

from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def to_kst_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(KST).isoformat()
