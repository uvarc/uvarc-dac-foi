import typing
import logging
import pandas as pd

from app.services.scraper import BaseScraper
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
        faculty_names = []
        faculty_emails = []
        faculty_about = []
        faculty_profile_urls = []

        for endpoint in profile_endpoints:
            profile_url = InstitutionUtils.get_profile_url(school_base_url, endpoint)
            faculty_profile_urls.append(profile_url)

            name = scraper.get_name_from_profile(profile_url)
            if self._data_not_found(name):
                logger.warning(f"Name not found for URL: {profile_url}")
                name = "UNKNOWN"
            faculty_names.append(name)

            emails = scraper.get_emails_from_profile(profile_url)
            if self._data_not_found(emails):
                logger.warning(f"Email not found for URL: {profile_url}")
                emails = ["UNKNOWN"]
            faculty_emails.append(emails)

            about = scraper.get_about_from_profile(profile_url)
            if self._data_not_found(about):
                logger.warning(f"About not found for URL: {profile_url}")
                about = "UNKNOWN"
            faculty_about.append(about)

        faculty_data = {
            "Faculty Name": faculty_names,
            "About Section": faculty_about,
            "Email Address": faculty_emails,
            "Profile URL": faculty_profile_urls,
        }
        return pd.DataFrame(faculty_data)

    def _select_scraper(self, department: str) -> BaseScraper:
        """
        Select scraper based on department
        :param department: UVA school department e.g. Biomedical Engineering
        :return: scraper instance corresponding to given department
        """
        school_id = InstitutionUtils.get_school_from_department(department)
        return next(scraper for scraper in self.scrapers if scraper.SCHOOL_ID == school_id)

    def _data_not_found(self, object: typing.Any) -> bool:
        if isinstance(object, str):
            return object == ""
        if isinstance(object, list):
            return object == []


if __name__ == '__main__':
    from app.utils.http_client import HttpClient
    from app.utils.institution_utils import InstitutionUtils
    from app.services.scraper import SEASScraper

    seas_scraper = SEASScraper(HttpClient())
    scrapers = [seas_scraper]
    service = ScraperService(scrapers)
    print(service.get_department_info('Biomedical Engineering'))
