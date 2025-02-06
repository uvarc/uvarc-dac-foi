from backend.core import create_app  # Import the Flask factory function
from backend.utils.factory import get_database_driver, get_search_service

app = create_app()  # ✅ Use the factory method to ensure db.init_app(app) is called

with app.app_context():
    database_driver = get_database_driver()
    search_service = get_search_service()

    client = app.test_client()
    response = client.get('/api/search/?query=machine+learning&limit=10')
    print("Status Code:", response.status_code)
    response_json = response.get_json()
    names = [
        (result["name"], result["about"], result["department"]) for result in response_json["results"]
    ]
    for (name, about, department) in names:
        print(name + " " + department + "\n" + about)
        print()