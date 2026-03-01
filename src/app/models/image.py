# models/image.py
import sqlalchemy as sa
import sqlalchemy.orm as so
from enum import Enum
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SqlEnum
from datetime import datetime,timezone
from src.app.core.db import Base
from pydantic import BaseModel
import uuid

class ImageStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"

class Image(Base):
    __tablename__ = "images"

    id: so.Mapped[uuid.UUID] = so.mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    filename: so.Mapped[str] = so.mapped_column(nullable=False)
    path: so.Mapped[str] = so.mapped_column(nullable=False)
    processed_path: so.Mapped[str] = so.mapped_column(nullable=True)
    status: so.Mapped[ImageStatus] = so.mapped_column(SqlEnum(ImageStatus), default=ImageStatus.PENDING,index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ImageCreateSchema(BaseModel):
    filename: str

class ImageResponseSchema(BaseModel):
    id: uuid.UUID
    filename: str
    path: str
    processed_path: Optional[str] = None
    status: ImageStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
