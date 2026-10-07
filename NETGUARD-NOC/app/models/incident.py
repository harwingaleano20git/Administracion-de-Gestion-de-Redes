from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database import Base

class Incident(Base):
    """Un incidente tiene responsable, seguimiento y cierre explícito."""
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('syslog_messages.id'), nullable=False, unique=True)
    title = Column(String(160), nullable=False)
    responsible = Column(String(100), nullable=False)
    status = Column(String(30), default='ABIERTO', nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime)
    cause = Column(Text, default='')
    resolution = Column(Text, default='')
    sla_minutes = Column(Integer, default=60)

class IncidentNote(Base):
    __tablename__ = 'incident_notes'
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey('incidents.id'), nullable=False)
    actor = Column(String(100), nullable=False)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
