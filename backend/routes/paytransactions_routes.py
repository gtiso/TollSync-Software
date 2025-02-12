from flask import Blueprint, request, jsonify
import io
import csv
from dateutil import parser
from models.passes import Pass
from models.tollstation import TollStation
from config.db import db
from sqlalchemy import func
import datetime
from utils.auth import token_required
from sqlalchemy.orm import aliased

transactions_bp = Blueprint("transactions", __name__)

# PayTransactions Endpoint
@transactions_bp.route('/api/payTransactions/<tollOpID>/<tagOpID>/<date_from>/<date_to>', methods=['POST'])
@token_required
def paytransactions(current_user, tollOpID, tagOpID, date_from, date_to):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        data = {"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    station = TollStation.query.filter_by(OpID=tollOpID).first()
    tag = TollStation.query.filter_by(OpID=tagOpID).first()
    if not station or not tag:
        data = {"status": "failed", "info": "Toll operator not found"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    station_alias = aliased(TollStation)

    db.session.query(Pass).filter(
        Pass.tagHomeID == tagOpID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date,
        Pass.paid == 0,
        db.session.query(station_alias.TollID)  # ✅ Ensures JOIN with TollStation
        .filter(station_alias.TollID == Pass.tollID, station_alias.OpID == tollOpID)
        .exists()
    ).update({"paid": 1}, synchronize_session=False)

    data = {"status": "OK", "message": "Passes records updated successfully."}
    if format_type == "csv":
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return csv_output.getvalue(), 200
    else:
        return jsonify(data), 200
    
# GetTransactions Endpoint
@transactions_bp.route('/api/getTransactions/<tollOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def gettransactions(current_user, tollOpID, tagOpID, date_from, date_to):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        data = {"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    station = TollStation.query.filter_by(OpID=tollOpID).first()
    tag = TollStation.query.filter_by(OpID=tagOpID).first()
    if not station or not tag:
        data = {"status": "failed", "info": "Toll operator not found"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    query = db.session.query(
        func.count(Pass.passID).label("nPasses"),
        func.sum(Pass.charge).label("passesCost")
    ).join(TollStation, Pass.tollID == TollStation.TollID)
    
    result = query.filter(
        TollStation.OpID == tollOpID,
        Pass.tagHomeID == tagOpID,
        Pass.timestamp >= start_date,
        Pass.timestamp <= end_date,
        Pass.paid == 0
    ).first()
    
    response = {
        "tollOpID": tollOpID,
        "tagOpID": tagOpID,
        "requestTimestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodFrom": start_date.strftime("%Y-%m-%d"),
        "periodTo": end_date.strftime("%Y-%m-%d"),
        "nPasses": result.nPasses if result.nPasses else 0,
        "passesCost": float(result.passesCost) if result.passesCost else 0.0
    }
    if format_type == "csv":
        writer.writerow(["tollOpID", "tagOpID", "requestTimestamp", "periodFrom", "periodTo", "nPasses","passesCost"])
        writer.writerow([
                response["tollOpID"], response["tagOpID"], response["requestTimestamp"], response["periodFrom"],
                response["periodTo"], response["nPasses"], response["passesCost"]
        ])
        return csv_output.getvalue(), 200
    else:
        return jsonify(response), 200