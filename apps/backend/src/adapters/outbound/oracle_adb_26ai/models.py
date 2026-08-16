from ast import Index
from datetime import datetime, timezone

from sqlalchemy import CLOB, TIMESTAMP, Column, Identity, Index, Integer, String, text
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


class TaskGroupTable(SQLModel, table=True):
    __tablename__ = "task_group"
    __table_args__ = (Index("ix_task_group_category_status", "category", "status"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    category: str = Field(max_length=10)
    name: str = Field(max_length=200)
    description: str | None = Field(default=None, sa_column=Column(CLOB))
    status: str = Field(
        default="진행중",
        sa_column=Column(String(10), nullable=False, server_default=text("'진행중'")),
    )
    is_archived: str = Field(
        default="N",
        sa_column=Column(String(1), nullable=False, server_default=text("'N'")),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("SYSTIMESTAMP")
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("SYSTIMESTAMP")
        ),
    )
