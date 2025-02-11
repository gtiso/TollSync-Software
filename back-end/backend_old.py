from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil import parser
import jwt as pyjwt
import datetime
from functools import wraps
import csv
import os

# Αρχικοποίηση Flask app
app = Flask(__name__)

# Ρυθμίσεις σύνδεσης MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:user@localhost/tollsync'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

# Ορισμός μοντέλων δεδομένων
class TollStation(db.Model):
    TollID = db.Column(db.String(10), primary_key=True)
    OpID = db.Column(db.String(10), nullable=False)
    Name = db.Column(db.String(255), nullable=False)
    Operator = db.Column(db.String(100), nullable=False)
    PM = db.Column(db.String(10), nullable=False)
    Locality = db.Column(db.String(255), nullable=False)
    Road = db.Column(db.String(255), nullable=False)
    Lat = db.Column(db.Float, nullable=False)
    Long = db.Column(db.Float, nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Price1 = db.Column(db.Float, nullable=False)
    Price2 = db.Column(db.Float, nullable=False)
    Price3 = db.Column(db.Float, nullable=False)
    Price4 = db.Column(db.Float, nullable=False)

class Pass(db.Model):
    passID = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    timestamp = db.Column(db.DateTime, nullable=False)
    tollID = db.Column(db.String(10), db.ForeignKey('toll_station.TollID'), nullable=False)
    tagRef = db.Column(db.String(50), nullable=False)
    tagHomeID = db.Column(db.String(10), nullable=False)
    charge = db.Column(db.Float, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

# Middleware για έλεγχο JWT με ρόλους
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-OBSERVATORY-AUTH')  
        if not token:
            return jsonify({"message": "Token is missing!"}), 400
        try:
            data = pyjwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Login Endpoint
@app.route('/login', methods=['POST'])
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
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Logout Endpoint (Client-sided)
@app.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return ('', 204)  

# HealthCheck Endpoint
@app.route('/admin/healthcheck', methods=['GET'])
@token_required
def healthcheck(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "dbconnection": "Admin access required!"}), 401
    try:
        db.session.execute(text('SELECT 1'))
        n_stations = db.session.query(TollStation).count()
        n_tags = db.session.query(Pass.tagRef).distinct().count()
        n_passes = db.session.query(Pass).count()
        return jsonify({
            "status": "OK",
            "dbconnection": app.config['SQLALCHEMY_DATABASE_URI'],
            "n_stations": n_stations,
            "n_tags": n_tags,
            "n_passes": n_passes
        }), 200
    except Exception as e:
        return jsonify({"status": "failed", "dbconnection": str(e)}), 401

# ResetStations Endpoint
@app.route('/admin/resetstations', methods=['POST'])
@token_required
def reset_stations(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "info": "Admin access required!"}), 401
    try:
        csv_file = os.path.join(os.path.dirname(__file__), "misc", "tollstations2024.csv")
        if not os.path.exists(csv_file):
            return jsonify({"status": "failed", "info": "CSV file not found"}), 400
        
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
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 400

# ResetPasses Endpoint
@app.route('/admin/resetpasses', methods=['POST'])
@token_required
def reset_passes(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "info": "Admin access required!"}), 401
    try:
        db.session.query(Pass).delete()
        db.session.commit()
        
        # Επαναφορά admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', password_hash=generate_password_hash('freepasses4all', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin_user)
        else:
            admin_user.password_hash = generate_password_hash('freepasses4all', method='pbkdf2:sha256')
        db.session.commit()
        
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 400

# AddPasses Endpoint
@app.route('/admin/addpasses', methods=['POST'])
@token_required
def add_passes(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "info": "Admin access required!"}), 401
    
    if 'file' not in request.files:
        return jsonify({"status": "failed", "info": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename != 'passes-sample.csv':
        return jsonify({"status": "failed", "info": "Invalid file name"}), 400
    
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
        return jsonify({"status": "OK"}), 200
    except Exception as e:
        return jsonify({"status": "failed", "info": str(e)}), 400
    
# Endpoint to create or modify a user (--usermod)
@app.route('/admin/usermod', methods=['POST'])
@token_required
def usermod(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "info": "Admin access required!"}), 401

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"status": "failed", "info": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        user.password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        db.session.commit()
        return jsonify({"status": "OK", "info": f"User {username} updated successfully"}), 200
    else:
        user = User(username=username, password_hash=generate_password_hash(password, method="pbkdf2:sha256"), role='user')
        db.session.add(user)
        db.session.commit()
        return jsonify({"status": "OK", "info": f"User {username} created successfully"}), 200


# Endpoint to list all users (--users)
@app.route('/admin/users', methods=['GET'])
@token_required
def list_users(current_user):
    if current_user.role != 'admin':
        return jsonify({"status": "failed", "info": "Admin access required!"}), 401

    users = User.query.all()
    user_list = [{"id": user.id, "username": user.username, "role": user.role} for user in users]

    return jsonify({"status": "OK", "users": user_list}), 200

# TollStationPasses Endpoint
@app.route('/tollStationPasses/<tollStationID>/<date_from>/<date_to>', methods=['GET'])
def toll_station_passes(tollStationID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)

    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    station = TollStation.query.filter_by(TollID=tollStationID).first()
    if not station:
        return jsonify({"status": "failed", "info": "Toll station not found"}), 400
    
    passes = Pass.query.filter(
        Pass.tollID == tollStationID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date
    ).all()
    
    response = {
        "stationID": station.TollID,
        "stationOperator": station.OpID,
        "requestTimestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodFrom": start_date.strftime("%Y-%m-%d"),
        "periodTo": end_date.strftime("%Y-%m-%d"),
        "nPasses": len(passes),
        "passList": [
            {
                "passIndex": i + 1,
                "passID": p.passID,
                "timestamp": p.timestamp.strftime("%Y-%m-%d %H:%M"),
                "tagID": p.tagRef,
                "tagProvider": p.tagHomeID,
                "passType": "home" if p.tagHomeID == station.OpID else "visitor",
                "passCharge": p.charge
            }
            for i, p in enumerate(passes)
        ]
    }
    return jsonify(response)

# PassAnalysis Endpoint
@app.route('/passAnalysis/<stationOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def pass_analysis(current_user, stationOpID, tagOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    passes = Pass.query.join(TollStation, Pass.tollID == TollStation.TollID)
    passes = passes.filter(
        TollStation.OpID == stationOpID,
        Pass.tagHomeID == tagOpID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date
    ).all()
    
    response = {
        "stationOpID": stationOpID,
        "tagOpID": tagOpID,
        "requestTimestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodFrom": start_date.strftime("%Y-%m-%d"),
        "periodTo": end_date.strftime("%Y-%m-%d"),
        "nPasses": len(passes),
        "passList": [
            {
                "passIndex": i + 1,
                "passID": pass_obj.passID,
                "stationID": pass_obj.tollID,
                "timestamp": pass_obj.timestamp.strftime("%Y-%m-%d %H:%M"),
                "tagID": pass_obj.tagRef,
                "passCharge": pass_obj.charge
            }
            for i, pass_obj in enumerate(passes)
        ]
    }
    return jsonify(response)

# PassesCost Endpoint
@app.route('/passesCost/<tollOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def passes_cost(current_user, tollOpID, tagOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    query = db.session.query(
        func.count(Pass.passID).label("nPasses"),
        func.sum(Pass.charge).label("passesCost")
    ).join(TollStation, Pass.tollID == TollStation.TollID)
    
    query = query.filter(
        TollStation.OpID == tollOpID,
        Pass.tagHomeID == tagOpID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date
    )
    
    result = query.first()
    
    response = {
        "tollOpID": tollOpID,
        "tagOpID": tagOpID,
        "requestTimestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodFrom": start_date.strftime("%Y-%m-%d"),
        "periodTo": end_date.strftime("%Y-%m-%d"),
        "nPasses": result.nPasses if result.nPasses else 0,
        "passesCost": float(result.passesCost) if result.passesCost else 0.0
    }
    return jsonify(response)

# ChargesBy Endpoint
@app.route('/chargesBy/<tollOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def charges_by(current_user, tollOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    query = db.session.query(
        Pass.tagHomeID.label("visitingOpID"),
        func.count(Pass.passID).label("nPasses"),
        func.sum(Pass.charge).label("passesCost")
    ).join(TollStation, Pass.tollID == TollStation.TollID)
    
    query = query.filter(
        TollStation.OpID == tollOpID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date,
        Pass.tagHomeID != tollOpID  # Μόνο άλλοι operators
    ).group_by(Pass.tagHomeID).all()
    
    response = {
        "tollOpID": tollOpID,
        "requestTimestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodFrom": start_date.strftime("%Y-%m-%d"),
        "periodTo": end_date.strftime("%Y-%m-%d"),
        "vOpList": [
            {
                "visitingOpID": row.visitingOpID,
                "nPasses": row.nPasses,
                "passesCost": float(row.passesCost) if row.passesCost else 0.0
            }
            for row in query
        ]
    }
    return jsonify(response)

# Φόρτωση σταθμών διοδίων από CSV κατά την αρχικοποίηση
def load_tollstations_from_csv():
    csv_file = os.path.join(os.path.dirname(__file__), "misc", "tollstations2024.csv")
    print(f"Looking for file at: {csv_file}")
    if not os.path.exists(csv_file):
        print("CSV file not found, skipping station initialization")
        return
    
    with open(csv_file, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            new_station = TollStation(
                TollID=row['TollID'],
                OpID=row['OpID'],
                Operator=row['Operator'],
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

# Δημιουργία πινάκων και αρχικοποίηση admin user
def setup_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', password_hash=generate_password_hash(password='freepasses4all', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin_user)
            db.session.commit()
    
        load_tollstations_from_csv()

if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=9115)
