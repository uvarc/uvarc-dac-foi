import requests
import logging
import typing
import urllib.parse
import urllib.robotparser
from requests.exceptions import RequestException, Timeout, HTTPError
from backend.utils.institution_utils import InstitutionUtils

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(
        self,
        timeout: int = 10,
        retries: int = 3,
        user_agent: str = 'uvarc-dac-foi',
        respect_robots_txt: bool = True,
    ):
        """
        Initializes the HTTP client facade.
        :param timeout (int): Timeout in seconds for requests.
        :param retries (int): Number of retries for transient errors.
        :param user_agent: User agent to use when evaluating robots.txt rules.
        :param respect_robots_txt: Whether to block requests disallowed by robots.txt.
        """
        self.timeout = timeout
        self.retries = retries
        self.user_agent = user_agent
        self.respect_robots_txt = respect_robots_txt

    def _robots_url_for(self, url: str) -> str:
        parsed_url = urllib.parse.urlparse(url)
        return urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, "/robots.txt", "", "", ""))

    def _fetch_robots_txt(
        self,
        robots_url: str,
        headers: typing.Mapping[str, str] | None = None,
    ) -> requests.Response:
        return requests.get(robots_url, timeout=self.timeout, headers=headers)

    def _get_robot_parser(
        self,
        robots_url: str,
        headers: typing.Mapping[str, str] | None = None,
    ) -> tuple[urllib.robotparser.RobotFileParser, list[str]]:
        robot_parser = urllib.robotparser.RobotFileParser(robots_url)

        try:
            response = self._fetch_robots_txt(robots_url, headers=headers)
        except RequestException as e:
            logger.warning(f"Could not fetch robots.txt from {robots_url}; disallowing request: {e}")
            robot_parser.disallow_all = True
            return robot_parser, []

        if response.status_code == 200:
            lines = response.text.splitlines()
            robot_parser.parse(lines)
            return robot_parser, lines

        if response.status_code in (401, 403):
            robot_parser.disallow_all = True
            return robot_parser, []

        if 400 <= response.status_code < 500:
            robot_parser.allow_all = True
            return robot_parser, []

        logger.warning(f"Could not fetch robots.txt from {robots_url}: HTTP {response.status_code}; disallowing request")
        robot_parser.disallow_all = True
        return robot_parser, []

    def _extract_user_agent(self, headers: typing.Mapping[str, str] | None = None) -> str:
        if not headers:
            return self.user_agent

        for header_name, header_value in headers.items():
            if header_name.lower() == "user-agent":
                return header_value

        return self.user_agent

    def _headers_with_user_agent(
        self,
        headers: typing.Mapping[str, str] | None = None,
    ) -> dict[str, str]:
        request_headers = dict(headers or {})

        if not any(header_name.lower() == "user-agent" for header_name in request_headers):
            request_headers["User-Agent"] = self.user_agent

        return request_headers

    def _user_agent_applies(self, robot_user_agent: str, request_user_agent: str) -> bool:
        if robot_user_agent == "*":
            return True

        return robot_user_agent.lower() in request_user_agent.split("/")[0].lower()

    def _parse_content_signals(self, value: str) -> dict[str, str]:
        signals = {}
        for signal in value.split(","):
            name, separator, setting = signal.partition("=")
            if separator:
                signals[name.strip().lower()] = setting.strip().lower()

        return signals

    def _ai_input_disallowed(self, lines: list[str], user_agent: str) -> bool:
        matching_signals: list[tuple[int, dict[str, str]]] = []
        current_user_agents: list[str] = []
        current_signals: dict[str, str] = {}
        group_has_directives = False

        def finish_group() -> None:
            if not current_user_agents:
                return

            matching_agents = [
                agent for agent in current_user_agents
                if self._user_agent_applies(agent, user_agent)
            ]
            if not matching_agents:
                return

            specificity = max(0 if agent == "*" else len(agent) for agent in matching_agents)
            matching_signals.append((specificity, current_signals.copy()))

        for raw_line in lines:
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                finish_group()
                current_user_agents = []
                current_signals = {}
                continue

            field, separator, value = line.partition(":")
            if not separator:
                continue

            field = field.strip().lower()
            value = value.strip()

            if field == "user-agent":
                if group_has_directives:
                    finish_group()
                    current_user_agents = []
                    current_signals = {}
                    group_has_directives = False
                current_user_agents.append(value.lower())
            elif field == "content-signal":
                current_signals.update(self._parse_content_signals(value))
                group_has_directives = True
            else:
                group_has_directives = True

        finish_group()

        if not matching_signals:
            return False

        _, most_specific_signals = max(matching_signals, key=lambda signal: signal[0])
        return most_specific_signals.get("ai-input") == "no"

    def _ensure_robots_txt_allows(
        self,
        url: str,
        headers: typing.Mapping[str, str] | None = None,
    ) -> None:
        if not self.respect_robots_txt:
            return

        user_agent = self._extract_user_agent(headers)
        robots_url = self._robots_url_for(url)
        robot_parser, robots_lines = self._get_robot_parser(robots_url, headers=headers)

        if not robot_parser.can_fetch(user_agent, url):
            raise PermissionError(f"robots.txt disallows {user_agent} from fetching {url}")

        if self._ai_input_disallowed(robots_lines, user_agent):
            raise PermissionError(f"robots.txt Content-Signal disallows ai-input for {url}")

    def _send_request(self, method: str, url: str, **kwargs: typing.Any) -> requests.Response:
        return requests.request(method, url, timeout=self.timeout, **kwargs)

    def _log_response(self, response: requests.Response, url: str) -> None:
        return None

    def request(self, method: str, url: str, **kwargs: typing.Any) -> requests.Response | None:
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

        headers = self._headers_with_user_agent(kwargs.get("headers"))
        kwargs["headers"] = headers
        self._ensure_robots_txt_allows(url, headers=headers)

        for attempt in range(self.retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1}/{self.retries})")
                response = self._send_request(method, url, **kwargs)
                self._log_response(response, url)
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
        :param url: API endpoint.
        :param kwargs: Additional arguments for the DELETE request.
        :return requests.Response: The HTTP response object.
        """
        return self.request("DELETE", url, **kwargs)
