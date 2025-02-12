from flask import Blueprint, jsonify, request
from config.db import db
from utils.auth import token_required
from utils.tagfiller import populate_tags_from_passes
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import os
from models.passes import Pass
from models.tag import Tag
from models.tollstation import TollStation
from models.user import User
from config.settings import Config
from dateutil import parser
import csv
import io

admin_bp = Blueprint("admin", __name__)

# HealthCheck Endpoint
@admin_bp.route('/api/admin/healthcheck', methods=['GET'])
@token_required
def healthcheck(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "dbconnection": "Admin access required!"} 
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401 
    try:
        db.session.execute(text('SELECT 1'))
        n_stations = db.session.query(TollStation).count()
        n_tags = db.session.query(Pass.tagRef).distinct().count()
        n_passes = db.session.query(Pass).count()
        response = {
            "status": "OK",
            "dbconnection": Config.SQLALCHEMY_DATABASE_URI,
            "n_stations": n_stations,
            "n_tags": n_tags,
            "n_passes": n_passes
        }
        if format_type == "csv":
            writer.writerow(response.keys())
            writer.writerow(response.values())
            return csv_output.getvalue(), 200
        else:
            return jsonify(response), 200
    except Exception as e:
        data = {"status": "failed", "dbconnection": str(e)}
        if format_type == "csv":
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400

# ResetStations Endpoint
@admin_bp.route('/api/admin/resetstations', methods=['POST'])
@token_required
def reset_stations(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "info": "Admin access required!"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401
    try:
        csv_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "misc", "tollstations2024.csv"))
        if not os.path.exists(csv_file):
            data = {"status": "failed", "info": "CSV file not found"}
            if format_type == "csv":
                writer.writerow(data.keys())
                writer.writerow(data.values())
                return csv_output.getvalue(), 400
            else:
                return jsonify(data), 400
        
        db.session.query(TollStation).delete()
        db.session.commit()
        
        with open(csv_file, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_station = TollStation(
                    OpID=row['OpID'],
                    Operator=row['Operator'],
                    TollID=row['TollID'],
                    Name=row['Name'],
                    PM=row['PM'],
                    Locality=row['Locality'],
                    Road=row['Road'],
                    Lat=float(row['Lat']),
                    Long=float(row['Long']),
                    Email=row['Email'],
                    Price1=float(row['Price1']),
                    Price2=float(row['Price2']),
                    Price3=float(row['Price3']),
                    Price4=float(row['Price4'])
                )
                db.session.add(new_station)
            db.session.commit()
        data = {"status": "OK"}
        if format_type == "csv":
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 200
        else:
            return jsonify(data), 200
    except Exception as e:
        data = {"status": "failed", "info": str(e)}
        if format_type == "csv":
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400

# ResetPasses Endpoint
@admin_bp.route('/api/admin/resetpasses', methods=['POST'])
@token_required
def reset_passes(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "info": "Admin access required!"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401
    try:
        db.session.query(Pass).delete()
        db.session.query(Tag).delete()
        db.session.commit()
        
        # Επαναφορά admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=generate_password_hash('freepasses4all', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin_user)
        else:
            admin_user.password_hash = generate_password_hash('freepasses4all', method='pbkdf2:sha256')
        db.session.commit()
        
        if format_type == "csv":
            csv_output = io.StringIO()
            writer = csv.writer(csv_output)
            writer.writerow(["status"])
            writer.writerow(["OK"])
            return csv_output.getvalue(), 200
        else:
            return jsonify({"status": "OK"}), 200
    except Exception as e:
        data = {"status": "failed", "info": str(e)}
        if format_type == "csv":
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400

# AddPasses Endpoint
@admin_bp.route('/api/admin/addpasses', methods=['POST'])
@token_required
def add_passes(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "info": "Admin access required!"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401
    
    if 'file' not in request.files:
        data = {"status": "failed", "info": "No file provided"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    file = request.files['file']
    
    try:
        upload_folder = os.path.abspath("uploads")  
        os.makedirs(upload_folder, exist_ok=True)  
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        
        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            counter = 0
            for row in reader:
                counter = counter + 1 
                new_pass = Pass(
                    timestamp = parser.parse(row['timestamp']),
                    tollID=row['tollID'],
                    tagRef=row['tagRef'],
                    tagHomeID=row['tagHomeID'],
                    charge=float(row['charge'])
                )
                db.session.add(new_pass)
            db.session.commit()
        os.remove(file_path)
        populate_tags_from_passes()
        if format_type == "csv":
            writer.writerow(["status"])
            writer.writerow(["OK"])
            return csv_output.getvalue(), 200
        else:
            return jsonify({"status": "OK"}), 200
    except Exception as e:
        data = {"status": "failed", "info": str(e)}
        if format_type == "csv":
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
# Endpoint to create or modify a user (--usermod)
@admin_bp.route('/api/admin/usermod', methods=['POST'])
@token_required
def usermod(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "info": "Admin access required!"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        data = {"status": "failed", "info": "Missing username or password"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
        

    user = User.query.filter_by(username=username).first()
    if user:
        user.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        db.session.commit()
        data = {"status": "OK", "info": f"User {username} updated successfully"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 200
        else:
            return jsonify(data), 200
    else:
        user = User(username=username, password_hash=generate_password_hash(password, method="pbkdf2:sha256"), role='user')
        db.session.add(user)
        db.session.commit()
        data = {"status": "OK", "info": f"User {username} created successfully"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 200
        else:
            return jsonify(data), 200


# Endpoint to list all users (--users)
@admin_bp.route('/api/admin/users', methods=['GET'])
@token_required
def list_users(current_user):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    if current_user.role != 'admin':
        data = {"status": "failed", "info": "Admin access required!"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 401
        else:
            return jsonify(data), 401

    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "role": user.role} for user in users]
    data = {"status": "OK", "users": user_list}
    if format_type == 'csv':
        writer.writerow(["status", "id", "username", "role"])
        for p in data["users"]:
            writer.writerow([data["status"], p["id"], p["username"], p["role"]])
        return csv_output.getvalue(), 200
    else:
        return jsonify(data), 200