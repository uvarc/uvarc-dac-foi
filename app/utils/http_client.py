import requests
import logging
from requests.exceptions import RequestException, Timeout, HTTPError

logger = logging.getLogger(__name__)

class HttpClient:
    """
    Initializes the HTTP client facade.

    Args:
        base_url (str): Base URL for the API.
        timeout (int): Timeout in seconds for requests.
        retries (int): Number of retries for transient errors.
    """
    def __init__(self, base_url, timeout=10, retries=3):
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries

    def request(self, method, endpoint):
        """
        Makes an HTTP request with retries.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            endpoint (str): API endpoint (relative or absolute URL).

        Returns:
            requests.Response: The HTTP response object.

        Raises:
            HTTPError: For non-2xx HTTP responses.
            Timeout: If the request times out.
            RequestException: For other types of request errors.
        """
        url = self.base_url + endpoint if not endpoint.startswith("http") else endpoint

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