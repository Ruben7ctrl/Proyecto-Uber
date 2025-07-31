from marshmallow import Schema, fields, validate


class RideExtraSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True)
