import typing
import logging
from requests import RequestException, Timeout, HTTPError
import requests
from backend.utils.http_client import HttpClient

logger = logging.getLogger(__name__)

class NSFProxy:
    NSF_REPORTER_ENDPOINT = "http://api.nsf.gov/services/v1/awards.json"

    def __init__(self, http_client: HttpClient):
        pass

    def call_nsf_api(self, payload: typing.Dict) -> typing.Dict:
        """
        Call the NSF API with the given payload
        :param payload: the payload for the POST request
        :return: API response as a dictionary
        :raises: Any exceptions raised by the HTTP client
        """
        try:
            logger.info(f"Invoking NSF API with payload: {payload}")
            response = requests.get(self.NSF_REPORTER_ENDPOINT, params=payload)
            response.raise_for_status()
            return response.json()
        except (RequestException, Timeout, HTTPError) as e:
            logger.error(f"NSF API request failed: {e}")
            raise
