from openai import OpenAI
from backend.core.config import Config
from backend.services.database.database_driver import DatabaseDriver
from backend.services.embedding.embedding_generator import EmbeddingGenerator
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.embedding.embedding_storage import EmbeddingStorage
from backend.services.search.search_service import SearchService

def search_service():
    openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    embedding_storage = EmbeddingStorage()
    embedding_generator = EmbeddingGenerator(openai_client)
    embedding_service = EmbeddingService(embedding_generator, embedding_storage)
    database_driver = DatabaseDriver()
    return SearchService(database_driver, embedding_service)