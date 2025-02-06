import os
from flask import Blueprint, render_template
from backend.core.config import Config

search_template = os.path.join(Config.TEMPLATES_FOLDER, "search.html")

def create_search_ui_blueprint():
    search_ui_bp = Blueprint('search_ui', __name__)

    @search_ui_bp.route("/")
    def search_ui():
        return render_template(search_template)

    return search_ui_bp