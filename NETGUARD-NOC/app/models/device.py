from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    ip_address = Column(String, unique=True, nullable=False)

    brand = Column(String, nullable=False)

    model = Column(String, nullable=True)

    version = Column(String, nullable=True)

    location = Column(String, nullable=True)

    status = Column(
        String,
        nullable=False,
        default="OFFLINE"
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )