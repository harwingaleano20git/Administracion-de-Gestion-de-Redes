from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class SyslogMessage(Base):
    __tablename__ = "syslog_messages"

    id = Column(Integer, primary_key=True, index=True)

    received_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    source_ip = Column(String(45), nullable=False)
    severity = Column(Integer, nullable=True)
    facility = Column(Integer, nullable=True)
    device_id = Column(Integer, nullable=True, index=True)
    brand = Column(String(80), nullable=True)
    event_at = Column(DateTime, nullable=True)
    simulated = Column(Integer, default=1, nullable=False)
    message = Column(Text, nullable=False)
