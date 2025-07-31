from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from app.models import db, Ride, RideExtra, Setting, User
from app.schemas.ride_schema import RideSchema
from app.utils.email_utils import send_service_inquiry_email
from app.utils.google_maps import get_lat_lng_from_place_id

cliente_bp = Blueprint('cliente_bp', __name__, url_prefix='/api/cliente')


@cliente_bp.route('/book', methods=['POST'])
def book_ride():
    data = request.get_json()

    service_id = data.get('service')
    user_id = data.get('user_id')
    extras_ids = data.get('extras', [])

    if not service_id or not user_id:
        return jsonify({'message': 'Faltan campos requeridos'}), 400

    user = User.query.get_or_404(user_id)
    new_ride = user.new_ride  # Se espera que esté precargado desde lógica previa

    app_tax = float(Setting.query.get('tax').value) / 100
    app_fee = float(Setting.query.get('operative_fee').value) / 100

    extras = RideExtra.query.filter(RideExtra.id.in_(extras_ids)).all()
    extras_total = sum(extra.price for extra in extras)

    subtotal = total = new_ride['computed']['ride_price']
    tax = subtotal * app_tax
    fee = subtotal * app_fee
    total = round(subtotal + tax + fee + extras_total, 2)

    if service_id == 4:  # Minibús
        send_service_inquiry_email(user, extras, extras_total)
        return jsonify({
            'service': service_id,
            'status': 'success',
            'distance': 0,
            'time': 0,
        })

    ride = Ride(
        status_id=1,
        city_id=1,
        customer_id=user.id,
        service_requested_id=service_id,
        pickup=new_ride['userInput']['pickup'],
        destination=new_ride['userInput']['destination'],
        parada=new_ride['userInput'].get('parada'),
        total_distance=new_ride['computed']['distance'],
        duration=new_ride['computed']['duration'] / 60,
        subtotal=subtotal,
        tax=tax,
        fee=fee,
        extras_total=extras_total,
        total=total
    )

    db.session.add(ride)
    db.session.commit()
    ride.extras.extend(extras)
    db.session.commit()

    return jsonify({
        'status': 'OK',
        'message': 'Se ha reservado el servicio correctamente.',
        'ride': RideSchema().dump(ride)
    })


@cliente_bp.route('/place-coordinates', methods=['POST'])
def place_coordinates():
    data = request.get_json()
    place_id = data.get('place_id')

    if not place_id:
        return jsonify({'message': 'Falta el place_id'}), 400

    coords = get_lat_lng_from_place_id(place_id)
    if coords:
        return jsonify({'location': coords}), 200
    else:
        return jsonify({'message': 'No se pudo obtener la ubicación'}), 500
