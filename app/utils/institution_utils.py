import re
import typing

from app.core.constants import *

class InstitutionUtils:
    @staticmethod
    def get_departments_from_school(school: str) -> typing.List[str]:
        return [dept for dept in SCHOOL_DEPARTMENT_DATA[school]["departments"]]

    @staticmethod
    def get_school_from_department(department: str) -> str:
        for school, data in SCHOOL_DEPARTMENT_DATA.items():
            if department in data["departments"]:
                return school
        return "UNKNOWN"

    @staticmethod
    def get_school_base_url(school: str) -> str:
        return SCHOOL_DEPARTMENT_DATA[school]["base_url"]

    @staticmethod
    def get_people_url_from_department(department: str) -> str:
        school = InstitutionUtils.get_school_from_department(department)
        return SCHOOL_DEPARTMENT_DATA[school]["departments"][department]["people_url"]

    @staticmethod
    def get_profile_url(base_url: str, profile_endpoint: str) -> str:
        return f"{base_url}{profile_endpoint}"

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return bool(re.match(r"^https?://[^\s/$.?#].[^\s]*$", url))
