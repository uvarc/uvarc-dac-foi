import logging
import typing
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.database.database_driver import DatabaseDriver

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, database_driver: DatabaseDriver, embedding_service: EmbeddingService):
        self.database_driver = database_driver
        self.embedding_service = embedding_service

    def search(self,
               query: str = None,
               k: int = None,
               school: str = None,
               department: str = None,
               activity_code: str = None,
               agency_ic_admin: str = None,
               has_funding: bool = None) -> typing.List["Faculty"]:
        """
        Search for the most similar faculty based on a natural language query.
        :param query: user natural language query
        :param k: number of faculty profiles to return
        :param school: school name
        :param department: department name
        :param activity_code: activity code
        :param agency_ic_admin: agency ic admin name
        :param has_funding: has funding
        :return: list of Faculty
        """
        similar_embeddings_eids = self.embedding_service.search_similar_embeddings(
            query=query,
            top_k=k,
            school=school,
            department=department,
            activity_code=activity_code,
            agency_ic_admin=agency_ic_admin,
            has_funding=has_funding
        )

        similar_faculty = [self._get_faculty_record(eid) for eid in similar_embeddings_eids]
        similar_faculty_no_nulls = [faculty for faculty in similar_faculty if faculty is not None]
        if len(similar_faculty) > len(similar_faculty_no_nulls):
            missing = len(similar_faculty) - len(similar_faculty_no_nulls)
            logger.warning(f"{missing} embedding ID(s) had no matching faculty record and were excluded from results.")
        return similar_faculty_no_nulls

    def _get_faculty_record(self, eid: int) -> "Faculty":
        """
        Get faculty record by embedding id
        :param eid: embedding id
        :return: Faculty
        """
        return self.database_driver.get_faculty_by_embedding_id(eid)
