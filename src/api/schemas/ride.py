from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Ride


class RideSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ride
        include_fk = True
        load_instance = True
