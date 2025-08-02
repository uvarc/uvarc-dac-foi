import typing
import pandas as pd
import logging
import copy
from datetime import datetime
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.core.populate_config import NIH_REPORTER_PAYLOAD, DEFAULT_FISCAL_YEARS

logger = logging.getLogger(__name__)

class NSFService:

    def __init__(self, proxy: NSFProxy):
        self.proxy = proxy

    def compile_project_metadata(self, pi_first_name: str = None, pi_last_name: str = None, fiscal_years: typing.List[int] = DEFAULT_FISCAL_YEARS) -> pd.DataFrame:
        """
        Extract relevant metadata from PI projects for provided fiscal years
        :param pi_first_name: PI's first name
        :param pi_last_name: PI's last name
        :param fiscal_years: fiscal years during which projects were/are active
        :return: dataframe of given PI's project metadata
        """
        resp = self.proxy.call_nsf_api(payload={
            "coPDPI": pi_first_name + " " + pi_last_name
        }) if pi_first_name and pi_last_name else None

        response = self.invoke_proxy(pi_first_name=pi_first_name, pi_last_name=pi_last_name, fiscal_years=fiscal_years)

        projects = resp["response"]["award"]
        if len(projects) == 0:
            logger.warning(f"No projects founds for PI '{pi_first_name} {pi_last_name}' and fiscal years '{fiscal_years}'")
            return pd.DataFrame()

        compiled_metadata = [
            {
                "id": self.safe_get_field(project, "id"),
                "date": self.safe_get_field(project, "date"),
                "start_date": self.safe_get_field(project, "start_date"),
                "title": self.safe_get_field(project, "title"),
            }
            for project in projects
        ]

        return pd.DataFrame(compiled_metadata)

    def invoke_proxy(self, pi_first_name: str, pi_last_name: str, fiscal_years: typing.List) -> typing.Dict:
        if pi_first_name is None or pi_last_name is None:
            raise ValueError("pi_first_name and pi_last_name cannot be None")
        payload = self.build_payload(pi_first_name, pi_last_name, fiscal_years)
        return self.proxy.call_nsf_api(payload)

    @staticmethod
    def process_date_string(raw_date: str) -> datetime.date:
        try:
            parsed_datetime = datetime.strptime(raw_date, "%m/%d/%Y")
            return parsed_datetime.date()
        except Exception as e:
            logger.error(f"Unexpected error parsing date {raw_date}, returning unprocessed date: {e}")
            return None

    @staticmethod
    def build_payload(pi_first_name: str, pi_last_name: str, fiscal_years: typing.List[int]) -> typing.Dict:
        """
        Build the payload for the NIH RePORTER API request
        :param pi_first_name: PI's first name
        :param pi_last_name: PI's last name
        :param fiscal_years: list of fiscal years to filter results
        :return: payload as dictionary
        """
        payload = copy.deepcopy(NIH_REPORTER_PAYLOAD)
        payload["criteria"]["pi_names"][0]["first_name"] = pi_first_name
        payload["criteria"]["pi_names"][0]["last_name"] = pi_last_name
        payload["criteria"]["fiscal_years"] = fiscal_years
        return payload

    @staticmethod
    def safe_get_field(data: dict, key: str) -> typing.Any:
        """
        Return field from API response and abstract error handling logic from JSON indexing,
        :param data: API response
        :param key: key corresponding to field to retrieve
        :return: field to retrieve
        """
        try:
            field = data[key]
            if key == "agency_ic_admin":
                return field["name"]
            return field
        except KeyError:
            logger.error(f"{key} missing in data: {data}")
            return "N/A"
