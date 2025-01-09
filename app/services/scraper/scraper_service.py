import typing
import logging
import pandas as pd

from app.services.scraper.base_scraper import BaseScraper
from app.utils.institution_utils import InstitutionUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self, scrapers: typing.List[BaseScraper]):
        self.scrapers = scrapers

    def get_department_faculty_data(self, department: str) -> pd.DataFrame:
        """
        Returns scraped information about a department's faculty members as a Pandas DataFrame
        :param department: school department e.g. Biomedical Engineering (Dept of SEAS)
        :return: dataframe containing the faculty name, email address, about section, and SEAS website
        """
        scraper = self._select_scraper(department)
        people_url = InstitutionUtils.get_people_url_from_department(department)
        school = InstitutionUtils.get_school_from_department(department)
        school_base_url = InstitutionUtils.get_school_base_url(school)

        logger.info(f"Extracting faculty profile endpoints from {department} webpage")
        profile_endpoints = scraper.get_profile_endpoints_from_people(people_url)

        faculty_data = []
        for endpoint in profile_endpoints:
            profile_url = InstitutionUtils.get_profile_url(school_base_url, endpoint)
            name = scraper.get_name_from_profile(profile_url) or "UNKNOWN"
            emails = ", ".join(scraper.get_emails_from_profile(profile_url)) or ["UNKNOWN"]
            about = scraper.get_about_from_profile(profile_url) or "UNKNOWN"

            faculty_data.append({
                "Faculty Name": name,
                "Email Address": emails,
                "About Section": about,
                "Profile URL": profile_url,
            })

        return pd.DataFrame(faculty_data)

    def _select_scraper(self, department: str) -> BaseScraper:
        """
        Select scraper based on department
        :param department: UVA school department e.g. Biomedical Engineering
        :return: scraper instance corresponding to given department
        """
        school_id = InstitutionUtils.get_school_from_department(department)
        for scraper in self.scrapers:
            if scraper.SCHOOL_ID == school_id:
                return scraper
        raise ValueError(f"No scraper found for department {department}")

    def _data_not_found(self, obj: typing.Union[str, typing.List]) -> bool:
        if isinstance(obj, str):
            return obj == ""
        if isinstance(obj, list):
            return obj == []
