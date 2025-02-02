import typing
import logging
import pandas as pd

from backend.services.scraper.base_scraper import BaseScraper
from backend.utils.institution_utils import InstitutionUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self, scrapers: typing.List[BaseScraper]):
        self.scrapers = scrapers

    def get_school_faculty_data(self, school: str) -> typing.Dict[str, pd.DataFrame]:
        """
        Fetch school faculty data
        :param school: school acronym
        :return: dictionary mapping school acronym to school faculty data as dataframe
        """
        departments = InstitutionUtils.get_departments_from_school(school)
        logger.info(f"Fetching school faculty data for school: {school}")

        try:
            school_data = {}
            for dept in departments:
                data = self.get_department_faculty_data(dept)
                school_data[dept] = data
            return school_data
        except Exception as e:
            logger.critical(f"Failed to fetch school faculty data for school: {school}: {e}")
            raise RuntimeError(f"Data generation failed for school: {school}") from e



    def get_department_faculty_data(self, department: str) -> pd.DataFrame:
        """
        Returns scraped information about a department's faculty members as a Pandas DataFrame
        :param department: school department e.g. Biomedical Engineering (Dept of SEAS)
        :return: dataframe containing the faculty name, email address, about section, and profile URL
        """
        scraper = self._select_scraper(department)
        people_url = InstitutionUtils.get_people_url_from_department(department)
        school = InstitutionUtils.get_school_from_department(department)
        school_base_url = InstitutionUtils.get_school_base_url(school)

        logger.info(f"Scraping faculty profile endpoints from {department} webpage")
        profile_endpoints = scraper.get_profile_endpoints_from_people(people_url)

        faculty_data = []
        for endpoint in profile_endpoints:
            profile_url = InstitutionUtils.make_profile_url(school_base_url, endpoint)
            name = scraper.get_name_from_profile(profile_url)
            emails = ",".join(scraper.get_emails_from_profile(profile_url))
            about = scraper.get_about_from_profile(profile_url)

            faculty_data.append({
                "Faculty_Name": name,
                "School": school,
                "Department": department,
                "Email_Address": emails,
                "About_Section": about,
                "Profile_URL": profile_url,
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