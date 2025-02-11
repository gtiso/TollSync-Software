from config.db import db

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