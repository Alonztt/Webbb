from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    original_filename: Mapped[str] = mapped_column(String(255))
    original_ext: Mapped[str] = mapped_column(String(8))
    content_type: Mapped[str] = mapped_column(String(64))

    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    size_bytes: Mapped[int] = mapped_column(Integer)

    thumb_ext: Mapped[str] = mapped_column(String(8), default="jpg")

    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)