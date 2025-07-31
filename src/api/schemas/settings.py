from marshmallow import Schema, fields, validate


class SettingCreateSchema(Schema):
    key = fields.Str(required=True, validate=validate.Length(min=1))
    display_name = fields.Str(required=True, validate=validate.Length(min=1))
    value = fields.Str(required=True, validate=validate.Length(min=1))


class SettingUpdateSchema(Schema):
    display_name = fields.Str(required=False)
    value = fields.Str(required=False)
