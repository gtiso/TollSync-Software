from config.db import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    @staticmethod
    def create_admin():
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=generate_password_hash('freepasses4all', method='pbkdf2:sha256'), role='admin')
            db.session.add(admin)
            db.session.commit()