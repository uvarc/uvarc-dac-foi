from flask import Blueprint, render_template

def create_search_ui_blueprint():
    search_ui_bp = Blueprint('search_ui', __name__)

    @search_ui_bp.route("/")
    def search_ui():
        return render_template("search.html")

    return search_ui_bp