import typing
import logging
from urllib.parse import urljoin

from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
from backend.services.scraper.base_scraper import BaseScraper
from lxml import html

logger = logging.getLogger(__name__)


class NursingScraper(BaseScraper):
    SCHOOL_ID = "NURSING"
    EMAIL_XPATH = "//a[contains(@href, 'mailto:')]/@href"
    PROFILE_URL_XPATH = '//a[@class="custom-contact-card-anchor"]/@href'
    RAW_NAME_XPATH = "//title/text()"
    RAW_EMAIL_XPATH = '//a[starts-with(@href, "mailto:")]/@href'
    BIO_CONTAINER_XPATH = '//div[contains(@class, "field--body--biography")]'
    RESEARCH_AREAS_XPATH = (
        lambda self, profile_url: f"""//div[contains(@class,"text_block")]
    [.//a[@href="{profile_url}"]]
    //div[contains(@class,"custom-contact-card-title2")]/text()"""
    )
    PEOPLE_URL = None

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(
        self, people_url: str, max_pages: int = 0
    ) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f"Invalid URL: {people_url}")
            raise ValueError("Invalid URL")

        profile_urls = []

        try:
            # Fetch the page
            response = self.http_client.get(people_url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML
            tree = html.fromstring(response.content)

            # Extract href attributes from anchor tags with the specific class
            profile_urls = tree.xpath(self.PROFILE_URL_XPATH)

            self.PEOPLE_URL = people_url

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {[people_url]}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {people_url}: {e}")
            raise

        if (
            not profile_urls
        ):  # ensure url_list isn't empty if no prior errors were raised
            raise ValueError(
                f"There were no HTML errors, but no URLs were found. Are you sure `{self.PROFILE_URL_XPATH}` is the correct XPATH and/or `{people_url}` is correct?"
            )

        return list(set(profile_urls))

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")

        try:
            response = self.http_client.get(profile_url)
            response.raise_for_status()

            tree = html.fromstring(response.content)
            # original name format: Lastname, Firstname • University of Virginia School of Nursing
            # convert to Firstname Lastname
            raw_name = tree.xpath(self.RAW_NAME_XPATH)[0]
            name_part = raw_name.split("•")[0].strip()
            last_name, first_name = [part.strip() for part in name_part.split(",")]
            formatted_name = f"{first_name} {last_name}"
            if not formatted_name or formatted_name.isspace():
                raise ValueError(
                    f"Name could not be extracted from profile URL: {profile_url}"
                )
            return formatted_name

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_emails = tree.xpath(self.RAW_EMAIL_XPATH)
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
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")

        try:
            response = self.http_client.get(profile_url)
            response.raise_for_status()

            tree = html.fromstring(response.content)
            bio_container = tree.xpath(
                '//div[contains(@class, "field--body--biography")]'
            )[0]

            # Extract text only from elements before the first <ul>
            bio_text_parts = []
            for element in bio_container:
                if element.tag == "ul":
                    break
                # Get text content from paragraphs or other tags
                text = element.text_content().strip()
                if text:
                    bio_text_parts.append(text)

            return "\n\n".join(bio_text_parts)

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")

        if self.PEOPLE_URL is None:
            logger.error(
                "PEOPLE_URL is not set. Please call get_profile_endpoints_from_people first."
            )
            raise ValueError("PEOPLE_URL is not set.")

        try:
            # Fetch the page
            response = self.http_client.get(self.PEOPLE_URL)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML
            tree = html.fromstring(response.content)
            tree.make_links_absolute(urljoin(self.PEOPLE_URL, "/"))
            research_areas_raw: str = tree.xpath(self.RESEARCH_AREAS_XPATH(profile_url))[0]
            research_areas = (
                research_areas_raw.replace("RESEARCH AREAS:", "").strip().split(", ")
            )
            return research_areas
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {[self.PEOPLE_URL]}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {self.PEOPLE_URL}: {e}")
            raise
