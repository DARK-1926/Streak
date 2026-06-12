import os
from flask import Flask
from .routes import bp as routes_bp
from detector import Detector

def create_app():
    """Factory that creates and configures the Flask application."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'), template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    # Minimal secret key for session usage – in prod this should be env‑protected
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

    # Initialise the Detector singleton and store it on the app for easy access
    app.detector = Detector()

    # Register blueprints (UI + API routes)
    app.register_blueprint(routes_bp)

    @app.route('/status')
    def status():
        return {'status': 'ok'}

    return app
