import typing
import logging

from app.utils.http_client import HttpClient
from app.utils.institution_utils import InstitutionUtils
from app.services.scraper.base_scraper import BaseScraper
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEASScraper(BaseScraper):
    SCHOOL_ID = "SEAS"
    NO_RESULTS_XPATH = '//div[contains(@class, "results_message_inner typography") and contains(text(), "There are no results matching these criteria.")]'
    CONTACT_BLOCK_NAME_XPATH = '//a[contains(@class, "contact_block_name_link")]/@href'
    EMAIL_XPATH = "//a[contains(@class, 'people_meta_detail_info_link') and starts-with(@href, 'mailto:')]/@href"
    EDUCATION_XPATH = "//h2[text()='Education']"
    ABOUT_AND_EDUCATION_XPATH = "//h2[text()='About']/following-sibling::*[following-sibling::h2[text()='Education']]"
    ABOUT_XPATH = "//h2[text()='About']/following-sibling::*"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str, max_pages: int =100) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f'Invalid URL: {people_url}')
            return []

        page_number = 0
        profile_urls = []

        while page_number < max_pages:
            page_url = f"{people_url}&page={page_number}"
            logger.info(f"Processing page {page_number}: {page_url}")

            try:
                response = self.http_client.request('GET', page_url)
            except Exception:
                return []

            try:
                tree = html.fromstring(response.content)
                no_results = tree.xpath(self.NO_RESULTS_XPATH)
                if no_results:
                    logger.info(f"No results found for page {page_number}: {page_url}")
                    break
                urls = tree.xpath(self.CONTACT_BLOCK_NAME_XPATH)
                profile_urls.extend(urls)
                page_number += 1
            except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {page_url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing page {page_number}: {e}")
                break
        return profile_urls

    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            return []

        try:
            response = self.http_client.request('GET', profile_url)
        except Exception:
            return []

        try:
            tree = html.fromstring(response.content)
            raw_emails = tree.xpath(self.EMAIL_XPATH)
            emails = {email.replace("mailto:", "").strip() for email in raw_emails}
            return list(emails)
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")

    def get_about_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            return "UNKNOWN"

        try:
            response = self.http_client.request('GET', profile_url)
        except Exception:
            return "UNKNOWN"

        try:
            tree = html.fromstring(response.content)
            raw_education = tree.xpath(self.EDUCATION_XPATH)
            if raw_education:
                raw_about = tree.xpath(self.ABOUT_AND_EDUCATION_XPATH)
            else:
                raw_about = tree.xpath(self.ABOUT_XPATH)
            about_content = [element.text_content().strip() for element in raw_about if element.text_content().strip()]
            if about_content:
                logger.info(f"Extract About section text for profile: {profile_url}")
                return "\n".join(about_content)
            else:
                logger.warning(f"No About section text found for profile: {profile_url}")
                return "UNKNOWN"
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
        return "UNKNOWN"

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            return ""
        endpoint = profile_url.split("/")[-1]
        return " ".join(name.capitalize() for name in endpoint.split("-"))


