from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend.core.config import Config
from backend.services.search.search_service import SearchService
from backend.utils.factory import search_service
from backend.views.search_view import create_search_blueprint

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config, search_service_instance: SearchService=None):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if not search_service_instance:
        search_service_instance = search_service()

    search_bp = create_search_blueprint(search_service_instance)
    app.register_blueprint(search_bp, url_prefix="/api/search")

    db.init_app(app)
    migrate.init_app(app, db)

    return app