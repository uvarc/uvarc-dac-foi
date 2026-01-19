import typing
import logging
from urllib.parse import urljoin

from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
from backend.services.scraper.base_scraper import BaseScraper
from lxml import html

logger = logging.getLogger(__name__)


class BattenScraper(BaseScraper):
    SCHOOL_ID = "BATTEN"
    PROFILE_URL_XPATH = (
        '//a[contains(@class, "title-link") and starts-with(@href, "/people/")]/@href'
    )
    NAME_XPATH = "//meta[@property='og:title']/@content" # selects Open Graph title meta tag, normally intended for link previews
    ENCODED_EMAIL_XPATH = '(//*[contains(concat(" ", normalize-space(@class), " "), " __cf_email__ ")])[1]/@data-cfemail' # selects Cloudflare protected email
    BIO_CONTAINER_XPATH = '//div[contains(@class, "person__field-biography")]'
    RESEARCH_AREAS_XPATH = '//div[contains(@class, "person__field-relfocus")]//div[contains(@class, "field__item")]'

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
            # tree.make_links_absolute(urljoin(people_url, "/")) # change all links from relative to absolute

            # Extract href attributes from anchor tags with the specific class
            relative_urls = tree.xpath(self.PROFILE_URL_XPATH)
            profile_urls = [urljoin(people_url, rel_url) for rel_url in relative_urls]

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
            # Fetch the profile page
            response = self.http_client.get(profile_url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML
            tree = html.fromstring(response.content)

            # Extract the name using the specified XPATH
            name = tree.xpath(self.NAME_XPATH)[0].strip()

            return name

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {[profile_url]}: {e}")
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
            response.raise_for_status()

            tree = html.fromstring(response.content)
            encoded_email = tree.xpath(self.ENCODED_EMAIL_XPATH)
            if encoded_email:
                decoded_email = InstitutionUtils.decode_cloudflare_email(encoded_email[0])
                return [decoded_email]
            else:
                return []
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
            response.encoding = "utf-8"

            tree = html.fromstring(response.text)
            bio_divs = tree.xpath(self.BIO_CONTAINER_XPATH)
            bios = [div.text_content().strip() for div in bio_divs]

            return "\n\n".join(bios)
        
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

        try:
            # Fetch the page
            response = self.http_client.get(profile_url)
            response.raise_for_status()  # Raise an error for bad status codes

            # Parse the HTML
            tree = html.fromstring(response.content)
            
            # Extract research areas using the specified XPATH
            interests_raw = tree.xpath(self.RESEARCH_AREAS_XPATH)
            interests = [interest.text_content().strip() for interest in interests_raw]

            return interests

        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {[profile_url]}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise