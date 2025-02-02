from openai import OpenAI
from backend.app import app
from backend.core.config import Config
from backend.core.script_config import SCHOOLS_TO_SCRAPE
from backend.utils.http_client import HttpClient
from backend.services.scraper.seas_scraper import SEASScraper
from backend.services.scraper.scraper_service import ScraperService
from backend.services.nih.nih_reporter_proxy import NIHReporterProxy
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.embedding.preprocessor import Preprocessor
from backend.services.embedding.embedding_storage import EmbeddingStorage
from backend.services.embedding.embedding_generator import EmbeddingGenerator
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.aggregator.data_aggregator import DataAggregator

# instantiate dependencies
http_client = HttpClient()

seas_scraper = SEASScraper(http_client)
scraper_service = ScraperService([seas_scraper])
nih_service = NIHReporterService(NIHReporterProxy(http_client))
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
preprocessor = Preprocessor()
embedding_storage = EmbeddingStorage()
embedding_generator = EmbeddingGenerator(openai_client)
embedding_service = EmbeddingService(preprocessor, embedding_generator, embedding_storage)
data_aggregator = DataAggregator(scraper_service, nih_service, embedding_service)

if __name__ == '__main__':
    all_faculty = []
    for school in SCHOOLS_TO_SCRAPE:
        all_faculty.extend(data_aggregator.aggregate_school_faculty_data(school))

    with app.app_context():
        from backend.services.database.database_driver import DatabaseDriver
        database_driver = DatabaseDriver()
        database_driver.clear()
        for faculty in all_faculty:
            database_driver.create_faculty(faculty)
