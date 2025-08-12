from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from api.models2 import Ride


class RideSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ride
        include_fk = True
        load_instance = True
