from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Audit(Base):
    """Bitácora local. El actor es declarado; no equivale a autenticación."""
    __tablename__ = 'audit'
    id = Column(Integer, primary_key=True)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    device_id = Column(Integer)
    proposal = Column(Text, default='')
    approval = Column(String(100), default='NO APLICA - SIMULACION')
    result = Column(Text, nullable=False)
    evidence_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
