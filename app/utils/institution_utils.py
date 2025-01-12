import re
import typing
import logging

from app.core.constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstitutionUtils:
    @staticmethod
    def get_departments_from_school(school: str) -> typing.List[str]:
        try:
            return [dept for dept in SCHOOL_DEPARTMENT_DATA[school]["departments"]]
        except KeyError:
            logger.error(f"No departments found for school: {school}")
            raise

    @staticmethod
    def get_school_from_department(department: str) -> str:
        for school, data in SCHOOL_DEPARTMENT_DATA.items():
            if department in data["departments"]:
                return school
        raise RuntimeError(f"No school found for department: {department}")

    @staticmethod
    def get_school_base_url(school: str) -> str:
        try:
            return SCHOOL_DEPARTMENT_DATA[school]["base_url"]
        except KeyError:
            logger.error(f"No school found for school: {school}")
            raise

    @staticmethod
    def get_people_url_from_department(department: str) -> str:
        try:
            school = InstitutionUtils.get_school_from_department(department)
            return SCHOOL_DEPARTMENT_DATA[school]["departments"][department]["people_url"]
        except KeyError:
            logger.error(f"No people URL found for department: {department}")
            raise

    @staticmethod
    def make_profile_url(base_url: str, profile_endpoint: str) -> str:
        return f"{base_url}{profile_endpoint}"

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return bool(re.match(r"^https?://[^\s/$.?#].[^\s]*$", url))
