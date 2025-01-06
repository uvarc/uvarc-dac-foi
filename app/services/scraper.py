from app.utils.constants import SEAS_DEPARTMENT_PEOPLE
from app.utils.http_client import HttpClient

import typing
import logging
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTACT_BLOCK_NAME_A_TAG = '//a[contains(@class, "contact_block_name_link")]/@href'
NO_RESULTS_DIV = '//div[contains(@class, "results_message_inner typography") and contains(text(), "There are no results matching these criteria.")]'

class DepartmentScraper:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def extract_faculty_profile_urls(self, base_url: str) -> typing.List[str]:
        """
        Extracts faculty profile URLs from paginated department people pages.

        Args:
            base_url (str): The base URL of the department's people page.

        Returns:
            list: A list of profile URLs.
        """
        page_number = 0
        profile_urls = []
        MAX_PAGES = 100

        while page_number < MAX_PAGES:
            page_url = f"{base_url}&page={page_number}"
            logger.info(f"Processing page {page_number}: {page_url}")
            try:
                response = self.http_client.request('GET', page_url)
                tree = html.fromstring(response.content)
                no_results = tree.xpath(NO_RESULTS_DIV)
                if no_results:
                    logger.info(f"No results found for page {page_number}: {page_url}")
                    break
                links = tree.xpath(CONTACT_BLOCK_NAME_A_TAG)
                profile_urls.extend(links)
                page_number += 1
            except Exception as e:
                logger.error(f"Error processing page {page_number}: {e}")
                break
        return profile_urls


# http_client = HttpClient()
# scraper = DepartmentScraper(http_client)
# URL = SEAS_DEPARTMENT_PEOPLE['Biomedical Engineering']
# info = scraper.extract_faculty_profile_urls(URL)
# print(info)