import logging
import typing
from sqlalchemy import delete, or_
from contextlib import contextmanager
from sqlalchemy.orm import joinedload

from backend.core.extensions import db

logger = logging.getLogger(__name__)

class DatabaseDriver:
    def __init__(self, app):
        self.app = app

    @contextmanager
    def _app_context(self):
        """
        Context manager to handle app context transparently.
        """
        if self.app:
            with self.app.app_context():
                yield
        else:
            yield

    def add_faculty(self, faculty: "Faculty"):
        """
        Persist a single Faculty object and its associated Projects.
        :param faculty: Faculty object.
        """
        try:
            with self._app_context():
                self._add_faculty(faculty)
        except Exception as e:
            logger.error(f"Failed to create faculty record for {faculty.name}: {e}", exc_info=True)
            raise

    @staticmethod
    def _add_faculty(faculty: "Faculty"):
        """Helper function to add faculty to the database."""
        logger.info(f"Creating faculty record for {faculty.name}.")
        db.session.add(faculty)
        db.session.commit()
        logger.info(f"Faculty record created successfully for {faculty.name}.")

    def get_faculty_by_embedding_id(self, embedding_id: int) -> "Faculty":
        """
        Retrieve a single Faculty object by corresponding embedding ID.
        :param embedding_id: ID of the embedding.
        :return: Faculty object or None if not found.
        """
        try:
            with self.app.app_context():
                return self._get_faculty_by_embedding_id(embedding_id)
        except Exception as e:
            logger.error(f"Failed to retrieve faculty record by embedding_id {embedding_id}: {e}")
            raise

    @staticmethod
    def _get_faculty_by_embedding_id(embedding_id: int):
        """Helper function to query faculty by embedding ID."""
        from backend.models.models import Faculty
        faculty = Faculty.query.options(joinedload(Faculty.projects)).filter_by(embedding_id=embedding_id).first()
        if faculty:
            logger.info(f"Retrieved faculty record with embedding_id {embedding_id}: {faculty.name}")
        else:
            logger.warning(f"No faculty record found with embedding_id {embedding_id}.")
        return faculty

    def get_embedding_ids_by_search_parameters(self, **parameters) -> typing.List[int]:
        """
        Get Faculty embedding IDs that satisfy search parameters.
        :param school: School name
        :param department: Department name
        :param activity_code: Activity code
        :param agency_ic_admin: Agency IC admin
        :return: List of Faculty embedding IDs
        """
        try:
            with self.app.app_context():
                return self._get_embedding_ids_by_search_parameters(**parameters)
        except Exception as e:
            logger.error(f"Failed to retrieve faculty record by filters: {e}")
            raise

    @staticmethod
    def _get_embedding_ids_by_search_parameters(school=None,
                                                department=None,
                                                activity_code=None,
                                                agency_ic_admin=None,
                                                has_funding=None) -> typing.List[int]:
        """Helper function to query faculty by embedding IDs."""
        from backend.models.models import Faculty, Project
        query = db.session.query(Faculty.embedding_id).outerjoin(Project)

        if school:
            query = query.filter(Faculty.school == school)
        if department:
            query = query.filter(Faculty.department.contains(department))
        if activity_code:
            query = query.filter(Project.activity_code == activity_code)
        if agency_ic_admin:
            query = query.filter(Project.agency_ic_admin == agency_ic_admin)
        if has_funding:
            query = query.filter(Faculty.has_funding == has_funding)

        return [record.embedding_id for record in query.distinct().all()]

    def search_exact_words(self, query: str, top_k: int, 
                           school: str = None,
                           department: str = None,
                           activity_code: str = None,
                           agency_ic_admin: str = None,
                           has_funding: bool = None) -> typing.List[int]:
        """
        Search for faculty with exact words in their profiles.
        :param query: Exact words to search for
        :param top_k: Number of results to return
        :param school: School name
        :param department: Department name
        :param activity_code: Activity code
        :param agency_ic_admin: Agency IC admin name
        :param has_funding: Faculty has funding
        :return: List of faculty EIDs
        """
        try:
            with self.app.app_context():
                return self._search_exact_words(query, top_k, school, department, activity_code, agency_ic_admin, has_funding)
                
        except Exception as e:
            logger.error(f"Failed to search exact words '{query}': {e}")
            raise
    
    @staticmethod
    def _search_exact_words(query: str, top_k: int,
                            school: str = None,
                            department: str = None,
                            activity_code: str = None,
                            agency_ic_admin: str = None,
                            has_funding: bool = None) -> typing.List[int]:
        """Helper function to search for exact words in faculty profiles."""
        from backend.models.models import Faculty, Project
        faculty_query = db.session.query(Faculty.embedding_id).outerjoin(Faculty.projects).filter(
            or_(
            Faculty.about.ilike(f"%{query}%"),
            Project.abstract.ilike(f"%{query}%"),
            Project.relevant_terms.ilike(f"%{query}%")
            )
        )
        if school:
            faculty_query = faculty_query.filter(Faculty.school == school)
        if department:
            faculty_query = faculty_query.filter(Faculty.department.contains(department))
        if activity_code:
            faculty_query = faculty_query.filter(Faculty.projects.any(Project.activity_code == activity_code))
        if agency_ic_admin:
            faculty_query = faculty_query.filter(Faculty.projects.any(Project.agency_ic_admin == agency_ic_admin))
        if has_funding is not None:
            faculty_query = faculty_query.filter(Faculty.has_funding == has_funding)
        return [record.embedding_id for record in faculty_query.distinct().limit(top_k).all()]
        

    def clear(self):
        """
        Clear database tables.
        """
        try:
            with self.app.app_context():
                self._clear_db()
        except Exception as e:
            logger.error(f"Failed to clear faculty records: {e}")
            raise

    @staticmethod
    def _clear_db():
        """Helper function to clear faculty records."""
        from backend.models.models import Faculty
        db.session.execute(delete(Faculty))
        db.session.commit()
        logger.info("All faculty records deleted.")
