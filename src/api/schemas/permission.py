from marshmallow import Schema, fields


class PermissionCreateSchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str()


class PermissionUpdateSchema(Schema):
    name = fields.Str()
    description = fields.Str()
