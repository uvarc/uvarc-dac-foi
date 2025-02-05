import typing
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.database.database_driver import DatabaseDriver

class SearchService:
    def __init__(self, database_driver: DatabaseDriver, embedding_service: EmbeddingService):
        self.database_driver = database_driver
        self.embedding_service = embedding_service

    def search(self, query: str, k: int) -> typing.List["Faculty"]:
        """
        Search for the most similar faculty based on a natural language query.
        :param query: user input
        :param k: number of faculties to return
        :return: list of Faculty
        """
        similar_embeddings = self.embedding_service.search_similar_embeddings(query, k)
        similar_faculty = [self._get_faculty_record(id) for id in similar_embeddings]
        return similar_faculty

    def _get_faculty_record(self, id: int) -> "Faculty":
        """
        Get faculty record by embedding id
        :param id: embedding id
        :return: Faculty
        """
        return self.database_driver.get_faculty_by_embedding_id(id)
