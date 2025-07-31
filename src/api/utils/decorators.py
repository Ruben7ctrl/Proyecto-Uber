from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from api.models import User


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"msg": "Unauthorized"}), 403
        return func(*args, **kwargs)
    return wrapper
