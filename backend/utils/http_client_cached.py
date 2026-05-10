import requests
import requests_cache
import typing
from backend.utils.http_client import HttpClient
from backend.utils.institution_utils import InstitutionUtils
import logging
from requests.exceptions import HTTPError, Timeout, RequestException
logger = logging.getLogger(__name__)


class HttpClientCached(HttpClient):
    """
    HTTP client with caching capabilities using requests-cache.
    Inherits from HttpClient and adds caching to reduce redundant network calls.
    """

    def __init__(self, cache_name: str = 'instance/http_cache', backend: str = 'sqlite', expire_after: int = 30, **kwargs: typing.Any):
        """
        Initialize the cached HTTP client.
        :param cache_name: Name of the cache file or database.
        :param backend: Backend for requests-cache (e.g., 'sqlite', 'memory', 'redis').
        :param expire_after: Time in seconds after which cached responses expire.
        :param kwargs: Additional arguments for the base HttpClient.
        """
        super().__init__(**kwargs)
        self.session = requests_cache.CachedSession(
            cache_name=cache_name,
            backend=backend,
            expire_after=expire_after,
            allowable_codes=(200,),
        )

    def request(self, method: str, url: str, **kwargs: typing.Any) -> requests.Response:
        """
        Make an HTTP request with caching.
        :param method: HTTP method (GET, POST, etc.).
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
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if getattr(response, "from_cache", False):
                    logger.info(f"Using cached response for {url}")
                else:
                    logger.info(f"Fetched live response for {url}")
                response.raise_for_status()
                return response
            except (Timeout, HTTPError) as e:
                logger.warning(f"Attempt {attempt + 1} of {self.retries} failed for {url}: {e}")
                if attempt == self.retries - 1:
                    raise
            except RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                raise