from backend.core.script_config import SCHOOLS_TO_SCRAPE
from backend.utils.http_client import HttpClient
from backend.utils.factory import get_embedding_service
from backend.services.scraper.seas_scraper import SEASScraper
from backend.services.scraper.scraper_service import ScraperService
from backend.services.nih.nih_reporter_proxy import NIHReporterProxy
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.aggregator.data_aggregator import DataAggregator

# instantiate dependencies
http_client = HttpClient()

seas_scraper = SEASScraper(http_client)
scraper_service = ScraperService([seas_scraper])
nih_service = NIHReporterService(NIHReporterProxy(http_client))
embedding_service = get_embedding_service()

data_aggregator = DataAggregator(scraper_service, nih_service, embedding_service)

if __name__ == '__main__':
    all_faculty = []
    for school in SCHOOLS_TO_SCRAPE:
        all_faculty.extend(data_aggregator.aggregate_school_faculty_data(school))

    database_driver = embedding_service.embedding_storage.database_driver
    database_driver.clear()
    for faculty in all_faculty:
        database_driver.create_faculty(faculty)
