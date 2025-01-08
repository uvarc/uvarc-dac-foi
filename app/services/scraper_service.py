import typing
from typing import Tuple
from app.services.scraper import SEASScraper
from app.utils.institution_utils import InstitutionUtils

class FacultyDataService:
    def __init__(self, seas_scraper: SEASScraper):
        self.seas_scraper = seas_scraper

    def get_faculty_name(self, endpoint: str) -> typing.Tuple[str, ...]:
        name = endpoint.split('/')[-1]
        return tuple(name.split('-'))


if __name__ == '__main__':
    from app.utils.http_client import HttpClient
