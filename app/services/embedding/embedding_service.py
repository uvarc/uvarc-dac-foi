import typing
import logging
from app.models.models import *
from app.services.embedding.preprocessor import Preprocessor
from app.services.embedding.embedding_generator import EmbeddingGenerator
from app.services.embedding.embedding_storage import EmbeddingStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self,
                 api_key: str = None,
                 index_path: str = None,
                 preprocessor: Preprocessor = None,
                 embedding_generator: EmbeddingGenerator = None,
                 embedding_storage: EmbeddingStorage = None,):
        if api_key is None:
            raise ValueError('api_key is required')
        if index_path is None:
            raise ValueError('index_path is required')
        if preprocessor is None:
            raise ValueError('preprocessor must be defined')
        if embedding_generator is None:
            raise ValueError('embedding_generator must be defined')
        if embedding_storage is None:
            raise ValueError('embedding_storage must be defined')

        self.api_key = api_key
        self.index_path = index_path
        self.preprocessor = preprocessor
        self.embedding_generator = embedding_generator
        self.embedding_storage = embedding_storage

    def generate_and_store_embedding(self, faculty: Faculty, projects: typing.List[Project]) -> int:
        """
        Preprocess, generate, and store the embedding for a faculty member
        :param faculty: Faculty model object containing faculty data
        :param projects: List of Project model objects containing project metadata
        :return: Index of the generated embedding in FAISS
        """
        logging.info(f"Starting embedding generation for faculty: {faculty.name}")
        try:
            text = self.preprocessor.preprocess_faculty_profile(faculty, projects)
            embedding = self.embedding_generator.generate_embedding(text)
            embedding_id = self.embedding_storage.add_embedding(embedding)
            logging.info(f"Embedding generated and stored at index: {embedding_id} for faculty: {faculty.name}")
        except Exception as e:
            logging.error(f"Failed to generate and store embedding for faculty {faculty.name}: {e}")
            raise

    def search_similar_faculty(self, query: str, top_k: int = 5) -> typing.List[int]:
        """
        Search for the most similar faculty based on a natural language query.
        :param query: user input query
        :param top_k: Number of results to return
        :return: List of faculty IDs
        """
        logging.info(f"Searching similar faculty for query: {query}.")
        query_embedding = self.embedding_generator.generate_embedding(query)
        results = self.embedding_storage.search(query_embedding, top_k)
        logging.info(f"Search successful. Found {len(results)} results.")
        return results


