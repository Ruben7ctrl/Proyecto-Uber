from marshmallow import Schema, fields, validate, ValidationError


def validate_password(pwd):
    if not (8 <= len(pwd) <= 16):
        raise ValidationError(
            "La contraseña debe tener entre 8 y 16 caracteres.")


class DriverCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password)
    vehicle_id = fields.Int(required=True)
    profile_photo_path = fields.Str(required=False, allow_none=True)


class DriverUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=3, max=255))
    email = fields.Email()
    password = fields.Str(validate=validate_password)
    vehicle_id = fields.Int()
    profile_photo_path = fields.Str(allow_none=True)
