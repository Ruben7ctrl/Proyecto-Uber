from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Imagen(db.Model):
    __tablename__ = 'imagenes'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String, nullable=False)  # Debe coincidir con el SKU del producto
    imagen_url = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.String)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "sku": self.sku,
            "imagen": self.imagen_url,
            "description": self.descripcion,
            # do not serialize the password, its a security breach
        }