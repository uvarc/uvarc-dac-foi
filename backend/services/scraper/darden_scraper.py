import typing
import logging
from urllib.parse import urljoin

from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
from backend.services.scraper.base_scraper import BaseScraper
from lxml import html

logger = logging.getLogger(__name__)

class DardenScraper(BaseScraper):
    SCHOOL_ID = "DARDEN"
    PROFILE_URL_XPATH = "//a[contains(@class, 'faculty-directory-avatar')]/@href"
    NAME_XPATH = "//title/text()"
    ENCODED_EMAIL_XPATH = '(//*[contains(concat(" ", normalize-space(@class), " "), " __cf_email__ ")])[1]/@data-cfemail' # selects first Cloudflare protected email on page
    BIO_CONTAINER_XPATH = '//div[contains(@class, "field--name-field-text-introduction")]'
    RESEARCH_AREAS_XPATH = '//div[contains(@class, "field--name-field-areas-of-expertise")]'
    
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        
    def get_profile_endpoints_from_people(self, people_url: str, max_pages: int = 9) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f"Invalid URL: {people_url}")
            raise ValueError("Invalid URL")

        profile_urls = []

        try:
            if max_pages < 1:
                raise ValueError("max_pages must be at least 1")
            
            for page in range(max_pages):
                paged_url = f"{people_url}?page={page+1}"
                
                # Fetch the page
                response = self.http_client.get(paged_url)
                response.raise_for_status()  # Raise an error for bad status codes
                
                # Parse the HTML
                tree = html.fromstring(response.content)
                relative_urls = tree.xpath(self.PROFILE_URL_XPATH)
                profile_urls.extend([urljoin(people_url, rel_url) for rel_url in relative_urls])
                
            if not profile_urls:
                raise ValueError(
                    f"There were no HTML errors, but no URLs were found. Are you sure `{self.PROFILE_URL_XPATH}` is the correct XPATH and/or `{people_url}` is correct?"
                )
            
            return profile_urls
        
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {[people_url]}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error processing page {people_url}: {e}")
            raise
        
        
    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")

        try:
            # Fetch the profile page
            response = self.http_client.get(profile_url)
            response.raise_for_status()  # Raise an error for bad status codes
            
            logger.info(f"Parsing name from {profile_url}")
            
            # Parse the HTML
            tree = html.fromstring(response.content)

            # Extract the name using the specified XPATH (get text before pipe character)
            logger.debug(f"Extracted name: {tree.xpath(self.NAME_XPATH)}")
            name = tree.xpath(self.NAME_XPATH)[0].split('|')[0].strip()

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
            
            # Target the container with all paragraphs, including the Education one
            bio_div = tree.xpath(self.BIO_CONTAINER_XPATH)[0]

            # Get all <p> elements inside that div, excluding paragraphs with <strong>education</strong> (case-insensitive)
            bio_paragraphs = bio_div.xpath('./p[not(.//strong[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "education")])]')
            bio_paragraphs = [p.text_content().strip() for p in bio_paragraphs]
            return "\n\n".join(bio_paragraphs)
        
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
            response = self.http_client.get(profile_url)
            response.raise_for_status()
            response.encoding = "utf-8"

            tree = html.fromstring(response.text)
            research_divs = tree.xpath(self.RESEARCH_AREAS_XPATH)
            interests = [div.text_content().strip() for div in research_divs]

            return interests
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise