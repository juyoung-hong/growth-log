from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, Column, Identity, Integer
from sqlmodel import Field, SQLModel


class PersonTable(SQLModel, table=True):
    __tablename__ = "person"

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    category: str = Field(max_length=10)
    name: str = Field(max_length=100)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    affiliation: str | None = Field(default=None, max_length=200)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP, nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP, nullable=False),
    )
