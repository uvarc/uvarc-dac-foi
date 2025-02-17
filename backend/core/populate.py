import logging
from backend.core.script_config import SCHOOLS_TO_SCRAPE
from backend.services.scraper.som_scraper import SOMScraper
from backend.utils.http_client import HttpClient
from backend.utils.factory import get_embedding_service, get_database_driver
from backend.services.scraper.seas_scraper import SEASScraper
from backend.services.scraper.scraper_service import ScraperService
from backend.services.nih.nih_reporter_proxy import NIHReporterProxy
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.aggregator.data_aggregator import DataAggregator
from app import app

logger = logging.getLogger(__name__)

# instantiate dependencies
http_client = HttpClient()

seas_scraper = SEASScraper(http_client)
som_scraper = SOMScraper(http_client)

scraper_service = ScraperService([
    SOMScraper(http_client),
    SEASScraper(http_client),
])

nih_service = NIHReporterService(NIHReporterProxy(http_client))
embedding_service = get_embedding_service()
database_driver = get_database_driver(app=app)

data_aggregator = DataAggregator(scraper_service, nih_service, embedding_service)

if __name__ == '__main__':
    logger.info("Starting populate_db.")
    all_faculty = []

    logger.info("Clearing database.")
    database_driver.clear()

    for school in SCHOOLS_TO_SCRAPE:
        all_faculty.extend(data_aggregator.aggregate_school_faculty_data(school))

    for faculty in all_faculty:
        database_driver.add_faculty(faculty)
