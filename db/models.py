from enum import Enum
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, JSON


class Status(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Priority(str, Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Task(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    plan_uuid: str = Field(index=True)
    idx: int
    title: str
    status: Status = Field(default=Status.PENDING)
    priority: Priority | None = Field(default=None)
    allocated_minutes: int | None = Field(default=None)
    pomodoro_count: int = Field(default=0)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)


class Plan(SQLModel, table=True):
    uuid: str = Field(primary_key=True)
    title: str
    tasks: list[str] | None = Field(default=None, sa_column=Column(JSON))
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)


class CommandHistory(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    command: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
