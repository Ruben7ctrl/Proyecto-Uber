
import os
from flask_admin import Admin
from .models2 import db, User, VehicleBrand, VehicleCategory, VehicleColor, VehicleModel, Vehicle
from flask_admin.contrib.sqla import ModelView
from .admin_views import VehicleBrandAdmin, VehicleCategoryAdmin, VehicleColorAdmin, VehicleModelAdmin, VehicleAdmin


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(VehicleBrandAdmin(VehicleBrand, db.session))
    admin.add_view(VehicleCategoryAdmin(VehicleCategory, db.session))
    admin.add_view(VehicleColorAdmin(VehicleColor, db.session))
    admin.add_view(VehicleModelAdmin(VehicleModel, db.session))
    admin.add_view(VehicleAdmin(Vehicle, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
