"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, Imagen
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from dbfread import DBF
import os

# ruta = '/Users/rubencabellomiguel/Downloads/datos/almacen.dbf'
# print(f"Existe archivo: {os.path.isfile(ruta)}")

# tabla = DBF(ruta, encoding='latin1')
# for row in tabla:
#     print(row)
#     break  # solo para ver la primera fila

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

api = Blueprint('api', __name__)

# Allow CORS requests to this API
# CORS(api)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/upload-imagen', methods=['POST'])
def upload_imagen():
    sku = request.form.get('sku')
    descripcion = request.form.get('descripcion')
    file = request.files.get('imagen')

    if not file or not sku:
        return jsonify({"error": "Faltan datos"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{sku}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        nueva_imagen = Imagen(sku=sku, imagen_url=filepath, descripcion=descripcion)
        db.session.add(nueva_imagen)
        db.session.commit()

        return jsonify({"message": "Imagen subida con éxito", "imagen": filepath}), 200

    return jsonify({"error": "Archivo no válido"}), 400


@api.route('/productos-con-imagen')
def get_productos_con_imagen():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/articulo.dbf', encoding='latin1')
    productos = []

    for row in tabla:
        producto = dict(row)
        sku = producto.get("CODIGO")  # o el campo SKU real en tu DBF
        imagen = Imagen.query.filter_by(sku=sku).first()

        producto['imagen_url'] = imagen.imagen_url if imagen else None
        productos.append(producto)

    return jsonify(productos)


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

@api.route('/factura')
def get_factura():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/factural.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

@api.route('/familia')
def get_familia():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/familias.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

@api.route('/prueba')
def get_prueba():
    tabla = DBF('/workspaces/react-flask-hello/src/front/assets/img/proveedo.dbf', encoding='latin1')
    productos = [dict(row) for row in tabla]
    return jsonify(productos)

