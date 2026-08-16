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


class FileTooLargeError(Exception):
    def __init__(self, size_bytes: int):
        super().__init__(f"file too large: {size_bytes} bytes")
        self.size_bytes = size_bytes


class TaskGroupAttachmentNotFoundError(Exception):
    def __init__(self, attachment_id: int):
        super().__init__(f"task_group_attachment {attachment_id} not found")
        self.attachment_id = attachment_id
