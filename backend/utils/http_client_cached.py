import requests
import requests_cache
import typing
from backend.utils.http_client import HttpClient
import logging
logger = logging.getLogger(__name__)


class HttpClientCached(HttpClient):
    """
    HTTP client with caching capabilities using requests-cache.
    Inherits from HttpClient and adds caching to reduce redundant network calls.
    """

    def __init__(
        self,
        cache_name: str = 'instance/http_cache',
        backend: str = 'sqlite',
        expire_after: int = 30,
        user_agent: str = 'uvarc-dac-foi',
        respect_robots_txt: bool = True,
        **kwargs: typing.Any,
    ):
        """
        Initialize the cached HTTP client.
        :param cache_name: Name of the cache file or database.
        :param backend: Backend for requests-cache (e.g., 'sqlite', 'memory', 'redis').
        :param expire_after: Time in seconds after which cached responses expire.
        :param user_agent: User agent to use when evaluating robots.txt rules.
        :param respect_robots_txt: Whether to block requests disallowed by robots.txt.
        :param kwargs: Additional arguments for the base HttpClient.
        """
        super().__init__(
            user_agent=user_agent,
            respect_robots_txt=respect_robots_txt,
            **kwargs,
        )
        self.session = requests_cache.CachedSession(
            cache_name=cache_name,
            backend=backend,
            expire_after=expire_after,
            allowable_codes=(200,),
        )
        self.session.headers.update({"User-Agent": user_agent})

    def _fetch_robots_txt(
        self,
        robots_url: str,
        headers: typing.Mapping[str, str] | None = None,
    ) -> requests.Response:
        return self.session.get(robots_url, timeout=self.timeout, headers=headers)

    def _send_request(self, method: str, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.session.request(method, url, timeout=self.timeout, **kwargs)

    def _log_response(self, response: requests.Response, url: str) -> None:
        if getattr(response, "from_cache", False):
            logger.info(f"Using cached response for {url}")
        else:
            logger.info(f"Fetched live response for {url}")
