import logging
import re

logger = logging.getLogger(__name__)

class Preprocessor:
    @staticmethod
    def preprocess_faculty_profile(faculty: "Faculty") -> str:
        """
        Preprocess faculty and project(s) data into a single string for embedding
        :param faculty: faculty data
        :return: concatenated data string
        """
        logger.info(f"Preprocessing data for faculty: {faculty.name}")

        project_details = " ".join(
            f"Abstract: {project.abstract or ''}, Terms: {project.relevant_terms or ''}\n"
            for project in faculty.projects
        )

        processed_text = (
            f"Department: {faculty.department}."
            f"School: {faculty.school}."
            f"About: {faculty.about or ''}."
            f"Projects: {project_details}"
        )
        logging.debug(f"Processed text for faculty {faculty.name}: {processed_text}")
        return processed_text

    @staticmethod
    def preprocess_query(query: str) -> str:
        """
        Preprocess query into standardized string for embedding
        :param query: user input
        :return: standardized string
        """
        query = query.lower()
        query = re.sub(r"[^\w\s,.:;?!-]", "", query)
        query = re.sub(r"\s+", " ", query).strip()
        return query

