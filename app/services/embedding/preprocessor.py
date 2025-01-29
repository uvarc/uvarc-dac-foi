import typing
import logging
import re
from app.utils.token_utils import count_tokens
from app.core.script_config import OPENAI_CONFIG
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
            f"Abstract: {project.abstract or ''}, Terms: {project.relevant_terms or ''}\n"
            for project in projects
        )

        processed_text = (
            f"Faculty Name: {faculty.name}."
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

    @staticmethod
    def chunk_text(text: str) -> typing.List[str]:
        """
        Split text into chunks that fit within the model's token limit.
        :param text: input text
        :return: list of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            word_length = count_tokens(word)
            if current_length + word_length > OPENAI_CONFIG["MAX_TOKENS"]:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += word_length + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks