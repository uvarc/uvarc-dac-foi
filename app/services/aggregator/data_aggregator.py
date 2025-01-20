import typing
import pandas as pd
from app.services.nih.nih_reporter_service import NIHReporterService
from app.services.scraper.scraper_service import ScraperService
from app.models.models import *


class DataAggregator:
    def __init__(self, scraper_service: ScraperService, nih_service: NIHReporterService):
        self.scraper_service = scraper_service
        self.nih_service = nih_service
        """
        {
            dept1: [
                {
                    "faculty": FacultyObject
                    "projects": [ProjectObject,...,ProjectObject]
                    "embedding_id": int
                },
                {
                ...
                }
            ]
            dept2: [
                ...
            ]
            ...
        }
        :param school: 
        :return: 
        """

    def aggregate_school_faculty_data(self, school: str) -> typing.Dict:
        school_faculty_df = self.scraper_service.get_school_faculty_data(school)
        aggregated_faculty_data = {}
        for dept, dept_faculty_df in school_faculty_df.items():
            aggregated_faculty_data[dept] = []
            for faculty_profile in dept_faculty_df.itertuples():


    @staticmethod
    def convert_to_faculty_model(faculty_profile: typing.Tuple) -> Faculty:
        return Faculty(
            name=faculty_profile.Faculty_Name,
            school=faculty_profile.School,
            department=faculty_profile.Department,
            about=faculty_profile.About_Section,
            email=faculty_profile.Email_Address,
            profile_url=faculty_profile.Profile_URL
        )


from app.utils.http_client import HttpClient
from app.services.nih.nih_reporter_proxy import NIHReporterProxy
from app.services.scraper.seas_scraper import SEASScraper
nih_service = NIHReporterService(NIHReporterProxy(HttpClient()))
scrapers = [
    SEASScraper(HttpClient())
]
scraper_service = ScraperService(scrapers)
aggregator = DataAggregator(scraper_service, nih_service)
dept_faculty_df = scraper_service.get_department_faculty_data("Biomedical Engineering")
for faculty_profile in dept_faculty_df.itertuples():
    faculty_member = convert_to_faculty_model(faculty_profile)