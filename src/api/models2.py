from datetime import datetime
from typing import ClassVar, List, Optional

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin
from sqlalchemy import (
    String, Boolean, ForeignKey, Float, DateTime, Enum, JSON, Table, event, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import os
import hashlib
from mailchimp3 import MailChimp

# Inicialización
db = SQLAlchemy()

# =========================================================
# RELACIONES DE TABLAS INTERMEDIAS
# =========================================================
roles_users = Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

ride_extras_pivot = Table(
    'ride_extras_pivot',
    db.Column('ride_id', db.Integer, db.ForeignKey('rides.id')),
    db.Column('extra_id', db.Integer, db.ForeignKey('ride_extras.id'))
)

roles_permissions = Table(
    "roles_permissions",
    db.metadata,
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id")),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"))
)

# =========================================================
# MODELOS DE USUARIO Y AUTENTICACIÓN
# =========================================================


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False)  # client, driver, admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    marketing_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    profile_photo_path: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True)

    # Columna para discriminador de polimorfismo
    type: Mapped[str] = mapped_column(String(50))

    # Relaciones comunes
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey('vehicles.id'), nullable=True, unique=True)
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=roles_users, back_populates="users")
    documents: Mapped[List["DriverDocument"]] = relationship(
        "DriverDocument", back_populates="user")
    # rides_as_driver: Mapped[List["Ride"]] = relationship("Ride", foreign_keys="Ride.driver_id", back_populates="driver")
    # rides_as_customer: Mapped[List["Ride"]] = relationship("Ride", foreign_keys="Ride.customer_id", back_populates="customer")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def is_driver(self) -> bool:
        return self.role == "driver"

    def is_client(self) -> bool:
        return self.role == "client"

    def is_admin(self) -> bool:
        return self.role == "admin"

    def serialize(self) -> dict:
        base = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "marketing_allowed": self.marketing_allowed,
            "profile_photo_path": self.profile_photo_path,
            "type": self.type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

        # Agrega info específica según tipo polimórfico
        if isinstance(self, Driver):
            base["documents"] = [doc.serialize() for doc in self.documents]
            base["vehicle"] = self.vehicle.serialize() if self.vehicle else None

        return base

    def _subscriber_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    @staticmethod
    def t(query: str) -> str:
        translations = {
            "user": "cliente",
            "users": "clientes"
        }
        return translations.get(query.lower(), query)

    @staticmethod
    def after_save_hook(mapper, connection, target):
        if not current_app.config.get("ENV") == "development" and target.email:
            print("📨 Ejecutando sincronización con Mailchimp...")
            try:
                client = MailChimp(
                    mc_api=os.environ['MAILCHIMP_API_KEY'],
                    mc_user=os.environ['MAILCHIMP_USERNAME']
                )
                list_id = os.environ['MAILCHIMP_LIST_ID']

                if target.marketing_allowed:
                    client.lists.members.create_or_update(
                        list_id,
                        target._subscriber_hash(),
                        {
                            'email_address': target.email,
                            'status_if_new': 'subscribed',
                            'status': 'subscribed',
                            'merge_fields': {'FNAME': target.name}
                        }
                    )
                else:
                    client.lists.members.update(
                        list_id,
                        target._subscriber_hash(),
                        {'status': 'unsubscribed'}
                    )
            except Exception as e:
                print(f"[Mailchimp Sync Error] {e}")


# Registrar los hooks
event.listen(User, 'after_insert', User.after_save_hook)
event.listen(User, 'after_update', User.after_save_hook)


# Subclase Admin
class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    # Métodos específicos de admin
    def can_manage_reservations(self) -> bool:
        return True

    def can_edit_content(self) -> bool:
        return True


# Subclase Driver
class Driver(User):
    __mapper_args__ = {
        'polymorphic_identity': 'driver',
    }

    # Relación 1:1 con Vehicle
    vehicle: Mapped[Optional["Vehicle"]] = relationship(
        "Vehicle", back_populates="driver", uselist=False)

    def get_assigned_vehicle(self):
        return self.vehicle

    # Métodos específicos para conductor
    def can_view_assigned_trips(self) -> bool:
        return True


# Subclase Customer
class Customer(User):
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    # Métodos específicos para cliente
    def can_make_reservations(self) -> bool:
        return True

    def serialize(self):
        base = super().serialize()
        base["marketing_allowed"] = self.marketing_allowed
        return base


# =========================================================
# MODELOS DE VIAJE
# =========================================================

class RideStatus(db.Model):
    __tablename__ = 'ride_statuses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hex: Mapped[str] = mapped_column(String(7), nullable=False)

    rides: Mapped[List["Ride"]] = relationship("Ride", back_populates="status")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "hex": self.hex
        }


class RideExtra(db.Model):
    __tablename__ = 'ride_extras'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }


class Ride(db.Model):
    __tablename__ = 'rides'

    STATUS_ACTIVE = 'active'
    STATUS_DONE = 'done'
    STATUS_CANCELED = 'canceled'
    STATUS_CREATED = 'created'

    id: Mapped[int] = mapped_column(primary_key=True)
    pickup: Mapped[dict] = mapped_column(JSON, nullable=True)
    destination: Mapped[dict] = mapped_column(JSON, nullable=True)
    parada: Mapped[dict] = mapped_column(JSON, nullable=True)
    status_value: Mapped[str] = mapped_column(Enum(
        STATUS_ACTIVE, STATUS_DONE, STATUS_CANCELED, STATUS_CREATED), default=STATUS_CREATED)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    city_id: Mapped[int] = mapped_column(
        ForeignKey('cities.id'), nullable=False)
    driver_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('users.id'), nullable=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    status_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('ride_statuses.id'), nullable=True)
    service_requested_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('vehicle_categories.id'), nullable=True)

    city: Mapped["City"] = relationship("City", back_populates="rides")
    driver: Mapped["User"] = relationship(
        "User", foreign_keys=[driver_id], back_populates="rides_as_driver")
    customer: Mapped["User"] = relationship(
        "User", foreign_keys=[customer_id], back_populates="rides_as_customer")
    status: Mapped["RideStatus"] = relationship(
        "RideStatus", back_populates="rides")
    extras: Mapped[List["RideExtra"]] = relationship(
        "RideExtra", secondary=ride_extras_pivot)
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="ride")

    def serialize(self):
        return {
            "id": self.id,
            "pickup": self.pickup,
            "destination": self.destination,
            "parada": self.parada,
            "status": self.status_value,
            "status_translation": self.get_ride_status_translation(self.status_value),
            "created_at": self.created_at.isoformat(),
            "city": self.city.serialize() if self.city else None,
            "driver": self.driver.serialize() if self.driver else None,
            "customer": self.customer.serialize() if self.customer else None,
            "extras": [extra.serialize() for extra in self.extras]
        }

    @staticmethod
    def get_ride_status_translation(status: str) -> str:
        translations = {
            Ride.STATUS_ACTIVE: "activo",
            Ride.STATUS_DONE: "completado",
            Ride.STATUS_CANCELED: "cancelado",
            Ride.STATUS_CREATED: "creado",
        }
        return translations.get(status, status)

# =========================================================
# MODELOS RELACIONADOS
# =========================================================


class City(db.Model):
    __tablename__ = 'cities'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rides: Mapped[List["Ride"]] = relationship("Ride", back_populates="city")

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def madrid(cls):
        """
        Devuelve la ciudad con nombre 'madrid' (equivalente a City::madrid() en Laravel).
        """
        return cls.query.filter_by(name='madrid').first()

    @staticmethod
    def t(query: str) -> str:
        """
        Traduce 'city' y 'cities' al español, como en el modelo Laravel original.
        """
        translations = {
            "city": "ciudad",
            "cities": "ciudades"
        }
        return translations.get(query.lower(), query)


class DriverDocument(db.Model):
    __tablename__ = 'driver_documents'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
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

# =========================================================
# MODELOS DE VEHÍCULOS
# =========================================================


class VehicleBrand(db.Model):
    __tablename__ = 'vehicle_brands'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    models: Mapped[List["VehicleModel"]] = relationship(
        'VehicleModel', back_populates="brand")

    def serialize(self):
        return {"id": self.id, "name": self.name}


class VehicleModel(db.Model):
    __tablename__ = 'vehicle_models'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_id: Mapped[int] = mapped_column(ForeignKey('vehicle_brands.id'))

    brand: Mapped["VehicleBrand"] = relationship(
        "VehicleBrand", back_populates="models")
    vehicles: Mapped[List["Vehicle"]] = relationship(
        "Vehicle", back_populates="model")

    def __repr__(self):
        return f"<VehicleModel {self.name}>"

    def serialize(self):
        return {"id": self.id, "name": self.name, "brand": self.brand.name if self.brand else None}


class VehicleColor(db.Model):
    __tablename__ = 'vehicle_colors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hex: Mapped[str] = mapped_column(String(7), nullable=False)  # Ej: #FF0000

    vehicles: Mapped[List["Vehicle"]] = relationship(
        "Vehicle", back_populates="color")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hex": self.hex
        }


class VehicleCategory(db.Model):
    __tablename__ = 'vehicle_categories'

    id = Column(Integer, primary_key=True)
    img = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    rate = Column(Numeric(10, 2), nullable=False)
    min_rate = Column(Numeric(10, 2), nullable=True)
    airport_min_rate = Column(Numeric(10, 2), nullable=True)

    vehicles: Mapped[List["Vehicle"]] = relationship(
        "Vehicle", back_populates="category")

    def serialize(self):
        return {
            "id": self.id,
            "img": self.img,
            "name": self.name,
            "rate": float(self.rate) if self.rate else None,
            "min_rate": float(self.min_rate) if self.min_rate else None,
            "airport_min_rate": float(self.airport_min_rate) if self.airport_min_rate else None,
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_plate: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("vehicle_models.id"))
    color_id: Mapped[int] = mapped_column(ForeignKey("vehicle_colors.id"))
    category_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_categories.id"))

    model: Mapped["VehicleModel"] = relationship(
        "VehicleModel", back_populates="vehicles")
    color: Mapped["VehicleColor"] = relationship(
        "VehicleColor", back_populates="vehicles")
    category: Mapped["VehicleCategory"] = relationship(
        "VehicleCategory", back_populates="vehicles")

    # Relación inversa para polimorfismo
    driver: Mapped[Optional[Driver]] = relationship(
        "Driver", back_populates="vehicle", uselist=False)

    def __repr__(self):
        return f"<Vehicle {self.plate}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model.name if self.model else None,
            "color": self.color.name if self.color else None,
            "category": self.category.name if self.category else None
        }

# =========================================================
# OTROS MODELOS
# =========================================================


class Role(db.Model):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relación con usuarios (uno a muchos)
    users = relationship("User", secondary=roles_users, back_populates="roles")

    # Relación con permisos (muchos a muchos)
    permissions = relationship(
        "Permission", secondary=roles_permissions, back_populates="roles")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "permissions": [p.serialize() for p in self.permissions]
        }


class Permission(db.Model):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    roles = relationship("Role", secondary=roles_permissions,
                         back_populates="permissions")

    def serialize(self):
        return {"id": self.id, "name": self.name}


class Setting(db.Model):
    __tablename__ = 'settings'

    key: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    def serialize(self):
        return {"key": self.key, "display_name": self.display_name, "value": self.value}

# =========================================================
# TRANSACCIONES
# =========================================================


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    ride_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('rides.id'), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False)  # eg. "payment", "refund"
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    ride: Mapped[Optional["Ride"]] = relationship(
        "Ride", back_populates="transactions")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ride_id": self.ride_id,
            "amount": self.amount,
            "type": self.type,
            "currency": self.currency,
            "created_at": self.created_at.isoformat()
        }


"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'admin', 'driver', 'customer'
    type: Mapped[str] = mapped_column(String(50))  # para polimorfismo

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"

# Modelo para Admin
class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    # Ejemplo: métodos específicos para admin
    def can_manage_reservations(self):
        return True

    def can_edit_content(self):
        return True

# Modelo para Driver
class Driver(User):
    __mapper_args__ = {
        'polymorphic_identity': 'driver',
    }

    # Ejemplo de relación 1:1 con vehículo asignado
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="driver", uselist=False)

    def get_assigned_vehicle(self):
        return self.vehicle

    # Métodos específicos para conductor
    def can_view_assigned_trips(self):
        return True

# Modelo para Customer (Cliente)
class Customer(User):
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }

    marketing_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Métodos específicos para cliente
    def can_make_reservations(self):
        return True

    # Ejemplo de serialización para API
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "marketing_allowed": self.marketing_allowed,
        }

# Modelo Vehicle para relacionar con Driver
class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String(100))
    driver_id: Mapped[Optional[int]] = mapped_column(Integer, db.ForeignKey('users.id'), unique=True)
    driver: Mapped[Driver] = relationship("Driver", back_populates="vehicle", uselist=False)
"""
