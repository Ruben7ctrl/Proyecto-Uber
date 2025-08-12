from flask import Blueprint, request, jsonify
from api import db
from api.models2 import IncidentReport

incidents_bp = Blueprint("incidents_bp", __name__, url_prefix="/incidents")


@incidents_bp.route("/", methods=["POST"])
def report_incident():
    data = request.get_json() or {}
    incident = IncidentReport(
        reporter_id=data.get("reporter_id"),
        ride_id=data.get("ride_id"),
        subject=data.get("subject"),
        description=data.get("description")
    )
    if not incident.reporter_id or not incident.subject or not incident.description:
        return jsonify({"error": "Missing required fields"}), 400
    db.session.add(incident)
    db.session.commit()
    return jsonify({"message": "Incident reported"}), 201


@incidents_bp.route("/", methods=["GET"])
def list_incidents():
    incidents = IncidentReport.query.all()
    return jsonify([{
        "id": i.id,
        "reporter_id": i.reporter_id,
        "ride_id": i.ride_id,
        "subject": i.subject,
        "description": i.description,
        "status": i.status,
        "created_at": i.created_at.isoformat() if i.created_at else None
    } for i in incidents])


@incidents_bp.route("/<int:incident_id>/status", methods=["PUT"])
def update_status(incident_id):
    data = request.get_json() or {}
    incident = IncidentReport.query.get_or_404(incident_id)
    incident.status = data.get("status", incident.status)
    db.session.commit()
    return jsonify({"message": "Status updated"})
