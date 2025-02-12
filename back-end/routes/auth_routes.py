from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from models.user import User
import datetime
import jwt as pyjwt
from utils.auth import token_required
import io
import csv

auth_bp = Blueprint("auth", __name__)

# Login Endpoint
@auth_bp.route('/api/login', methods=['POST'])
def login():
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        data = {"message": "Missing username or password"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        data = {"message": f"User {username} doesn't exist"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401
    elif check_password_hash(user.password_hash, password):
        token = pyjwt.encode(
            {'username': user.username, 'role': user.role, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            "your_secret_key",
            algorithm="HS256"
        )
        data = {"token": token}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 200
        else:
            return jsonify(data), 200
    else:
        data = {"message": "Invalid credentials"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401

# Logout Endpoint (Client-sided)
@auth_bp.route('/api/logout', methods=['POST'])
@token_required
def logout(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    data = {"message": ""}
    if format_type == 'csv':
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return csv_output.getvalue(), 204
    else:
        return jsonify(data), 204