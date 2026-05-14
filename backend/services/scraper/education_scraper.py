import typing
import logging
from urllib.parse import urljoin

from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
from backend.services.scraper.base_scraper import BaseScraper
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EducationScraper(BaseScraper):
    SCHOOL_ID = "ED"
    URL_PREFIX = "https://education.virginia.edu/about"
    CONTACT_BLOCK_NAME_XPATH = '//a[starts-with(@href, "/about/directory/")]'
    EDUCATION_FACULTY_NAME_XPATH = "//meta[@property='og:title']/@content"  # Open Graph title meta tag, normally intended for link previews
    RAW_EMAIL_XPATH = '(//*[contains(concat(" ", normalize-space(@class), " "), " __cf_email__ ")])[1]/@data-cfemail'
    EMAIL_XPATH = '//a[starts-with(@href, "mailto:")]/@href'
    BIOGRAPHY_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Interests")]'

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
            response = self.http_client.get(people_url)
            tree = html.fromstring(response.content)
            anchors = tree.xpath(self.CONTACT_BLOCK_NAME_XPATH)  # all anchor tags
            links = [
                (anchor.get("href"), anchor.text_content()) for anchor in anchors
            ]  # tuple of form (url, faculty_name) where faculty_name has to be re-formated
            for href, text in links:
                url = str(href)

                if url.startswith(self.URL_PREFIX):
                    url = url[len(self.URL_PREFIX) :]

                profile_urls.append(url)

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
                f"There were no HTML errors, but no URLs were found. Are you sure `{self.CONTACT_BLOCK_NAME_XPATH}` is the correct XPATH and/or `{people_url}` is correct?"
            )

        profile_urls = [
            urljoin(people_url, rel_url) for rel_url in profile_urls
        ]  # add domain to relative urls to make absolute urls
        return list(set(profile_urls))

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise

        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            name = tree.xpath(self.EDUCATION_FACULTY_NAME_XPATH)

            if not name:
                raise ValueError(
                    f"No name found using the XPATH `{self.EDUCATION_FACULTY_NAME_XPATH}` for `{profile_url}`"
                )

            return name[0].strip()

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
            response.raise_for_status()

            tree = html.fromstring(response.content)
            encoded_email = tree.xpath(self.RAW_EMAIL_XPATH)
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
            tree = html.fromstring(response.content)
            if len(tree) == 0:
                logger.warning(
                    f"No research description section text found for profile: {profile_url}"
                )
                return ""
            else:  # research interests are written as sentences, so I decided to append them with the about section
                research_description = self.extract_text_until_next_section(
                    tree.xpath(self.ABOUT_XPATH)
                )
                research_interests = self.extract_text_until_next_section(
                    tree.xpath(self.RESEARCH_INTERESTS_XPATH)
                )
                if not research_interests:
                    return research_description
                elif not research_description:
                    return research_interests
                elif not research_interests and not research_description:
                    logger.warning(
                        f"No About section nor research interests found for profile: {profile_url}"
                    )
                    return ""
                else:
                    return (
                        research_description
                        + "\nResearch Interests: "
                        + research_interests
                    )
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f"Invalid URL: {profile_url}")
            raise ValueError("Invalid URL")
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_research_disciplines = self.extract_text_until_next_section(
                tree.xpath(self.RESEARCH_DISCIPLINES_XPATH)
            )
            if not raw_research_disciplines:
                logger.warning(
                    f"No research disciplines section text found for profile: {profile_url}"
                )
                return []
            else:
                research_disciplines = [
                    item.strip() for item in raw_research_disciplines.split(",")
                ]
                return research_disciplines
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def extract_text_until_next_section(self, start_tag) -> str:
        # Check if start_tag is None or empty
        if not start_tag:
            return "The specified section could not be found."

        # Assume start_tag is a list, and we use the first element
        start_tag = start_tag[0]

        section_text = []
        for element in start_tag.itersiblings():
            # Stop if another <h4> is encountered
            if element.tag == "h4":
                break

            # Include text from <p> tags and their children
            if element.tag == "p":
                text = "".join(element.itertext()).strip()
                section_text.append(
                    text if text else "Nothing was found for this section."
                )

            # Include other relevant tags (e.g., <ul>, <ol>, <div>) if necessary
            elif element.tag in ("ul", "ol", "div"):
                text = "".join(element.itertext()).strip()
                if text:
                    section_text.append(text)

        # Join the extracted text
        return "\n".join(section_text)


# base_url = "https://education.virginia.edu/about/directory?type=11&department=All&program=All&page=0"

base_url = "https://education.virginia.edu/about/directory?type=11&department=All&program=All&page="  # iterate from 0 to end

education_url = "https://education.virginia.edu/about/directory/"

EDTest = EducationScraper(HttpClient())

# profile_urls = EDTest.get_profile_endpoints_from_people(people_url= base_url)

for i in range(10):
    new_base_url = base_url + str(i)
    profile_urls = EDTest.get_profile_endpoints_from_people(people_url=new_base_url)
    print(profile_urls)
