from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate  # <-- añadido
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    Migrate(app, db)  # <-- añadido

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/v1")

    from .routes.ride import ride_bp
    app.register_blueprint(ride_bp, url_prefix="/api/v1/ride")

    from .routes.maps import maps_bp
    app.register_blueprint(maps_bp, url_prefix="/api/v1/maps")

    from .routes.payment import payment_bp
    app.register_blueprint(payment_bp, url_prefix="/api/v1/payment")

    from .routes.notifications import notifications_bp
    app.register_blueprint(
        notifications_bp, url_prefix="/api/v1/notifications")

    from .routes.users import users_bp
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    from .routes.admin_dashboard import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")

    from .routes.balance import balance_bp
    app.register_blueprint(balance_bp, url_prefix="/api/v1/balance")

    from .routes.documents import documents_bp
    app.register_blueprint(documents_bp, url_prefix="/api/v1/documents")

    from .routes.incidents import incidents_bp
    app.register_blueprint(incidents_bp, url_prefix="/api/v1/incidents")

    from .routes.config import config_bp
    app.register_blueprint(config_bp, url_prefix="/api/v1/config")

    from .routes.images import images_bp
    app.register_blueprint(images_bp, url_prefix="/api/v1/images")

    return app
