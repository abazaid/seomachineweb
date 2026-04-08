from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ContentItem(Base):
    __tablename__ = 'content_items'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='research')
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    latest_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ContentVersion(Base):
    __tablename__ = 'content_versions'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_item_id: Mapped[int] = mapped_column(index=True, nullable=False)
    version_number: Mapped[int] = mapped_column(nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
