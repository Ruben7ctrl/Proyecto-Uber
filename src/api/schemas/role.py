from marshmallow import Schema, fields, validate


class RoleCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    display_name = fields.Str(
        required=True, validate=validate.Length(min=1, max=255))


class RoleUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    display_name = fields.Str(validate=validate.Length(min=1, max=255))
