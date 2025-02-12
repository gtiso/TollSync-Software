from config.db import db

class Pass(db.Model):
    passID = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    timestamp = db.Column(db.DateTime, nullable=False)
    tollID = db.Column(db.String(10), db.ForeignKey('toll_station.TollID'), nullable=False)
    tagRef = db.Column(db.String(50), nullable=False)
    tagHomeID = db.Column(db.String(10), nullable=False)
    charge = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Integer, nullable=False, default=0)