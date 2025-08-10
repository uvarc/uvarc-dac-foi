import logging
import os
from backend.app import app
from backend.core.populate_config import SCHOOLS_TO_SCRAPE, INDEX_PATH
from backend.services.scraper.som_scraper import SOMScraper
from backend.utils.http_client import HttpClient
from backend.utils.factory import get_embedding_service, get_database_driver
from backend.services.scraper.seas_scraper import SEASScraper
from backend.services.scraper.scraper_service import ScraperService
from backend.services.nih.nih_reporter_proxy import NIHReporterProxy
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.services.nsf.nsf_service import NSFService
from backend.services.aggregator.data_aggregator import DataAggregator

logger = logging.getLogger(__name__)

http_client = HttpClient()

scraper_service = ScraperService([
    SOMScraper(http_client),
    SEASScraper(http_client),
])

nih_service = NIHReporterService(NIHReporterProxy(http_client))
embedding_service = get_embedding_service(app)
database_driver = get_database_driver(app)
nsf_service = NSFService(NSFProxy())

data_aggregator = DataAggregator(scraper_service, nih_service, embedding_service, nsf_service)

if __name__ == '__main__':
    logger.info("Starting populate_db.")
    all_faculty = []

    logger.info("Clearing database.")
    database_driver.clear()

    try:
        for school in SCHOOLS_TO_SCRAPE:
            all_faculty.extend(data_aggregator.aggregate_school_faculty_data(school))

        for faculty in all_faculty:
            database_driver.add_faculty(faculty)

    except Exception as e:
        logger.error(f"Failed to aggregate data: {e}")
        database_driver.clear()
        logger.info("Deleting FAISS index.")
        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)
