import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api import db
from api.models import UserImage

images_bp = Blueprint("images_bp", __name__, url_prefix='/images')

UPLOAD_FOLDER = "uploads/images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@images_bp.route("/upload", methods=["POST"])
def upload_image():
    user_id = request.form.get("user_id")
    image_type = request.form.get("image_type")
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400
    if not user_id or not image_type:
        return jsonify({"error": "user_id and image_type are required"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    img = UserImage(user_id=user_id, image_type=image_type, image_url=filepath)
    db.session.add(img)
    db.session.commit()

    return jsonify({"message": "Image uploaded"}), 201


@images_bp.route("/<int:user_id>", methods=["GET"])
def list_images(user_id):
    images = UserImage.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": i.id,
        "type": i.image_type,
        "url": i.image_url
    } for i in images])
