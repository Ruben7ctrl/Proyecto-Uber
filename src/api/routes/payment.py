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
