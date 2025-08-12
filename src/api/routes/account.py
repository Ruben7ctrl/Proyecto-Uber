from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models2 import db, User
from app.schemas.user_schemas import UserSchema

account_bp = Blueprint('account_bp', __name__, url_prefix='/api/account')

user_schema = UserSchema()


@account_bp.route('/edit', methods=['PUT'])
@jwt_required()
def edit_account():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    # Actualizar solo los campos permitidos
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating user', 'error': str(e)}), 500

    return jsonify({
        'user': user_schema.dump(user),
        'message': 'Success',
    }), 200


@account_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def show_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user)), 200
