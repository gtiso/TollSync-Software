from flask import Blueprint, jsonify, request
from models.passes import Pass
from models.tag import Tag
from models.tollstation import TollStation
from config.db import db
import datetime
from utils.auth import token_required
import io
import csv
from sqlalchemy import text

carpass_bp = Blueprint("carpass", __name__)

@carpass_bp.route('/api/recordPass/<stationID>/<tagRef>/<vehicleType>', methods=['POST'])
@token_required
def record_pass(current_user, stationID, tagRef, vehicleType):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)

    stationExist = TollStation.query.filter_by(TollID=stationID).first()
    tagExist = Tag.query.filter_by(tagRef=tagRef).first()

    if not stationExist or not tagExist:
        data = {"status": "failed", "info": "Toll operator not found"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400

    result = db.session.execute(text(f"SELECT Price{vehicleType} FROM tollsync.toll_station WHERE TollID = '{stationID}'"))
    charge_row = result.fetchone()

    if charge_row:
        charge = charge_row[0]
    else:
        charge = None

    tag = Tag.query.filter_by(tagRef=tagRef).first()
    
    if not tag:
        data = {"status": "failed", "info": "TagRef doesn't exist."}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    if tag.balance < charge:
        data = {"status": "failed", "info": "Insufficient balance."}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 500
        else:
            return jsonify(data), 500

    tag.balance -= charge
    db.session.commit()

    new_pass = Pass(
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        tollID = stationID,
        tagRef = tagRef,
        tagHomeID = tag.tagHomeID,
        charge = charge
    )
    db.session.add(new_pass)
    db.session.commit()

    data = {"status": "OK", "info": "Pass recorded successfully"}
    if format_type == 'csv':
        writer.writerow(data.keys())
        writer.writerow(data.values())
        return csv_output.getvalue(), 200
    else:
        return jsonify(data), 200