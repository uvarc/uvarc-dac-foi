import logging
from app.core import db
from app.models.models import Faculty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseDriver:
    @staticmethod
    def create_faculty(faculty: Faculty):
        """
        Persist a single Faculty object and its associated Projects.
        :param faculty: Faculty object.
        """
        try:
            logger.info(f"Creating faculty record for {faculty.name}.")
            db.session.add(faculty)
            db.session.commit()
            logger.info(f"Faculty record created successfully for {faculty.name}.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create faculty record for {faculty.name}: {e}")
            raise

    @staticmethod
    def get_faculty_by_embedding_id(embedding_id: int) -> Faculty | None:
        """
        Retrieve a single Faculty object by corresponding embedding ID.
        :param embedding_id: ID of the embedding.
        :return: Faculty object or None if not found.
        """
        try:
            faculty = Faculty.query.filter_by(embedding_id=embedding_id).first()
            if faculty:
                logger.info(f"Retrieved faculty record with embedding_id {embedding_id}: {faculty.name}")
            else:
                logger.warning(f"No faculty record found with embedding_id {embedding_id}.")
            return faculty
        except Exception as e:
            logger.error(f"Failed to retrieve faculty record by embedding_id {embedding_id}: {e}")
            raise

    @staticmethod
    def clear():
        """
        Clear database tables.
        """
        try:
            num_deleted = Faculty.query.delete()
            db.session.commit()
            logger.info(f"Deleted {num_deleted} faculty records and their associated projects.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to clear faculty records: {e}")
            raise

