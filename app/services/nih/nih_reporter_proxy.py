import typing
import logging
import copy
from requests import RequestException, Timeout, HTTPError
from app.utils.http_client import HttpClient
from app.core.constants import NIH_REPORTER_PAYLOAD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NIHReporterProxy:
    NIH_REPORTER_ENDPOINT = "https://api.reporter.nih.gov/v2/projects/search"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    @staticmethod
    def build_payload(first_name: str, last_name: str, fiscal_years: typing.List) -> typing.Dict:
        """
        Build the payload for the NIH RePORTER API request
        :param first_name: PI's first name
        :param last_name: PI's last name
        :param fiscal_years: list of fiscal years to filter results
        :return: payload as dictionary
        """
        payload = copy.deepcopy(NIH_REPORTER_PAYLOAD)
        payload["criteria"]["pi_names"][0]["first_name"] = first_name
        payload["criteria"]["pi_names"][0]["last_name"] = last_name
        payload["criteria"]["fiscal_years"] = fiscal_years
        return payload

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
