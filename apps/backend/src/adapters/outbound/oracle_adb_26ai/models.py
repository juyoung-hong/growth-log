from ast import Index
from datetime import date, datetime, timezone

from sqlalchemy import (
    CLOB,
    TIMESTAMP,
    Column,
    Date,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    text,
)
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


class TaskGroupAttachmentTable(SQLModel, table=True):
    __tablename__ = "task_group_attachment"
    __table_args__ = (Index("ix_task_group_attachment_task_group", "task_group_id"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    task_group_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("task_group.id", name="fk_task_group_attachment_task_group"),
            nullable=False,
        )
    )
    type: str = Field(max_length=10)
    title: str = Field(max_length=300)
    object_storage_path: str | None = Field(default=None, max_length=500)
    external_url: str | None = Field(default=None, max_length=1000)
    file_size_bytes: int | None = Field(default=None)
    mime_type: str | None = Field(default=None, max_length=100)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("SYSTIMESTAMP")
        ),
    )


class TaskTable(SQLModel, table=True):
    __tablename__ = "task"
    __table_args__ = (
        Index("ix_task_task_group", "task_group_id"),
        Index("ix_task_status", "status"),
        Index("ix_task_dates", "start_date", "due_date"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    task_group_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("task_group.id", name="fk_task_task_group"),
            nullable=False,
        )
    )
    name: str = Field(max_length=300)
    status: str = Field(
        default="보류",
        sa_column=Column(String(10), nullable=False, server_default=text("'보류'")),
    )
    estimated_days: int | None = Field(default=None)
    start_date: date | None = Field(default=None)
    due_date: date | None = Field(default=None)
    completed_at: datetime | None = Field(default=None, sa_column=Column(TIMESTAMP))
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


class TaskActivityLogTable(SQLModel, table=True):
    __tablename__ = "task_activity_log"
    __table_args__ = (Index("ix_task_activity_log_task_time", "task_id", "event_at"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    task_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("task.id", name="fk_task_activity_log_task"),
            nullable=False,
        )
    )
    event_type: str = Field(max_length=10)
    event_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=text("SYSTIMESTAMP")
        ),
    )
    old_value: str | None = Field(default=None, max_length=400)
    new_value: str | None = Field(default=None, max_length=400)
    reason: str | None = Field(default=None, max_length=500)


class TaskCommentTable(SQLModel, table=True):
    __tablename__ = "task_comment"
    __table_args__ = (Index("ix_task_comment_task_time", "task_id", "created_at"),)

    id: int | None = Field(
        default=None,
        sa_column=Column(Integer, Identity(always=True), primary_key=True),
    )
    task_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("task.id", name="fk_task_comment_task"),
            nullable=False,
        )
    )
    content: str = Field(sa_column=Column(CLOB, nullable=False))
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
