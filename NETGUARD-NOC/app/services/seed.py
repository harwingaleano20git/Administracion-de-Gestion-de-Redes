from app.database import SessionLocal
from app.models.device import Device


def create_initial_devices():
    db = SessionLocal()

    try:
        if db.query(Device).count() > 0:
            return

        devices = [
            Device(
                name="Router-Core-01",
                ip_address="10.10.0.1",
                brand="Cisco",
                model="ISR4321",
                version="17.9",
                location="Centro de datos",
                status="ONLINE"
            ),
            Device(
                name="Firewall-FGT-01",
                ip_address="10.10.0.2",
                brand="Fortinet",
                model="FortiGate 60F",
                version="7.4",
                location="Centro de datos",
                status="ONLINE"
            ),
            Device(
                name="Switch-Core-01",
                ip_address="10.10.0.3",
                brand="Huawei",
                model="S5735",
                version="V200R022",
                location="Centro de datos",
                status="ONLINE"
            ),
            Device(
                name="Router-Sucursal",
                ip_address="10.20.0.1",
                brand="Cisco",
                model="ISR4331",
                version="17.6",
                location="Sucursal",
                status="OFFLINE"
            )
        ]

        db.add_all(devices)
        db.commit()

    finally:
        db.close()