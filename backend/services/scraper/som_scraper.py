import typing
import logging

from app.utils.http_client import HttpClient
from app.utils.institution_utils import InstitutionUtils
from app.services.scraper.base_scraper import BaseScraper
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOMScraper(BaseScraper): 
    SCHOOL_ID = "SOM"
    CONTACT_BLOCK_NAME_XPATH = '//a[contains(@href, "?facbio")]'
    SOM_FACULTY_NAME_XPATH= '//h1[@class="post-title"]/text()'
    EMAIL_XPATH = '//a[starts-with(@href, "mailto:")]/@href'
    ABOUT_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Description")]'
    RESEARCH_INTERESTS_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Interests")]'
    RESEARCH_DISCIPLINES_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Disciplines")]'

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str) -> typing.List[str]:
        """
        Finds all faculty pages listed on a base url and returns in as a list

        Args:
            people_url (str): Base url to find faculty page extensions from 

        Raises:
            ValueError: Invalid URL
            ValueError: The URL is valid, but no URLs matching the XPATH pattern are found

        Returns:
            typing.List[str]: A list containing extensions to the base url to fully specify a faculty page
            e.g. "base.url/`faculty1`" where `faculty1` is what would be returned
        """
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f'Invalid URL: {people_url}')
            raise ValueError("Invalid URL")
        
        profile_urls = []

        try: 
            response = self.http_client.get(people_url) 
            tree = html.fromstring(response.content)
            anchors = tree.xpath(self.CONTACT_BLOCK_NAME_XPATH) # all anchor tags 
            links = [(anchor.get('href'), anchor.text_content()) for anchor in anchors] # tuple of form (url, faculty_name) where faculty_name has to be re-formated
            for href, text in links:
                profile_urls.append(str(href))

        except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {[people_url]}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {people_url}: {e}")
            raise

        if not(profile_urls): # ensure url_list isn't empty if no prior errors were raised
            raise ValueError(f"There were no HTML errors, but no URLs were found. Are you sure `{self.CONTACT_BLOCK_NAME_XPATH}` is the correct XPATH and/or `{people_url}` is correct?")
        return list(dict.fromkeys(profile_urls)) # return list with no duplicates and order maintained since dictionary keys are unique 

    def get_name_from_profile(self, profile_url: str) -> str:
        """
        Returns name in Firstname Lastname format for a given SOM faculty page

        Args:
            profile_url (str): base_url concatenated with specific faculty identifier 

        Raises:
            ValueError: No name for the XPATH tag

        Returns:
            str: The faculty member's name, formatted Firstname Lastname
        """
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise

        try:
            response = self.http_client.get(profile_url) 
            tree = html.fromstring(response.content)
            name = tree.xpath(self.SOM_FACULTY_NAME_XPATH)

            if not name:
                raise ValueError(f"No name found using the XPATH `{self.SOM_FACULTY_NAME_XPATH}` for `{profile_url}`")

            parts = name[0].split(',', maxsplit=1)
            last_name = parts[0]
            first_name = parts[1].strip()  
            
            return f"{first_name} {last_name}" 
        
        except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {profile_url}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise 
    
    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        """
        Returns the email(s) for a faculty member 

        Args:
            profile_url (str): SOM faculty website 

        Raises:
            ValueError: Invalid URL

        Returns:
            typing.List[str]: List of faculty emails as strings
        """
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
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
        """
        String contaning data from `Research Description` and `Research Interests`
        section from SOM website. Research interests are written as sentences, so it
        felt more sensible to include them with the about section.

        Args:
            profile_url (str): SOM faculty website

        Raises:
            ValueError: Invalid URL

        Returns:
            str: String contaning data from `Research Description` and `Research Interests`
            section from SOM website
        """
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            if len(tree) == 0:
                logger.warning(f"No research description section text found for profile: {profile_url}")
                return ""
            else: # research interests are written as sentences, so I decided to append them with the about section 
                research_description = self.extract_text_until_next_section(tree.xpath(self.ABOUT_XPATH)) 
                research_interests = self.extract_text_until_next_section(tree.xpath(self.RESEARCH_INTERESTS_XPATH)) 
                if not research_interests:
                    return research_description
                elif not research_description:
                    return research_interests
                elif not research_interests and not research_description:
                    logger.warning(f"No About section nor research interests found for profile: {profile_url}")
                    return ""
                else:
                    return research_description + "\nResearch Interests: " + research_interests
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise
        
    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        """
        Results from the `Research Discplines` section of a SOM website; somewhat misleading
        since `Research Interests` from the SOM sites are gathered as part of the about secton
        data in the above function

        Args:
            profile_url (str): SOM faculty website

        Raises:
            ValueError: Invalid URL

        Returns:
            typing.List[str]: Comma separated research intersts from SOM website
        """
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_research_disciplines = self.extract_text_until_next_section(tree.xpath(self.RESEARCH_DISCIPLINES_XPATH)) 
            if not raw_research_disciplines:
                logger.warning(f"No research disciplines section text found for profile: {profile_url}")
                return ""
            else:
                research_disciplines = [item.strip() for item in raw_research_disciplines.split(',')]
                return research_disciplines
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def extract_text_until_next_section(self, start_tag) -> str:
        """
        Helper function to go through paragraph breaks in `Research Description`
        and `Research Interests` text on SOM websites, but can be applied to other
        sections if needed.

        Args:
            start_tag (_type_): XPATH tag associated with section of interest

        Returns:
            str:A All text from the section of interest
        """
    # Check if start_tag is None or empty
        if not start_tag:
            return "The specified section could not be found."
        
        # Assume start_tag is a list, and we use the first element
        start_tag = start_tag[0]

        section_text = []
        for element in start_tag.itersiblings():
            # Stop if another <h4> is encountered
            if element.tag == 'h4':
                break
            
            # Include text from <p> tags and their children
            if element.tag == 'p':
                text = ''.join(element.itertext()).strip()
                section_text.append(text if text else "Nothing was found for this section.")
            
            # Include other relevant tags (e.g., <ul>, <ol>, <div>) if necessary
            elif element.tag in ('ul', 'ol', 'div'):
                text = ''.join(element.itertext()).strip()
                if text:
                    section_text.append(text)

        # Join the extracted text
        return "\n".join(section_text)
