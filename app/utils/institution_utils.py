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
    def get_people_page_urls_from_department(department: str) -> str:
        return
