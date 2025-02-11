from openai import OpenAI

def get_openai_client():
    from backend.core.config import Config
    return OpenAI(api_key=Config.OPENAI_API_KEY)

def get_embedding_generator(client: OpenAI):
    from backend.services.embedding.embedding_service import EmbeddingGenerator
    return EmbeddingGenerator(client)

def get_embedding_storage(database_driver: "DatabaseDriver"):
    from backend.services.embedding.embedding_storage import EmbeddingStorage
    return EmbeddingStorage(database_driver)

def get_embedding_service():
    from backend.services.embedding.embedding_service import EmbeddingService
    return EmbeddingService(
        embedding_generator=get_embedding_generator(get_openai_client()),
        embedding_storage=get_embedding_storage(get_database_driver()),
    )

def get_database_driver():
    from backend.services.database.database_driver import DatabaseDriver
    return DatabaseDriver()

def get_search_service():
    from backend.services.search.search_service import SearchService
    embedding_service = get_embedding_service()
    database_driver = embedding_service.embedding_storage.database_driver
    return SearchService(database_driver, embedding_service)