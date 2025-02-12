from flask import Blueprint, request, jsonify
from models.user import User
import io
import csv

getopid_bp = Blueprint("getopid", __name__)

# GetOpID Endpoint
@getopid_bp.route('/api/getOpID/<username>', methods=['GET'])
def getOpID(username):
    format_type = request.args.get("format", "json").lower()
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)

    name = User.query.filter_by(username=username).first()
    if not name:
        data = {"status": "failed", "info": "User not found"}
        if format_type == 'csv':
            writer.writerow(data.keys())
            writer.writerow(data.values())
            return csv_output.getvalue(), 400
        else:
            return jsonify(data), 400
    
    response = {"OpID": f"{name.OpID}"}

    if format_type == 'csv':
        writer.writerow(response.keys())
        writer.writerow(response.values())
        return csv_output.getvalue(), 200
    else:
        return jsonify(response), 200