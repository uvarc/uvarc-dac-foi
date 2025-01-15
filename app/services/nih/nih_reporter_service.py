import typing
import pandas as pd
import logging
import copy

from datetime import datetime
from app.services.nih.nih_reporter_proxy import NIHReporterProxy
from app.utils.http_client import HttpClient
from app.core.constants import NIH_REPORTER_PAYLOAD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NIHReporterService:

    def __init__(self, proxy: NIHReporterProxy):
        self.proxy = proxy

    def get_project_data(self, first_name: str, last_name: str, fiscal_years: typing.List = None) -> pd.DataFrame:
        if fiscal_years is None:
            fiscal_years = [datetime.now().year]

        payload = self._build_payload(first_name, last_name, fiscal_years)
        response = self.proxy.call_reporter_api(payload)
        projects = self._all_projects(response)



    def _all_projects(self, response: typing.Dict) -> typing.List[typing.Dict]:
        try:
            projects = response["results"]
            if len(projects) == 0:
                logger.warning("No projects found for given PI or fiscal year(s)")
                return []
        except KeyError:
            logger.error("Results field absent in response JSON")
            return []

    @staticmethod
    def _build_payload(first_name: str, last_name: str, fiscal_years: typing.List) -> typing.Dict:
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



proxy = NIHReporterProxy(HttpClient())
payload = proxy.build_payload("Daniel", "Abebayehu", [2024, 2025])
response = proxy.call_reporter_api(payload)
print(response)