"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Imagen
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from api.routes.admin import admin_bp
from api.routes.auth import auth_bp
from api.routes.balance import balance_bp
from api.routes.config import config_bp
from api.routes.documents import documents_bp
from api.routes.extras import extras_bp
from api.routes.images import images_bp
from api.routes.incidents import incidents_bp
from api.routes.maps import maps_bp
from api.routes.notifications import notifications_bp
from api.routes.payment import payment_bp
from api.routes.places import places_bp
from api.routes.ride import ride_bp
from .routes.users import users_bp


api = Blueprint('api', __name__)
api.register_blueprint(admin_bp)
api.register_blueprint(auth_bp)
api.register_blueprint(balance_bp)
api.register_blueprint(config_bp)
api.register_blueprint(documents_bp)
api.register_blueprint(extras_bp)
api.register_blueprint(images_bp)
api.register_blueprint(incidents_bp)
api.register_blueprint(maps_bp)
api.register_blueprint(notifications_bp)
api.register_blueprint(payment_bp)
api.register_blueprint(places_bp)
api.register_blueprint(ride_bp)
api.register_blueprint(users_bp)


# Allow CORS requests to this API
# CORS(api)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200
