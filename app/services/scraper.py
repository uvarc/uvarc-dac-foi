from app.utils.constants import SEAS_DEPARTMENTS
from app.utils.constants import NO_RESULTS_DIV
from app.utils.constants import CONTACT_BLOCK_NAME_A_TAG
from app.utils.http_client import HttpClient

import requests
import typing
import logging
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DepartmentScraper:
    def __init__(self, http_client: HttpClient):
        self.http_client = http_client
        pass
