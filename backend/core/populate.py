import logging
import os
from backend.app import app
from backend.core.populate_config import (
    KEEP_EXISTING_SCHOOLS,
    REBUILD_INDEX,
    SCHOOLS_TO_SCRAPE,
    SCHOOL_DEPARTMENT_DATA,
    INDEX_PATH,
)
from backend.services.scraper.darden_scraper import DardenScraper
from backend.services.scraper.som_scraper import SOMScraper
from backend.utils.http_client import HttpClient
from backend.utils.http_client_cached import HttpClientCached
from backend.utils.factory import get_embedding_service, get_database_driver
from backend.services.scraper.seas_scraper import SEASScraper
from backend.services.scraper.batten_scraper import BattenScraper
from backend.services.scraper.scraper_service import ScraperService
from backend.services.nih.nih_reporter_proxy import NIHReporterProxy
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.aggregator.data_aggregator import DataAggregator

logger = logging.getLogger(__name__)

http_client = HttpClientCached()

scraper_service = ScraperService([
    SOMScraper(http_client),
    SEASScraper(http_client),
    BattenScraper(http_client),
    DardenScraper(http_client),
])

nih_service = NIHReporterService(NIHReporterProxy(http_client))
embedding_service = get_embedding_service(app)
database_driver = get_database_driver(app)

data_aggregator = DataAggregator(scraper_service, nih_service, embedding_service)


def delete_faiss_index():
    logger.info("Deleting FAISS index.")
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)
    embedding_service.embedding_storage.index = None


def merge_faculty_records(faculty_dict, faculty):
    faculty_identifier = (faculty.name, faculty.email)

    if faculty_identifier in faculty_dict:
        existing = faculty_dict[faculty_identifier]

        # Merge departments
        existing.department = ",".join(
            sorted(set(existing.department.split(",") + faculty.department.split(","))))

        # Merge schools
        existing.school = ",".join(sorted(set(existing.school.split(",") + faculty.school.split(","))))
    else:
        faculty_dict[faculty_identifier] = faculty


def rebuild_faiss_index():
    logger.info("Rebuilding FAISS index.")
    delete_faiss_index()

    for faculty in database_driver.get_all_faculty():
        embedding_id = embedding_service.generate_and_store_embedding(faculty)
        database_driver.update_faculty_embedding_id(faculty.faculty_id, embedding_id)


def should_rebuild_faiss_index():
    if KEEP_EXISTING_SCHOOLS:
        return REBUILD_INDEX

    if not REBUILD_INDEX:
        logger.info("REBUILD_INDEX=False ignored because KEEP_EXISTING_SCHOOLS=False.")
    return True


if __name__ == '__main__':
    logger.info("Starting populate_db.")
    all_faculty = []
    rebuild_index = should_rebuild_faiss_index()

    if KEEP_EXISTING_SCHOOLS:
        logger.info(f"Keeping existing schools outside scrape list: {SCHOOLS_TO_SCRAPE}.")
        database_driver.delete_faculty_by_schools(SCHOOLS_TO_SCRAPE)
    else:
        logger.info("Clearing database.")
        database_driver.clear()

    if rebuild_index:
        delete_faiss_index()
    else:
        logger.info("Keeping existing FAISS index and appending embeddings for scraped schools.")

    try:
        faculty_dict = dict()

        for school in SCHOOLS_TO_SCRAPE:
            school_config = SCHOOL_DEPARTMENT_DATA.get(school, {})
            add_nih_data = school_config.get("add_nih_data", True)
            school_faculty = data_aggregator.aggregate_school_faculty_data(
                school,
                add_nih_data=add_nih_data,
                generate_embeddings=False,
            )

            for faculty in school_faculty:
                merge_faculty_records(faculty_dict, faculty)

        all_faculty = list(faculty_dict.values())

        if not rebuild_index:
            for faculty in all_faculty:
                faculty.embedding_id = embedding_service.generate_and_store_embedding(faculty)

        for faculty in all_faculty:
            database_driver.add_faculty(faculty)

        if rebuild_index:
            rebuild_faiss_index()

    except Exception as e:
        logger.error(f"Failed to aggregate data: {e}")
        if KEEP_EXISTING_SCHOOLS:
            database_driver.delete_faculty_by_schools(SCHOOLS_TO_SCRAPE)
        else:
            database_driver.clear()
        if rebuild_index:
            delete_faiss_index()
