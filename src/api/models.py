from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="client")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    documents: Mapped[list["DriverDocument"]] = relationship(
        back_populates="user", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active
        }


class Driver(db.Model):
    __tablename__ = 'driver'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    vehicle: Mapped[str] = mapped_column(String(100), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True)

    rides: Mapped[list["Ride"]] = relationship(
        'Ride', back_populates="driver", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "vehicle": self.vehicle,
            "available": self.available,
        }


class Ride(db.Model):
    __tablename__ = 'ride'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    origin: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("driver.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    driver: Mapped["Driver"] = relationship('Driver', back_populates="rides")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "origin": self.origin,
            "destination": self.destination,
            "status": self.status,
            "driver_id": self.driver_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Transaction(db.Model):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class Extra(db.Model):
    __tablename__ = 'extra'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }


class DriverDocument(db.Model):
    __tablename__ = 'driver_documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="documents")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
