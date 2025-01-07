import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(self, timeout=10, retries=3):
        """
        Initializes the HTTP client facade.
        :param timeout (int): Timeout in seconds for requests.
        :param retries (int): Number of retries for transient errors.
       """
        self.timeout = timeout
        self.retries = retries

    def request(self, method, endpoint):
        """
        Makes an HTTP request with retries.
        :param method (str): HTTP method (GET, POST, etc.).
        :param endpoint (str): API endpoint (relative or absolute URL).
        :return requests.Response: The HTTP response object.
        :raise HTTPError: For non-2xx HTTP responses.
        :raise Timeout: If the request times out.
        :raise RequestException: For other types of request errors.
        """
        url = endpoint if not endpoint.startswith("http") else endpoint

        for attempt in range(self.retries):
            try:
                response = requests.request(method, url)
                response.raise_for_status()
                return response
            except (Timeout, HTTPError) as e:
                logger.warning(f"Attempt {attempt + 1} of {self.retries} failed for {url}: {e}")
                if attempt == self.retries - 1:
                    raise
            except RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                raise
