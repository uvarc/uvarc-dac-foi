import typing
from flask import Blueprint, request, jsonify
from backend.models.models import Faculty
from backend.services.search.search_service import SearchService

def create_search_blueprint(search_service: SearchService):
    search_bp = Blueprint('search', __name__)

    @search_bp.route('/', methods=["GET"])
    def search():
        query_text = request.args.get('query', "")
        limit = int(request.args.get('limit', 10))

        results = search_service.search(query_text, limit)

        response = {
            "results": [serialize_faculty(r) for r in results]
        }
        return jsonify(response), 200

    return search_bp

def serialize_faculty(faculty: Faculty) -> typing.Dict:
    """
    Unpack Faculty into JSON
    :param faculty: Faculty
    :return: JSON
    """
    return {
        "name": faculty.name,
        "school": faculty.school,
        "department": faculty.department,
        "about": faculty.about,
        "emails": faculty.email.split(","),
        "profile_url": faculty.profile_url,
        "projects": [
            {
                "project_number": project.project_number,
                "abstract": project.abstract,
                "relevant_terms": project.relevant_terms,
                "start_date": project.start_date,
                "end_date": project.end_date,
                "agency_ic_admin": project.agency_ic_admin,
                "activity_code": project.activity_code,
            }
            for project in faculty.projects
        ]
    }
