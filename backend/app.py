from flask import Flask
from flask_cors import CORS
from routes.chat import chat_bp
from routes.rag import rag_bp
from config import config
from models.database import init_db
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    CORS(app)  # Enable CORS for all routes

    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(rag_bp, url_prefix='/rag')
    
    # Initialize database
    init_db(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
