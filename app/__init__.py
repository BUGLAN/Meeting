from flask import Flask
from config import BaseConfig
from ext import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    db.init_app(app)

    from .Auth.auth import auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/v1.0')
    from .main.views import main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/api/v1.0')
    from .Auth import auth
    from .main import views

    return app
