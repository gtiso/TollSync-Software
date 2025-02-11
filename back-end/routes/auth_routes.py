from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from config.db import db
import datetime
import jwt as pyjwt
from utils.auth import token_required

auth_bp = Blueprint("auth", __name__)

# Login Endpoint
@auth_bp.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": f"User {username} doesn't exist"}), 401
    elif check_password_hash(user.password_hash, password):
        token = pyjwt.encode(
            {'username': user.username, 'role': user.role, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            "your_secret_key",
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Logout Endpoint (Client-sided)
@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    return jsonify({"message": ""}), 204