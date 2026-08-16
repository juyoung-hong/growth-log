class PersonNotFoundError(Exception):
    def __init__(self, person_id: int):
        super().__init__(f"person {person_id} not found")
        self.person_id = person_id


class EmailAlreadyExistsError(Exception):
    def __init__(self, email: str):
        super().__init__(f"email already exists: {email}")
        self.email = email


class PersonReferencedError(Exception):
    def __init__(self, person_id: int):
        super().__init__(f"person {person_id} is referenced")
        self.person_id = person_id
