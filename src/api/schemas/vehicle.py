from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import validates, ValidationError
from ..models import (
    VehicleBrand,
    VehicleModel,
    VehicleColor,
    VehicleCategory,
    Vehicle,
)
from ..models import db

# VehicleBrand Schema


class VehicleBrandSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VehicleBrand
        sqla_session = db.session
        load_instance = True

    name = auto_field(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError(
                "El nombre de la marca no puede estar vacío.")

# VehicleModel Schema


class VehicleModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VehicleModel
        sqla_session = db.session
        load_instance = True
        include_fk = True

    name = auto_field(required=True)
    brand_id = auto_field(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("El nombre del modelo no puede estar vacío.")

# VehicleColor Schema


class VehicleColorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VehicleColor
        sqla_session = db.session
        load_instance = True

    name = auto_field(required=True)
    hex = auto_field(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("El nombre del color no puede estar vacío.")

# VehicleCategory Schema


class VehicleCategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = VehicleCategory
        sqla_session = db.session
        load_instance = True

    name = auto_field(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError(
                "El nombre de la categoría no puede estar vacío.")

# Vehicle Schema


class VehicleSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        sqla_session = db.session
        load_instance = True
        include_fk = True

    plate = auto_field(required=True)
    model_id = auto_field(required=True)
    color_id = auto_field(required=True)
    category_id = auto_field(required=True)

    @validates("plate")
    def validate_plate(self, value):
        if not value.strip():
            raise ValidationError("La matrícula no puede estar vacía.")
