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


class TaskGroupNotFoundError(Exception):
    def __init__(self, task_group_id: int):
        super().__init__(f"task_group {task_group_id} not found")
        self.task_group_id = task_group_id
