# from sqlalchemy import String, Integer, ForeignKey, Enum, DateTime
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import String, Boolean, ForeignKey, Float, DateTime, Integer
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from datetime import datetime
# from sqlalchemy.ext.declarative import declared_attr
# from flask_security import UserMixin, RoleMixin
# from typing import ClassVar, List
# import os
# from flask import current_app

# db = SQLAlchemy()


# class User(db.Model):
#     __tablename__ = 'user'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(80), nullable=False)
#     email: Mapped[str] = mapped_column(
#         String(120), unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(nullable=False)
#     role: Mapped[str] = mapped_column(String(20), default="client")
#     is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

#     documents: Mapped[list["DriverDocument"]] = relationship(
#         back_populates="user", lazy=True)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "role": self.role,
#             "is_active": self.is_active
#         }


# class Drivers(db.Model):
#     __tablename__ = 'drivers'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(80), nullable=False)
#     vehicle: Mapped[str] = mapped_column(String(100), nullable=False)
#     available: Mapped[bool] = mapped_column(Boolean, default=True)

#     rides: Mapped[list["Ride"]] = relationship(
#         'Ride', back_populates="driver", lazy=True)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "vehicle": self.vehicle,
#             "available": self.available,
#         }


# class Ride(db.Model):
#     __tablename__ = 'ride'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
#     origin: Mapped[str] = mapped_column(String(255), nullable=False)
#     destination: Mapped[str] = mapped_column(String(255), nullable=False)
#     status: Mapped[str] = mapped_column(String(50), default="pending")
#     driver_id: Mapped[int | None] = mapped_column(
#         ForeignKey("driver.id"), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow)

#     driver: Mapped["Driver"] = relationship('Driver', back_populates="rides")

#     city_id: Mapped[int] = mapped_column(ForeignKey("city.id"), nullable=False)
#     city: Mapped["City"] = relationship("City", back_populates="rides")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "origin": self.origin,
#             "destination": self.destination,
#             "status": self.status,
#             "driver_id": self.driver_id,
#             "created_at": self.created_at.isoformat() if self.created_at else None
#         }


# class Transaction(db.Model):
#     __tablename__ = 'transaction'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     amount: Mapped[float] = mapped_column(Float, nullable=False)
#     timestamp: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "amount": self.amount,
#             "timestamp": self.timestamp.isoformat() if self.timestamp else None
#         }


# class Extra(db.Model):
#     __tablename__ = 'extra'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     price: Mapped[float] = mapped_column(Float, nullable=False)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "price": self.price
#         }


# class DriverDocument(db.Model):
#     __tablename__ = 'driver_documents'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
#     document_type: Mapped[str] = mapped_column(String(100), nullable=False)
#     file_path: Mapped[str] = mapped_column(String(255), nullable=False)
#     uploaded_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow)

#     user: Mapped["User"] = relationship("User", back_populates="documents")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "user_id": self.user_id,
#             "document_type": self.document_type,
#             "file_path": self.file_path,
#             "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
#         }


# class City(db.Model):
#     __tablename__ = 'city'

#     # Campos del modelo
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
#     display_name: Mapped[str] = mapped_column(String(100), nullable=True)

#     # Relaciones
#     rides: Mapped[list["Ride"]] = relationship(
#         "Ride", back_populates="city", lazy=True)

#     # Constantes
#     SINGULAR_NAME: ClassVar[str] = 'ciudad'
#     PLURAL_NAME: ClassVar[str] = 'ciudades'

#     @staticmethod
#     def t(query: str) -> str:
#         """Traducción de nombre del modelo."""
#         return {
#             "city": City.SINGULAR_NAME,
#             "cities": City.PLURAL_NAME,
#         }.get(query.lower(), query)

#     @staticmethod
#     def madrid():
#         """Devuelve la instancia de la ciudad 'madrid' si existe."""
#         return City.query.filter_by(name='madrid').first()

#     def serialize(self) -> dict:
#         return {
#             "id": self.id,
#             "name": self.name,
#             "display_name": self.display_name
#         }


# class Customer(db.Model):
#     __tablename__ = 'users'  # igual que en Laravel

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(80), nullable=False)
#     email: Mapped[str] = mapped_column(
#         String(120), unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(String(255), nullable=False)
#     profile_photo_path: Mapped[str] = mapped_column(String(255), nullable=True)
#     marketing_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

#     # Constantes de traducción
#     SINGULAR_NAME: ClassVar[str] = 'cliente'
#     PLURAL_NAME: ClassVar[str] = 'clientes'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "user": Customer.SINGULAR_NAME,
#             "users": Customer.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self) -> dict:
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "profile_photo_path": self.profile_photo_path,
#             "marketing_allowed": self.marketing_allowed
#         }

#     @staticmethod
#     def after_save_hook(mapper, connection, target):
#         """
#         Simula el comportamiento del evento `saved()` de Laravel,
#         y ejecuta un comando al guardar el cliente.
#         """
#         if not current_app.config.get("ENV") == "development":
#             # Aquí simularías ejecutar un comando tipo `Artisan::call`
#             # Por ejemplo, puedes usar subprocess o una función directa
#             print("📨 Ejecutando sincronización con Mailchimp...")
#             # subprocess.call(["python", "scripts/sync_mailchimp.py"]) ← si tienes script propio


# class Driver(db.Model):
#     __tablename__ = 'users'  # usa la misma tabla que User/Customer

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(80), nullable=False)
#     email: Mapped[str] = mapped_column(
#         String(120), unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(String(255), nullable=False)
#     role: Mapped[str] = mapped_column(String(20), default="driver")
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)

#     vehiculo_id: Mapped[int] = mapped_column(
#         ForeignKey('vehicle.id'), nullable=True)
#     vehicle: Mapped["Vehicle"] = relationship(
#         "Vehicle", back_populates="drivers")

#     # Traducción del modelo
#     SINGULAR_NAME: ClassVar[str] = 'cliente'
#     PLURAL_NAME: ClassVar[str] = 'clientes'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "user": Driver.SINGULAR_NAME,
#             "users": Driver.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "role": self.role,
#             "is_active": self.is_active,
#             "vehicle": self.vehicle.serialize() if self.vehicle else None
#         }


# class Permission(db.Model):
#     __tablename__ = 'permissions'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del nombre del modelo
#     SINGULAR_NAME: ClassVar[str] = 'permiso'
#     PLURAL_NAME: ClassVar[str] = 'permisos'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "permission": Permission.SINGULAR_NAME,
#             "permissions": Permission.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name
#         }


# class Ride(db.Model):
#     __tablename__ = 'rides'

#     # Estatus de los viajes
#     STATUS_ACTIVE = 'active'
#     STATUS_DONE = 'done'
#     STATUS_CANCELED = 'canceled'
#     STATUS_CREATED = 'created'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     pickup: Mapped[dict] = mapped_column(JSON, nullable=True)
#     destination: Mapped[dict] = mapped_column(JSON, nullable=True)
#     parada: Mapped[dict] = mapped_column(JSON, nullable=True)
#     status: Mapped[str] = mapped_column(Enum(
#         STATUS_ACTIVE, STATUS_DONE, STATUS_CANCELED, STATUS_CREATED), default=STATUS_CREATED)
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime, default=datetime.utcnow)

#     # Relaciones
#     city_id: Mapped[int] = mapped_column(ForeignKey('city.id'), nullable=False)
#     driver_id: Mapped[int] = mapped_column(
#         ForeignKey('user.id'), nullable=True)
#     customer_id: Mapped[int] = mapped_column(
#         ForeignKey('user.id'), nullable=False)
#     status_id: Mapped[int] = mapped_column(
#         ForeignKey('ride_status.id'), nullable=True)
#     service_requested_id: Mapped[int] = mapped_column(
#         ForeignKey('vehicle_category.id'), nullable=True)

#     city: Mapped["City"] = relationship("City")
#     driver: Mapped["User"] = relationship("User", foreign_keys=[driver_id])
#     customer: Mapped["User"] = relationship("User", foreign_keys=[customer_id])
#     status: Mapped["RideStatus"] = relationship("RideStatus")
#     service_requested: Mapped["VehicleCategory"] = relationship(
#         "VehicleCategory")
#     extras: Mapped[List["RideExtra"]] = relationship(
#         "RideExtra", secondary="ride_extras_pivot")

#     # Traducción del modelo
#     SINGULAR_NAME: ClassVar[str] = 'viaje'
#     PLURAL_NAME: ClassVar[str] = 'viajes'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "ride": Ride.SINGULAR_NAME,
#             "rides": Ride.PLURAL_NAME,
#         }.get(query.lower(), query)

#     @staticmethod
#     def get_ride_status_badge(status: str) -> str:
#         status_translation = Ride.get_ride_status_translation(status)
#         badge_classes = {
#             Ride.STATUS_ACTIVE: "badge bg-orange",
#             Ride.STATUS_DONE: "badge bg-green",
#             Ride.STATUS_CANCELED: "badge bg-red",
#         }
#         badge_class = badge_classes.get(status, "")
#         return f"<span class='text-capitalize {badge_class}' style='min-width:5rem;'>{status_translation}</span>"

#     @staticmethod
#     def get_ride_status_translation(status: str) -> str:
#         status_translations = {
#             Ride.STATUS_ACTIVE: "activo",
#             Ride.STATUS_DONE: "completado",
#             Ride.STATUS_CANCELED: "cancelado",
#             Ride.STATUS_CREATED: "creado",
#         }
#         return status_translations.get(status, status)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "pickup": self.pickup,
#             "destination": self.destination,
#             "parada": self.parada,
#             "status": self.status,
#             "status_translation": Ride.get_ride_status_translation(self.status),
#             "created_at": self.created_at.isoformat(),
#             "city": self.city.serialize() if self.city else None,
#             "driver": self.driver.serialize() if self.driver else None,
#             "customer": self.customer.serialize() if self.customer else None,
#             "service_requested": self.service_requested.serialize() if self.service_requested else None,
#             "extras": [extra.serialize() for extra in self.extras]
#         }


# class RideExtra(db.Model):
#     __tablename__ = 'ride_extras'

#     # Campos del modelo
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     price: Mapped[float] = mapped_column(Float, nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME: ClassVar[str] = 'extra'
#     PLURAL_NAME: ClassVar[str] = 'extras'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'rideextra': RideExtra.SINGULAR_NAME,
#             'ride_extras': RideExtra.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "price": self.price
#         }


# class RideStatus(db.Model):
#     __tablename__ = 'ride_statuses'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     display_name: Mapped[str] = mapped_column(String(255), nullable=False)
#     # Para el código de color hexadecimal
#     hex: Mapped[str] = mapped_column(String(7), nullable=False)

#     # Relación
#     rides: Mapped[List["Ride"]] = relationship("Ride", back_populates="status")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "display_name": self.display_name,
#             "hex": self.hex
#         }


# class Role(db.Model):
#     __tablename__ = 'roles'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     display_name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME: ClassVar[str] = 'rol'
#     PLURAL_NAME: ClassVar[str] = 'roles'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "role": Role.SINGULAR_NAME,
#             "roles": Role.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "display_name": self.display_name
#         }


# class Setting(db.Model):
#     __tablename__ = 'settings'

#     # Clave primaria personalizada
#     key: Mapped[str] = mapped_column(primary_key=True)
#     display_name: Mapped[str] = mapped_column(String(255), nullable=False)
#     value: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME: ClassVar[str] = 'ajuste'
#     PLURAL_NAME: ClassVar[str] = 'ajustes'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "setting": Setting.SINGULAR_NAME,
#             "settings": Setting.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "key": self.key,
#             "display_name": self.display_name,
#             "value": self.value
#         }


# # Relación con el modelo de roles
# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
# )


# class User(db.Model, UserMixin):
#     __tablename__ = 'users'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     email: Mapped[str] = mapped_column(
#         String(255), unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(String(255), nullable=False)
#     marketing_allowed: Mapped[bool] = mapped_column(Boolean, default=False)

#     # Traducción del modelo
#     SINGULAR_NAME = 'usuario'
#     PLURAL_NAME = 'usuarios'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'user': User.SINGULAR_NAME,
#             'users': User.PLURAL_NAME,
#         }.get(query.lower(), query)

#     # Relaciones
#     roles: Mapped[List["Role"]] = relationship(
#         'Role', secondary=roles_users, backref="users")

#     # Métodos estáticos para obtener clientes y conductores
#     @staticmethod
#     def customers():
#         return User.query.filter(User.roles.any(name='cliente')).all()

#     @staticmethod
#     def drivers():
#         return User.query.filter(User.roles.any(name='conductor')).all()

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "email": self.email,
#             "marketing_allowed": self.marketing_allowed
#         }


# class Vehicle(db.Model):
#     __tablename__ = 'vehicles'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME = 'vehiculo'
#     PLURAL_NAME = 'vehiculos'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'vehicle': Vehicle.SINGULAR_NAME,
#             'vehicles': Vehicle.PLURAL_NAME,
#         }.get(query.lower(), query)

#     # Relaciones
#     model_id: Mapped[int] = mapped_column(db.ForeignKey("vehicle_models.id"))
#     color_id: Mapped[int] = mapped_column(db.ForeignKey("vehicle_colors.id"))
#     category_id: Mapped[int] = mapped_column(
#         db.ForeignKey("vehicle_categories.id"))

#     model: Mapped["VehicleModel"] = relationship("VehicleModel")
#     color: Mapped["VehicleColor"] = relationship("VehicleColor")
#     driver: Mapped["Driver"] = relationship(
#         "Driver", back_populates="vehicle", uselist=False)
#     category: Mapped["VehicleCategory"] = relationship("VehicleCategory")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "model": self.model.name if self.model else None,
#             "color": self.color.name if self.color else None,
#             "category": self.category.name if self.category else None
#         }


# class VehicleBrand(db.Model):
#     __tablename__ = 'vehicle_brands'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME = 'marca'
#     PLURAL_NAME = 'marcas'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'vehiclebrand': VehicleBrand.SINGULAR_NAME,
#             'vehicle_brands': VehicleBrand.PLURAL_NAME,
#         }.get(query.lower(), query)

#     # Relaciones
#     models: Mapped[List["VehicleModel"]] = relationship(
#         'VehicleModel', backref="brand", lazy=True)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name
#         }


# class VehicleCategory(db.Model):
#     __tablename__ = 'vehicle_categories'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME = 'categoria'
#     PLURAL_NAME = 'categorias'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'vehiclecategory': VehicleCategory.SINGULAR_NAME,
#             'vehicle_categories': VehicleCategory.PLURAL_NAME,
#         }.get(query.lower(), query)

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name
#         }


# class VehicleColor(db.Model):
#     __tablename__ = 'vehicle_colors'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)

#     # Traducción del modelo
#     SINGULAR_NAME = 'color'
#     PLURAL_NAME = 'colores'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             "vehiclecolor": VehicleColor.SINGULAR_NAME,
#             "vehicle_colors": VehicleColor.PLURAL_NAME,
#         }.get(query.lower(), query)

#     # Relaciones
#     vehiculos = relationship("Vehicle", back_populates="color")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name
#         }


# class VehicleModel(db.Model):
#     __tablename__ = 'vehicle_models'

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255), nullable=False)
#     brand_id: Mapped[int] = mapped_column(ForeignKey('vehicle_brands.id'))

#     # Traducción del modelo
#     SINGULAR_NAME = 'modelo'
#     PLURAL_NAME = 'modelos'

#     @staticmethod
#     def t(query: str) -> str:
#         return {
#             'vehiclemodel': VehicleModel.SINGULAR_NAME,
#             'vehicle_models': VehicleModel.PLURAL_NAME,
#         }.get(query.lower(), query)

#     # Relaciones
#     brand = relationship("VehicleBrand", back_populates="models")
#     vehiculos = relationship("Vehicle", back_populates="model")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "brand_id": self.brand_id,
#         }
