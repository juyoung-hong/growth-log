from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.deps import get_person_service
from adapters.inbound.api.schemas.person import PersonCreate, PersonRead, PersonUpdate
from application.services.person_service import PersonService
from domain.common.enums import Scope
from domain.common.exceptions import InvalidFieldError
from domain.exceptions import (
    EmailAlreadyExistsError,
    PersonNotFoundError,
    PersonReferencedError,
)

router = APIRouter(prefix="/persons", tags=["persons"])


@router.get("", response_model=list[PersonRead])
def list_persons(
    category: Scope | None = None,
    service: PersonService = Depends(get_person_service),
):
    return service.list(category)


@router.post("", response_model=PersonRead, status_code=201)
def create_person(
    body: PersonCreate, service: PersonService = Depends(get_person_service)
):
    try:
        return service.create(**body.model_dump())
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, service: PersonService = Depends(get_person_service)):
    try:
        return service.get(person_id)
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")


@router.patch("/{person_id}", response_model=PersonRead)
def update_person(
    person_id: int,
    body: PersonUpdate,
    service: PersonService = Depends(get_person_service),
):
    try:
        return service.update(person_id, **body.model_dump(exclude_unset=True))
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")
    except EmailAlreadyExistsError:
        raise HTTPException(status_code=409, detail="이미 등록된 이메일입니다.")
    except InvalidFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, service: PersonService = Depends(get_person_service)):
    try:
        service.delete(person_id)
    except PersonNotFoundError:
        raise HTTPException(status_code=404, detail="인물을 찾을 수 없습니다.")
    except PersonReferencedError:
        raise HTTPException(
            status_code=409, detail="다른 데이터에서 참조 중이라 삭제할 수 없습니다."
        )
