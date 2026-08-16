"""여러 도메인 엔티티가 공유하는 예외."""


class InvalidFieldError(Exception):
    """필드 값이 형식·규칙을 위반했을 때 발생하는 예외들의 공통 부모.

    API 계층에서 "형식 검증 실패는 전부 400으로" 처리하고 싶다면
    이 부모 클래스 하나만 잡아도 되고, 원인별로 다르게 처리하고
    싶으면 아래 구체 클래스를 각각 잡으면 된다.
    """

    def __init__(self, field: str, message: str):
        super().__init__(f"{field}: {message}")
        self.field = field


class EmptyFieldError(InvalidFieldError):
    """필드가 비어있을 때 발생."""

    def __init__(self, field: str):
        super().__init__(field, "비어있을 수 없습니다.")


class InvalidEmailError(InvalidFieldError):
    """이메일 형식이 올바르지 않을 때 발생."""

    def __init__(self, value: str, field: str = "email"):
        super().__init__(field, f"이메일 형식이 올바르지 않습니다: {value}")
        self.value = value


class InvalidPhoneError(InvalidFieldError):
    """전화번호 형식이 올바르지 않을 때 발생(하이픈 누락 등)."""

    def __init__(self, value: str, field: str = "phone"):
        super().__init__(
            field, f"전화번호는 하이픈을 포함해야 합니다(예: 010-1234-5678): {value}"
        )
        self.value = value
