from flask import Blueprint, jsonify, request
from models.passes import Pass
import datetime
from utils.auth import token_required
from sqlalchemy import func
from dateutil import parser
from models.passes import Pass
from models.tollstation import TollStation
from config.db import db

pass_bp = Blueprint("pass", __name__)

# TollStationPasses Endpoint
@pass_bp.route('/api/tollStationPasses/<tollStationID>/<date_from>/<date_to>', methods=['GET'])
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
@pass_bp.route('/api/passAnalysis/<stationOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def pass_analysis(current_user, stationOpID, tagOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    station = TollStation.query.filter_by(OpID=stationOpID).first()
    tag = TollStation.query.filter_by(OpID=tagOpID).first()
    if not station or not tag:
        return jsonify({"status": "failed", "info": "Toll operator not found"}), 400
    
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
@pass_bp.route('/api/passesCost/<tollOpID>/<tagOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def passes_cost(current_user, tollOpID, tagOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400
    
    station = TollStation.query.filter_by(OpID=tollOpID).first()
    tag = TollStation.query.filter_by(OpID=tagOpID).first()
    if not station or not tag:
        return jsonify({"status": "failed", "info": "Toll operator not found"}), 400
    
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
@pass_bp.route('/api/chargesBy/<tollOpID>/<date_from>/<date_to>', methods=['GET'])
@token_required
def charges_by(current_user, tollOpID, date_from, date_to):
    start_date = parser.parse(date_from)
    end_date = parser.parse(date_to)
    
    if not start_date or not end_date:
        return jsonify({"status": "failed", "info": "Invalid date format. Use YYYYMMDD"}), 400

    station = TollStation.query.filter_by(OpID=tollOpID).first()
    if not station:
        return jsonify({"status": "failed", "info": "Toll operator not found"}), 400
    
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