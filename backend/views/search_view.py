import typing
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def create_search_blueprint(search_service: "SearchService"):
    search_bp = Blueprint('search', __name__)

    @search_bp.route("/search", methods=["GET"])
    def search_route():
        """
        API endpoint for faculty search
        """
        return search(search_service)

    return search_bp


def search(search_service: "SearchService"):
    """
    Entry point for faculty search
    :param search_service: SearchService instance
    """
    query = request.args.get("query")
    limit = int(request.args.get("limit"))
    school = request.args.get("school", None)
    department = request.args.get("department", None)
    activity_code = request.args.get("activity_code", None)
    agency_ic_admin = request.args.get("agency_ic_admin", None)

    logging.info(f"Search query: {query}\nLimit: {limit}\nSchool: {school}\nDepartment: {department}\nActivity Code: \
{activity_code}\nAgency IC Admin: {agency_ic_admin}")

    results = search_service.search(
        query=query,
        k=limit,
        school=school,
        department=department,
        activity_code=activity_code,
        agency_ic_admin=agency_ic_admin,
    )

    response = {
        "results": [serialize_faculty(r) for r in results]
    }
    return jsonify(response), 200


def serialize_faculty(faculty: "Faculty") -> typing.Dict:
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
