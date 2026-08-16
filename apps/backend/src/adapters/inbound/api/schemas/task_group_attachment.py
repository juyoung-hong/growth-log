from pydantic import BaseModel

from domain.task_group_attachment import AttachmentType


class TaskGroupAttachmentRead(BaseModel):
    id: int
    task_group_id: int
    type: AttachmentType
    title: str
    object_storage_path: str | None
    external_url: str | None
    file_size_bytes: int | None
    mime_type: str | None
