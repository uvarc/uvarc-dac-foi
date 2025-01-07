from constants import *

class InstitutionUtils:
    @staticmethod
    def get_school_from_department(department: str) -> str:
        for school, data in SCHOOL_DEPARTMENT_DATA.items():
            if department in data["departments"]:
                return school
        return "UNKNOWN"

    @staticmethod
    def get_school_base_url(school: str) -> str:
        return SCHOOL_DEPARTMENT_DATA[school].get("base_url", "UNKNOWN")

    @staticmethod
    def get_people_url_from_department(department: str) -> str:
        school = InstitutionUtils.get_school_from_department(department)
        return SCHOOL_DEPARTMENT_DATA[school]["departments"][department]["people_url"]

    @staticmethod
    def get_profile_url(base_url: str, profile_endpoint: str) -> str:
        return f"{base_url}/{profile_endpoint}"
