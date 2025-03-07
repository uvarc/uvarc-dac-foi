from flask import Flask
from backend.core.config import Config
from backend.core.extensions import db, migrate
from backend.utils.factory import get_search_service


def create_app(config_class=Config, search_service_instance: "SearchService" = None):
    app = Flask(
        __name__,
        template_folder=Config.TEMPLATES_FOLDER,
        static_folder=Config.STATIC_FOLDER,
    )
    app.config.from_object(config_class)

    search_service_instance = search_service_instance or get_search_service()

    from backend.views.search_view import create_search_blueprint
    search_bp = create_search_blueprint(search_service_instance)
    app.register_blueprint(search_bp, url_prefix="/api")
    from backend.views.search_ui_view import create_search_ui_blueprint
    search_ui_bp = create_search_ui_blueprint()
    app.register_blueprint(search_ui_bp)

    db.init_app(app)
    migrate.init_app(app, db)

    return app