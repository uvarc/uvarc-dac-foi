import typing
import logging
from app.models.models import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Preprocessor:
    @staticmethod
    def preprocess_faculty_profile(faculty: Faculty, projects: typing.List[Project]) -> str:
        """
        Preprocess faculty and project(s) data into a single string for embedding
        :param faculty: faculty data
        :param projects: project data
        :return: concatenated data string
        """
        logger.info(f"Preprocessing data for faculty: {faculty.name}")

        project_details = " ".join(
            f"Abstract: {project.abstract or ''}, Terms: {project.relevant_terms or ''}."
            for project in projects
        )

        processed_text = (
            f"Faculty Name: {faculty.name}. "
            f"Department: {faculty.department}. "
            f"School: {faculty.school}. "
            f"About: {faculty.about or ''}. "
            f"Projects: {project_details}"
        )
        logging.debug(f"Processed text for faculty {faculty.name}: {processed_text}")
        return processed_text
