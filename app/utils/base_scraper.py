import typing
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def get_profile_endpoints_from_people(self, people_url: str, max_pages: int=100) -> typing.List[str]:
        """
        Extracts faculty profile URLs from paginated department people pages.
        :param people_url: The base URL of the department's people page.
        :param max_pages: The maximum number of pages requested before timeout
        :return list: A list of profile URLs.
        """
        pass

    @abstractmethod
    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        """
        Extracts emails from profile URLs.
        :param profile_url: the URL to the profile page
        :return emails: list of emails contained in the profile page
        """
        pass

    @abstractmethod
    def get_about_from_profile(self, profile_url: str) -> typing.List[str]:
        """
        Extracts about from profile URLs.
        :param profile_url: the URL to the profile page
        :return: About Section text for profile
        """
        pass

    @abstractmethod
    def get_name_from_profile(self, profile_url: str) -> str:
        """
        Extracts name from profile URLs.
        :param profile_url: profile URL
        :return: faculty name string
        """
        pass