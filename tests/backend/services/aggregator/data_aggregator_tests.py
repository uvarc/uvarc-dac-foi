import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from backend.services.aggregator.data_aggregator import DataAggregator
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.scraper.scraper_service import ScraperService
from backend.models.models import Faculty, Project

class TestDataAggregator(unittest.TestCase):
    def setUp(self):
        self.scraper_service = MagicMock(spec=ScraperService)
        self.nih_service = MagicMock(spec=NIHReporterService)
        self.embedding_service = MagicMock(spec=EmbeddingService)
        self.aggregator = DataAggregator(self.scraper_service, self.nih_service, self.embedding_service)

    def test_aggregate_school_faculty_data(self):
        mock_faculty_data = {
            "CS": pd.DataFrame([
                {
                    "Faculty_Name": "John Doe",
                    "School": "SEAS",
                    "Email_Address": "johndoe@virginia.edu",
                    "Department": "CS",
                    "About_Section": "About John",
                    "Profile_URL": "https://profile.com"
                 }
            ])
        }

        self.scraper_service.get_school_faculty_data.return_value = mock_faculty_data
        self.nih_service.compile_project_metadata.return_value = pd.DataFrame([
            {
                "project_number": "TEST",
                "abstract_text": "TEST",
                "terms": "TERMS",
                "start_date": date(2020, 1, 1),
                "end_date": date(2020, 2, 2),
                "agency_ic_admin": "TEST",
                "activity_code": "TEST"
            }
        ])
        self.embedding_service.generate_and_store_embedding.return_value = 1
        faculty_list = self.aggregator.aggregate_school_faculty_data("SEAS")

        self.assertEqual(len(faculty_list), 1)
        self.assertEqual(faculty_list[0].name, "John Doe")
        self.assertEqual(faculty_list[0].embedding_id, 1)

    def test_build_faculty_model(self):
        mock_profile = MagicMock(
            Faculty_Name="John Doe",
            School="NONE",
            Department="CS",
            Email_Address="johndoe@testing.edu",
            About_Section="About John",
            Profile_URL="https://profile.com"
        )

        with patch.object(self.aggregator, "_get_projects", return_value=[]):
            faculty = self.aggregator._build_faculty_model(mock_profile)

        self.assertEqual(faculty.name, "John Doe")
        self.assertEqual(faculty.school, "NONE")
        self.assertEqual(faculty.department, "CS")
        self.assertEqual(faculty.email, "johndoe@testing.edu")
        self.assertEqual(faculty.about, "About John")
        self.assertEqual(faculty.profile_url, "https://profile.com")
        self.assertEqual(faculty.has_funding, False)

    def test_get_faculty_projects(self):
        mock_project_df = pd.DataFrame([
            {
                "project_number": "TEST1",
                "abstract_text": "TEST2",
                "terms": "TEST3",
                "start_date": date(2020, 1, 1),
                "end_date": date(2020, 2, 2),
                "agency_ic_admin": "TEST4",
                "activity_code": "TEST5"
            }
        ])

        self.nih_service.compile_project_metadata.return_value = mock_project_df
        projects = self.aggregator._get_projects("John", "Doe")

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].project_number, "TEST1")
        self.assertEqual(projects[0].abstract, "TEST2")


    def test_update_faculty_department(self):
        faculty = Faculty(
            name="John Doe",
            school="SEAS",
            department="Biomedical Engineering",
            about="Info",
            email="email@email.com",
            profile_url="https://profile.com",
            projects=[],
            has_funding=False,
            embedding_id=1
        )

        updated_faculty = self.aggregator._update_faculty_department(faculty, "Chemical Engineering")
        self.assertEqual(updated_faculty.department, "Biomedical Engineering,Chemical Engineering")

    def test_has_funding_true(self):
        projects = [
            Project(
                project_number="TEST1",
                abstract="TEST2",
                relevant_terms="TEST3",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() + timedelta(days=30),
                agency_ic_admin="TEST4",
                activity_code="TEST5"
            )
        ]
        self.assertTrue(self.aggregator._has_funding(projects))

    def test_has_funding_false(self):
        projects = [
            Project(
                project_number="TEST1",
                abstract="TEST2",
                relevant_terms="TEST3",
                start_date=date.today() - timedelta(days=30),
                end_date=date.today() - timedelta(days=5),
                agency_ic_admin="TEST4",
                activity_code="TEST5"
            )
        ]
        self.assertFalse(self.aggregator._has_funding(projects))

    def test_has_funding_missing_date(self):
        projects = [
            Project(
                project_number="TEST1",
                abstract="TEST2",
                relevant_terms="TEST3",
                start_date=None,
                end_date=date.today() - timedelta(days=5),
                agency_ic_admin="TEST4",
                activity_code="TEST5"
            )
        ]
        self.assertFalse(self.aggregator._has_funding(projects))

if __name__ == '__main__':
    unittest.main()