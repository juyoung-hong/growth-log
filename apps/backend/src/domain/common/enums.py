"""여러 도메인 엔티티가 공유하는 값 목록(Enum).

한 엔티티에만 쓰이는 Enum은 그 도메인 파일에 그대로 두고,
Person·Level2처럼 둘 이상의 엔티티가 같은 값 목록을 쓸 때만 여기로 옮긴다.
"""

from __future__ import annotations

from enum import Enum


class Scope(str, Enum):
    """개인 소유인지 회사 소속인지 구분하는 레벨1 분류.

    Person.category, (앞으로 생길) Level2.category가 공유한다.
    두 엔티티가 각자 같은 값을 따로 정의하면 나중에 하나만 바뀌었을 때
    불일치가 생길 수 있어서 여기 하나로 모아둔다.
    """

    COMPANY = "회사"
    PERSONAL = "개인"


class TaskStatus(str, Enum):
    """레벨2·레벨3이 공유하는 진행 상태.

    레벨2 기본값은 '진행중', 레벨3 기본값은 '보류'로 서로 다르다 —
    값 목록 자체는 같아서 여기 하나로 모아둔다.
    """

    PENDING = "보류"
    IN_PROGRESS = "진행중"
    DONE = "완료"
