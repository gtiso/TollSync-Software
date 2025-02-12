from config.db import db
from datetime import datetime

class Transaction(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OpID = db.Column(db.Integer, db.ForeignKey("tollstation.OpID"), nullable=False)
    OpID = db.Column(db.Integer, db.ForeignKey("tollstation.OpID"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, from_company_id, to_company_id, amount):
        self.from_company_id = from_company_id
        self.to_company_id = to_company_id
        self.amount = amount
