import typing
import logging

from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
from backend.services.scraper.base_scraper import BaseScraper
from lxml import html

logger = logging.getLogger(__name__)

class SEASScraper(BaseScraper):
    SCHOOL_ID = "SEAS"
    NO_RESULTS_XPATH = '//div[contains(@class, "results_message_inner typography") and contains(text(), "There are no results matching these criteria.")]'
    CONTACT_BLOCK_NAME_XPATH = '//a[contains(@class, "contact_block_name_link")]/@href'
    EMAIL_XPATH = "//a[contains(@class, 'people_meta_detail_info_link') and starts-with(@href, 'mailto:')]/@href"
    EDUCATION_XPATH = "//h2[text()='Education']"
    ABOUT_AND_EDUCATION_XPATH = "//h2[text()='About']/following-sibling::*[following-sibling::h2[text()='Education']]"
    ABOUT_XPATH = "//h2[text()='About']/following-sibling::*"
    RESEARCH_INTERESTS_XPATH = "//h2[normalize-space(text())='Research Interests']/following-sibling::div[@class='directory_grid_items']//div[@class='directory_grid_item']"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str, max_pages: int = 20) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(people_url):
            raise ValueError(f"Invalid URL: {people_url}")

        profile_urls = []
        logger.info(f"Processing page {people_url}")

        try:
            response = self.http_client.get(people_url)
            tree = html.fromstring(response.content)
            urls = tree.xpath(self.CONTACT_BLOCK_NAME_XPATH)
            profile_urls.extend(urls)

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {people_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {people_url}: {e}")
            raise

        return profile_urls

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            raise ValueError(f"Invalid URL: {profile_url}")

        endpoint = profile_url.split("/")[-1]
        return " ".join(name.capitalize() for name in endpoint.split("-"))

    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            raise ValueError(f"Invalid URL: {profile_url}")

        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_emails = tree.xpath(self.EMAIL_XPATH)
            emails = {email.replace("mailto:", "").strip() for email in raw_emails}
            return list(emails)
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def get_about_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            raise ValueError(f"Invalid URL: {profile_url}")

        try:
            response = self.http_client.get(profile_url)
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
                return ""
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            raise ValueError(f"Invalid URL: {profile_url}")

        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_research_interests = tree.xpath(self.RESEARCH_INTERESTS_XPATH)
            research_interests = [element.text_content().strip() for element in raw_research_interests if element.text_content().strip()]
            return research_interests
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise