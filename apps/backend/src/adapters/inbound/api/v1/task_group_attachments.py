from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from adapters.inbound.api.deps import get_attachment_service
from adapters.inbound.api.schemas.task_group_attachment import TaskGroupAttachmentRead
from application.services.attachment_service import AttachmentService
from domain.exceptions import (
    FileTooLargeError,
    TaskGroupAttachmentNotFoundError,
    TaskGroupNotFoundError,
)
from domain.task_group_attachment import AttachmentType

router = APIRouter(tags=["task-group-attachments"])


@router.get(
    "/task-groups/{task_group_id}/attachments",
    response_model=list[TaskGroupAttachmentRead],
)
def list_attachments(
    task_group_id: int, service: AttachmentService = Depends(get_attachment_service)
):
    try:
        return service.list(task_group_id)
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")


@router.post(
    "/task-groups/{task_group_id}/attachments",
    response_model=TaskGroupAttachmentRead,
    status_code=201,
)
async def create_attachment(
    task_group_id: int,
    type: AttachmentType = Form(...),
    title: str = Form(...),
    external_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    service: AttachmentService = Depends(get_attachment_service),
):
    try:
        if type == AttachmentType.FILE:
            if file is None:
                raise HTTPException(
                    status_code=400, detail="파일 타입은 file이 필요합니다."
                )
            content = await file.read()
            return service.create_file_attachment(
                task_group_id=task_group_id,
                title=title,
                content=content,
                mime_type=file.content_type or "application/octet-stream",
            )
        if not external_url:
            raise HTTPException(
                status_code=400, detail="URL 타입은 external_url이 필요합니다."
            )
        return service.create_url_attachment(
            task_group_id=task_group_id, title=title, external_url=external_url
        )
    except TaskGroupNotFoundError:
        raise HTTPException(status_code=404, detail="TaskGroup을 찾을 수 없습니다.")
    except FileTooLargeError:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 상한을 초과했습니다.",
        )


@router.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(
    attachment_id: int, service: AttachmentService = Depends(get_attachment_service)
):
    try:
        service.delete(attachment_id)
    except TaskGroupAttachmentNotFoundError:
        raise HTTPException(status_code=404, detail="참고자료를 찾을 수 없습니다.")
