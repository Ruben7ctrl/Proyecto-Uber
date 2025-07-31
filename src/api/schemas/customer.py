from marshmallow import Schema, fields, validate


class CustomerCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True, validate=validate.Length(min=8, max=16))
    marketing_allowed = fields.Bool(missing=False)
    # profile_photo_path puede ser manejado aparte en subida


class CustomerUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=3, max=255))
    email = fields.Email()
    password = fields.Str(validate=validate.Length(min=8, max=16))
    marketing_allowed = fields.Bool()
