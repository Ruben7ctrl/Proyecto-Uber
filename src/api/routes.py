"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from dbfread import DBF
# import os

# ruta = '/Users/rubencabellomiguel/Downloads/datos/almacen.dbf'
# print(f"Existe archivo: {os.path.isfile(ruta)}")

# tabla = DBF(ruta, encoding='latin1')
# for row in tabla:
#     print(row)
#     break  # solo para ver la primera fila




api = Blueprint('api', __name__)

# Allow CORS requests to this API
# CORS(api)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


@api.route('/productos')
def get_productos():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/articulo.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

@api.route('/colores')
def get_colors():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/colores.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

@api.route('/tallas')
def get_tallas():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/tallajes.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

@api.route('/prueba')
def get_prueba():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/pathconfig.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)