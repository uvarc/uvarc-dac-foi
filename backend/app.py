from flask import current_app
from backend.core import create_app
from backend.utils.factory import get_search_service

app = create_app(
    search_service_instance=get_search_service(current_app)
)

if __name__ == '__main__':
    app.run()