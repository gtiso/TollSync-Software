from flask import request, jsonify
import jwt as pyjwt
from functools import wraps
from config.settings import Config
from models.user import User

# Middleware για έλεγχο JWT με ρόλους
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-OBSERVATORY-AUTH')  
        if not token:
            return jsonify({"message": "Token is missing!"}), 400
        try:
            data = pyjwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated
