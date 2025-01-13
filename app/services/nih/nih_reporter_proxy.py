from app.utils.http_client import HttpClient
from app.core.constants import NIH_REPORTER_PAYLOAD

class NIHReporterProxy():
    NIH_REPORTER_ENDPOINT = "https://api.reporter.nih.gov/v2/projects/search"

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

