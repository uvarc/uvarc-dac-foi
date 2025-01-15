import typing
import logging
from requests import RequestException, Timeout, HTTPError
from app.utils.http_client import HttpClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NIHReporterProxy:
    NIH_REPORTER_ENDPOINT = "https://api.reporter.nih.gov/v2/projects/search"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client


    def call_reporter_api(self, payload: typing.Dict) -> typing.Dict:
        """
        Call the NIH RePORTER API with the given payload
        :param payload: the payload for the POST request
        :return: API response as a dictionary
        :raises: Any exceptions raised by the HTTP client
        """
        logger.info(f"Invoking NIH RePORTER API with payload: {payload}")
        try:
            response = self.http_client.post(self.NIH_REPORTER_ENDPOINT, json=payload)
            return response.json()
        except (Timeout, HTTPError, RequestException, ValueError) as e:
            logger.error(f"NIH Reporter API request failed with error:{e}"
                         f"Please verify endpoint correctness: {self.NIH_REPORTER_ENDPOINT}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
