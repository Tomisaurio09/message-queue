"""
Task
- id (uuid)
- status
- task_name
- payload
- result
- error_message
- created_at
- updated_at
"""
import sqlalchemy as sa
import sqlalchemy.orm as so
from enum import Enum
from typing import Any, Optional
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SqlEnum
from datetime import datetime, timezone
from src.app.core.db import Base
from pydantic import BaseModel
import uuid 


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

class TaskSchema(BaseModel):
    id: uuid.UUID
    status: TaskStatus
    task_name: str
    payload: dict
    result: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class Task(Base):
    __tablename__ = "tasks"

    id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    status: so.Mapped[TaskStatus] = so.mapped_column(SqlEnum(TaskStatus), default=TaskStatus.PENDING,index=True)
    task_name: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    payload: so.Mapped[dict] = so.mapped_column(sa.JSON)
    result: so.Mapped[Optional[Any]] = so.mapped_column(sa.JSON, nullable=True)
    error_message: so.Mapped[Optional[str]] = so.mapped_column(sa.String(512), nullable=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
