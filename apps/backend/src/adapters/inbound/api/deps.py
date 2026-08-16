from typing import Iterator

from fastapi import Depends
from sqlmodel import Session

from adapters.outbound.oracle_adb_26ai.person_repository import SqlPersonRepository
from adapters.outbound.oracle_adb_26ai.session import engine
from application.services.person_service import PersonService


def get_db_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def get_person_service(session: Session = Depends(get_db_session)) -> PersonService:
    return PersonService(SqlPersonRepository(session))
