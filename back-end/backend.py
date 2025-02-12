import os
import csv
from models.tollstation import TollStation
from models.user import User
from flask import Flask
from config.db import db
from config.settings import Config
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.pass_routes import pass_bp
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pass_bp)
    
    return app

def load_tollstations_from_csv():
    csv_file = os.path.join(os.path.dirname(__file__), "misc", "tollstations2024.csv")
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

def create_admin(name, password):
        if not User.query.filter_by(username=name).first():
            admin = User(username=name, password_hash=generate_password_hash(password, method='pbkdf2:sha256'), role='admin')
            db.session.add(admin)
            db.session.commit()
            
def create_user(name, password):
        if not User.query.filter_by(username=name).first():
            user = User(username=name, password_hash=generate_password_hash(password, method='pbkdf2:sha256'), role='user')
            db.session.add(user)
            db.session.commit()

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        load_tollstations_from_csv()
        create_admin('admin', 'freepasses4all')
        create_user('customercare@aegeanmotorway.gr','toll')
        create_user('eoae@egnatia.gr','toll')
        create_user('info@gefyra.gr','toll')
        create_user('customercare@kentrikiodos.gr','toll')
        create_user('info@moreas.com.gr','toll')
        create_user('customercare@attikesdiadromes.gr','toll')
        create_user('info@neaodos.gr','toll')
        create_user('customercare@olympiaoperation.gr','toll')
    app.run(debug=True, port=9115)