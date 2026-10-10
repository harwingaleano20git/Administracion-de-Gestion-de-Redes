"""Indicios de amenazas y evidencia del resultado de notificaciones."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base

class Threat(Base):
    __tablename__ = 'threats'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('syslog_messages.id'), nullable=False)
    rule = Column(String(80), nullable=False)
    description = Column(String(500), nullable=False)
    detected_at = Column(DateTime, nullable=False)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('syslog_messages.id'), unique=True, nullable=False)
    status = Column(String(30), nullable=False, default='PENDIENTE')
    detail = Column(String(200), default='')
    created_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime)
    telegram_message_id = Column(Integer)
