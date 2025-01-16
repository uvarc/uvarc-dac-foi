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

    def get_project_data(self, first_name: str = None, last_name: str = None, fiscal_years: typing.List = None) -> pd.DataFrame:
        if first_name is None or last_name is None:
            raise ValueError("")
        if fiscal_years is None:
            fiscal_years = [datetime.now().year]

        payload = self.build_payload(first_name, last_name, fiscal_years)
        response = self.proxy.call_reporter_api(payload)
        projects = self.get_all_projects(response)

        all_project_data = []
        for project in projects:
            metadata = dict()
            metadata["project_number"] = self.get_project_number(project)
            metadata["abstract_text"] = self.get_abstract_text(project)

    @staticmethod
    def get_all_projects(self, response: typing.Dict) -> typing.List[typing.Dict]:
        try:
            projects = response["results"]
            if len(projects) == 0:
                logger.warning("No projects found for given PI or fiscal year(s)")
                return []
        except KeyError:
            logger.error("Results field missing in response")
            return []

    @staticmethod
    def get_project_number(self, project: typing.Dict) -> int:
        try:
            return project["project_num"]
        except KeyError:
            logger.error(f"Project number missing for project: {project}")
            return -1

    @staticmethod
    def get_abstract_text(self, project: typing.Dict) -> str:
        try:
            return project["abstract_text"]
        except KeyError:
            logger.error(f"Abstract text missing for project: {project}")
            return "N/A"

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



proxy = NIHReporterProxy(HttpClient())
service = NIHReporterService(proxy)
service.get_project_data("David", "Abebayehu", fiscal_years=[2024, 2025])