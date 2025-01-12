import requests
import logging
import typing
from requests.exceptions import RequestException, Timeout, HTTPError
from app.utils.institution_utils import InstitutionUtils

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(self, timeout: int = 10, retries: int = 3):
        """
        Initializes the HTTP client facade.
        :param timeout (int): Timeout in seconds for requests.
        :param retries (int): Number of retries for transient errors.
        """
        self.timeout = timeout
        self.retries = retries

    def request(self, method: str, url: str, **kwargs: typing.Any) -> requests.Response:
        """
        Makes an HTTP request with retries.
        :param method: HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        :param url: API endpoint (relative or absolute URL).
        :param kwargs: Additional arguments to pass to `requests.request`, such as `json`, `headers`, or `params`.
        :return requests.Response: The HTTP response object.
        :raise HTTPError: For non-2xx HTTP responses.
        :raise Timeout: If the request times out.
        :raise RequestException: For other types of request errors.
        """
        if not InstitutionUtils.is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        for attempt in range(self.retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1}/{self.retries})")
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response
            except (Timeout, HTTPError) as e:
                logger.warning(f"Attempt {attempt + 1} of {self.retries} failed for {url}: {e}")
                if attempt == self.retries - 1:
                    raise
            except RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                raise

    def get(self, url: str, **kwargs: typing.Any) -> requests.Response:
        """
        Convenience method for GET requests.
        :param url: API endpoint.
        :param kwargs: Additional arguments for the GET request.
        :return requests.Response: The HTTP response object.
        """
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs:typing.Any) -> requests.Response:
        """
        Convenience method for POST requests.
        :param url: API endpoint.
        :param kwargs: Additional arguments for the POST request.
        :return requests.Response: The HTTP response object.
        """
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: typing.Any) -> requests.Response:
        """
        Convenience method for PUT requests.
        :param url: API endpoint.
        :param kwargs: Additional arguments for the PUT request.
        :return requests.Response: The HTTP response object.
        """
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: typing.Any) -> requests.Response:
        """
        Convenience method for DELETE requests.
        :param url (str): API endpoint.
        :param kwargs: Additional arguments for the DELETE request.
        :return requests.Response: The HTTP response object.
        """
        return self.request("DELETE", url, **kwargs)
