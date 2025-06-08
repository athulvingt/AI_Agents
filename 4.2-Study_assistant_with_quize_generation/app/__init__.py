from flask import Flask
from .routes import main
from config import Config
import os

def create_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, '..', 'templates'),
        static_folder=os.path.join(base_dir, '..', 'static')
    )
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.register_blueprint(main)

    return app
