from flask import Blueprint, jsonify, request
from api.models2 import db, Transaction, User
from sqlalchemy.exc import SQLAlchemyError

balance_bp = Blueprint("balance_bp", __name__, url_prefix='/balance')


@balance_bp.route("/<int:user_id>", methods=["GET"])
def get_balance(user_id):
    user = User.query.get_or_404(user_id)
    credits = sum(t.amount for t in user.transactions if t.type == "credit")
    debits = sum(t.amount for t in user.transactions if t.type == "debit")
    balance = credits - debits
    return jsonify({
        "user_id": user_id,
        "balance": balance,
        "credits": credits,
        "debits": debits
    })


@balance_bp.route("/<int:user_id>/transactions", methods=["GET"])
def get_transactions(user_id):
    user = User.query.get_or_404(user_id)
    transactions = [{
        "id": t.id,
        "amount": t.amount,
        "type": t.type,
        "description": t.description,
        "created_at": t.created_at.isoformat()
    } for t in user.transactions]
    return jsonify(transactions)


@balance_bp.route("/<int:user_id>/add", methods=["POST"])
def add_transaction(user_id):
    data = request.get_json() or {}
    amount = data.get("amount")
    t_type = data.get("type")
    description = data.get("description", "")

    if amount is None or t_type not in {"credit", "debit"}:
        return jsonify({"error": "Invalid transaction data"}), 400

    user = User.query.get_or_404(user_id)

    try:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=t_type,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    return jsonify({"message": "Transaction recorded", "transaction_id": transaction.id}), 201
