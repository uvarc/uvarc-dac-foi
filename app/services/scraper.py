import requests
import typing
import logging

from app.utils.http_client import HttpClient
from app.utils.institution_utils import InstitutionUtils
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileScraper:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people_page(self, people_url: str) -> typing.List[str]:
        """
        Extracts faculty profile URLs from paginated department people pages.
        :param people_url: The base URL of the department's people page.
        :return list: A list of profile URLs.
        """

        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f'Invalid URL: {people_url}')
            return []

        page_number = 0
        profile_urls = []
        MAX_PAGES = 100
        NO_RESULTS_DIV = '//div[contains(@class, "results_message_inner typography") and contains(text(), "There are no results matching these criteria.")]'
        CONTACT_BLOCK_NAME_A_TAG = '//a[contains(@class, "contact_block_name_link")]/@href'

        while page_number < MAX_PAGES:
            page_url = f"{people_url}&page={page_number}"
            logger.info(f"Processing page {page_number}: {page_url}")

            if not InstitutionUtils.is_valid_url(page_url):
                logger.error(f'Invalid URL: {page_url}')
                return profile_urls

            try:
                response = self.http_client.request('GET', page_url)
            except Exception:
                return []

            try:
                tree = html.fromstring(response.content)
                no_results = tree.xpath(NO_RESULTS_DIV)
                if no_results:
                    logger.info(f"No results found for page {page_number}: {page_url}")
                    break
                urls = tree.xpath(CONTACT_BLOCK_NAME_A_TAG)
                profile_urls.extend(urls)
                page_number += 1
            except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {page_url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing page {page_number}: {e}")
                break
        return profile_urls

    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        """
        Extracts emails from profile URLs.
        :param profile_url: the URL to the profile page
        :return emails: list of emails contained in the profile page
        """
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            return []

        EMAIL_A_TAG = "//a[contains(@class, 'people_meta_detail_info_link') and starts-with(@href, 'mailto:')]/@href"

        try:
            response = self.http_client.request('GET', profile_url)
        except Exception:
            return []

        try:
            tree = html.fromstring(response.content)
            raw_emails = tree.xpath(EMAIL_A_TAG)
            emails = {email.replace("mailto:", "").strip() for email in raw_emails}
            return list(emails)
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")


# http_client = HttpClient()
# scraper = ProfileScraper(http_client)
# biomed_eng_people_url = InstitutionUtils.get_people_url_from_department("Biomedical Engineering")
# biomed_profile_endpoints = scraper.get_profile_endpoints_from_people_page(biomed_eng_people_url)
# endpoint = biomed_profile_endpoints[0]
# seas_base_url = InstitutionUtils.get_school_base_url("SEAS")
# profile_url = InstitutionUtils.get_profile_url(seas_base_url, endpoint)