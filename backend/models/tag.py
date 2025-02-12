from config.db import db

class Tag(db.Model):
    tagRef = db.Column(db.String(50), primary_key=True)
    tagHomeID = db.Column(db.String(10), nullable=False)  
    balance = db.Column(db.Float, nullable=False, default=50.0)
