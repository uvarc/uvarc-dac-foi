import logging
from flask import Flask
from backend.core.extensions import db
from backend.models.models import Faculty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseDriver:
    def __init__(self, app: Flask = None):
        """
        Optionally initialize with a Flask app instance for use in app contexts.
        :param app: Flask application instance
        """
        self.app = app

    def create_faculty(self, faculty: Faculty):
        """
        Persist a single Faculty object and its associated Projects.
        :param faculty: Faculty object.
        """
        try:
            if self.app:
                with self.app.app_context():
                    self._add_faculty(faculty)
            else:
                self._add_faculty(faculty)
        except Exception as e:
            logger.error(f"Failed to create faculty record for {faculty.name}: {e}")
            raise

    @staticmethod
    def _add_faculty(faculty: Faculty):
        """Helper function to add faculty to the database."""
        logger.info(f"Creating faculty record for {faculty.name}.")
        db.session.add(faculty)
        db.session.commit()
        logger.info(f"Faculty record created successfully for {faculty.name}.")
        db.session.remove()

    def get_faculty_by_embedding_id(self, embedding_id: int) -> Faculty | None:
        """
        Retrieve a single Faculty object by corresponding embedding ID.
        :param embedding_id: ID of the embedding.
        :return: Faculty object or None if not found.
        """
        try:
            if self.app:
                with self.app.app_context():
                    return self._query_faculty(embedding_id)
            return self._query_faculty(embedding_id)
        except Exception as e:
            logger.error(f"Failed to retrieve faculty record by embedding_id {embedding_id}: {e}")
            raise

    @staticmethod
    def _query_faculty(embedding_id: int):
        """Helper function to query faculty by embedding ID."""
        faculty = Faculty.query.filter_by(embedding_id=embedding_id).first()
        if faculty:
            logger.info(f"Retrieved faculty record with embedding_id {embedding_id}: {faculty.name}")
        else:
            logger.warning(f"No faculty record found with embedding_id {embedding_id}.")
        return faculty

    def clear(self):
        """
        Clear database tables.
        """
        try:
            if self.app:
                with self.app.app_context():
                    self._clear_db()
            else:
                self._clear_db()
        except Exception as e:
            logger.error(f"Failed to clear faculty records: {e}")
            raise

    @staticmethod
    def _clear_db():
        """Helper function to clear faculty records."""
        num_deleted = Faculty.query.delete()
        db.session.commit()
        logger.info(f"Deleted {num_deleted} faculty records and their associated projects.")
        db.session.remove()
