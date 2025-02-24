import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from backend.core.extensions import db
from backend.models.models import Faculty
from backend.services.database.database_driver import DatabaseDriver

class TestDatabaseDriver(unittest.TestCase):
    DB_DRIVER_MODULE = "backend.services.database.database_driver.DatabaseDriver"
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.db_driver = DatabaseDriver(self.app)

    def tearDown(self):
        self.app_context.pop()

    def test_add_faculty(self):
        faculty = MagicMock(spec=Faculty)
        faculty.name = "John Doe"

        with patch.object(self.db_driver, "_add_faculty") as mock_add_faculty:
            self.db_driver.add_faculty(faculty)
            mock_add_faculty.assert_called_once_with(faculty)

    def test_get_faculty_by_embedding_id(self):
        faculty = MagicMock(spec=Faculty)
        faculty.name = "John Doe"

        with patch(self.DB_DRIVER_MODULE + "._get_faculty_by_embedding_id", return_value=faculty):
            result = self.db_driver.get_faculty_by_embedding_id(123)
            self.assertEqual(result.name, "John Doe")

    def test_get_embedding_ids_by_search_parameters(self):
        mock_ids = [1, 2, 3]
        with patch(self.DB_DRIVER_MODULE + "._get_embedding_ids_by_search_parameters", return_value=mock_ids):
            result = self.db_driver.get_embedding_ids_by_search_parameters(school="SEAS")
            self.assertEqual(result, mock_ids)