from flask import Flask
from config.db import db
from config.settings import Config
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.pass_routes import pass_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(pass_bp)
    
    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=9115)