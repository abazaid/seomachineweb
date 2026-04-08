from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Report(Base):
    __tablename__ = 'reports'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='queued', index=True)
    days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    markdown_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
