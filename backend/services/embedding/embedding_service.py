import typing
import logging
from backend.services.embedding.preprocessor import Preprocessor
from backend.services.embedding.embedding_generator import EmbeddingGenerator
from backend.services.embedding.embedding_storage import EmbeddingStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self,
                 embedding_generator: EmbeddingGenerator = None,
                 embedding_storage: EmbeddingStorage = None):

        if not embedding_generator:
            raise ValueError('embedding_generator must be defined')
        if not embedding_storage:
            raise ValueError('embedding_storage must be defined')

        self.embedding_generator = embedding_generator
        self.embedding_storage = embedding_storage

    def generate_and_store_embedding(self, faculty: "Faculty", projects: typing.List["Project"]) -> int:
        """
        Preprocess, generate, and store the embedding for a faculty member
        :param faculty: Faculty model object containing faculty data
        :param projects: List of Project model objects containing project metadata
        :return: Index of the generated embedding in FAISS
        """
        logging.info(f"Starting embedding generation for faculty: {faculty.name}")
        try:
            text = Preprocessor.preprocess_faculty_profile(faculty, projects)
            embedding = self.embedding_generator.generate_embedding(text)
            embedding_id = self.embedding_storage.add_embedding(faculty.name, embedding)
            logging.info(f"Embedding generated and stored at index: {embedding_id} for faculty: {faculty.name}")

            return embedding_id
        except Exception as e:
            logging.error(f"Failed to generate and store embedding for faculty {faculty.name}: {e}")
            raise

    def search_similar_embeddings(self, query: str, top_k: int = 5) -> typing.List[int]:
        """
        Search for the most similar faculty based on a natural language query.
        :param query: user input query
        :param top_k: Number of results to return
        :return: List of faculty IDs
        """
        logging.info(f"Searching similar faculty for query: {query}.")
        standardized_query = Preprocessor.preprocess_query(query)
        query_embedding = self.embedding_generator.generate_embedding(standardized_query)

        results = [id for id in self.embedding_storage.search_similar_embeddings(query_embedding, top_k) if id != -1]
        len_results = len(results)
        if len_results < top_k:
            logging.warning(f"Only {len_results} result(s) were found.")
        logging.info(f"Search successful.")

        return results