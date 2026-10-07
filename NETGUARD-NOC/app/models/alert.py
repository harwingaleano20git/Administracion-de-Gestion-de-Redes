from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    syslog_message_id = Column(
        Integer,
        ForeignKey("syslog_messages.id"),
        unique=True,
        nullable=False
    )

    status = Column(
        String,
        default="PENDIENTE",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    reviewed_at = Column(DateTime, nullable=True)