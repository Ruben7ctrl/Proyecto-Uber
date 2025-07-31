import stripe
from flask import Blueprint, request, jsonify
import os

payment_bp = Blueprint("payment_bp", __name__, url_prefix="/payment")

# Cargar la clave secreta desde variables de entorno
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_dummy")


@payment_bp.route("/create-payment-intent", methods=["POST"])
def create_payment():
    data = request.get_json()
    amount = data.get("amount")  # en centavos

    if not amount:
        return jsonify({"error": "Amount is required"}), 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency="usd",
            payment_method_types=["card"]
        )
        return jsonify({
            "client_secret": intent.client_secret,
            "message": "Payment intent created"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@payment_bp.route("/pay-ride", methods=["POST"])
def pay_ride():
    data = request.get_json()
    ride_id = data.get("ride_id")
    # Deberías pasar el total desde frontend o calcularlo en backend
    total_amount = data.get("total")

    if not ride_id or not total_amount:
        return jsonify({"error": "ride_id and total are required"}), 400

    # Aquí podrías buscar el ride en la DB si usas un ORM, para validar que existe y obtener info

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'Servicio Ride #{ride_id}',
                    },
                    # total en centavos
                    'unit_amount': int(float(total_amount) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.getenv('MOBILE_APP_URL', '') + "/viaje-pagado",
            cancel_url=os.getenv('MOBILE_APP_URL', '') + "/confirmar-viaje",
        )
        return jsonify({'status': 'OK', 'session_id': session.id})
    except Exception as e:
        return jsonify({'status': 'ER', 'msg': str(e)}), 400
