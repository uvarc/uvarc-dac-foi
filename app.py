from backend.core import create_app
from backend.utils.factory import search_service

search_service_instance = search_service()
app = create_app(search_service_instance=search_service_instance)

if __name__ == '__main__':
    app.run()