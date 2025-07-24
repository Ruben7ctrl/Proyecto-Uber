import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.models import db, DriverDocument

documents_bp = Blueprint("documents_bp", __name__, url_prefix='/documents')

UPLOAD_FOLDER = "uploads/documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@documents_bp.route("/upload", methods=["POST"])
def upload_document():
    driver_id = request.form.get("driver_id")
    document_type = request.form.get("document_type")
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file provided"}), 400
    if not driver_id or not document_type:
        return jsonify({"error": "driver_id and document_type are required"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    doc = DriverDocument(
        driver_id=driver_id,
        document_type=document_type,
        document_url=filepath
    )
    db.session.add(doc)
    db.session.commit()

    return jsonify({"message": "Document uploaded"}), 201


@documents_bp.route("/<int:driver_id>", methods=["GET"])
def list_documents(driver_id):
    docs = DriverDocument.query.filter_by(driver_id=driver_id).all()
    return jsonify([{
        "id": d.id,
        "type": d.document_type,
        "status": d.status,
        "url": d.document_url
    } for d in docs])


@documents_bp.route("/<int:doc_id>/status", methods=["PUT"])
def update_status(doc_id):
    data = request.get_json() or {}
    doc = DriverDocument.query.get_or_404(doc_id)
    doc.status = data.get("status", doc.status)
    db.session.commit()
    return jsonify({"message": "Document status updated"})
