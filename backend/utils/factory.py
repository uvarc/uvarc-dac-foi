def get_openai_client():
    from backend.core.config import Config
    from openai import OpenAI
    return OpenAI(api_key=Config.OPENAI_API_KEY)

def get_embedding_generator():
    from backend.services.embedding.embedding_service import EmbeddingGenerator
    return EmbeddingGenerator(get_openai_client())

def get_embedding_storage(app: "Flask"):
    from backend.services.embedding.embedding_storage import EmbeddingStorage
    return EmbeddingStorage(get_database_driver(app))

def get_embedding_service(app: "Flask"):
    from backend.services.embedding.embedding_service import EmbeddingService
    return EmbeddingService(
        embedding_generator=get_embedding_generator(),
        embedding_storage=get_embedding_storage(app),
    )

def get_database_driver(app: "Flask"):
    from backend.services.database.database_driver import DatabaseDriver
    return DatabaseDriver(app)

def get_search_service(app: "Flask"):
    from backend.services.search.search_service import SearchService
    embedding_service = get_embedding_service(app)
    database_driver = embedding_service.embedding_storage.database_driver
    return SearchService(database_driver, embedding_service)