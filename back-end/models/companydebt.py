from config.db import db

class CompanyDebt(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OpID = db.Column(db.Integer, db.ForeignKey("tollstation.OpID"), nullable=False)
    OpID = db.Column(db.Integer, db.ForeignKey("tollstation.OpID"), nullable=False)
    amount_owed = db.Column(db.Float, nullable=False, default=0.0)

    def __init__(self, debtor_company_id, creditor_company_id, amount_owed):
        self.debtor_company_id = debtor_company_id
        self.creditor_company_id = creditor_company_id
        self.amount_owed = amount_owed
