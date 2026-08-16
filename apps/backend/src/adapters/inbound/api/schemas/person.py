from pydantic import BaseModel

from domain.common.enums import Scope


class PersonCreate(BaseModel):
    category: Scope
    name: str
    email: str | None = None
    phone: str | None = None
    affiliation: str | None = None


class PersonUpdate(BaseModel):
    category: Scope | None = None
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    affiliation: str | None = None


class PersonRead(BaseModel):
    id: int
    category: Scope
    name: str
    email: str | None
    phone: str | None
    affiliation: str | None
