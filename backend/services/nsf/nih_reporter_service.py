import typing
import pandas as pd
import logging
import copy
from datetime import datetime
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.core.populate_config import NIH_REPORTER_PAYLOAD, DEFAULT_FISCAL_YEARS

logger = logging.getLogger(__name__)

class NIHReporterService:

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
        response = self.invoke_proxy(pi_first_name=pi_first_name, pi_last_name=pi_last_name, fiscal_years=fiscal_years)

        projects = response["results"]
        if len(projects) == 0:
            logger.warning(f"No projects founds for PI '{pi_first_name} {pi_last_name}' and fiscal years '{fiscal_years}'")
            return pd.DataFrame()

        compiled_metadata = [
            {
                "project_number": self.get_project_number(project),
                "abstract_text": self.get_abstract_text(project),
                "terms": self.get_terms(project),
                "start_date": self.get_project_start_date(project),
                "end_date": self.get_project_end_date(project),
                "agency_ic_admin": self.get_agency_ic_admin(project),
                "activity_code": self.get_activity_code(project),
            }
            for project in projects
        ]

        return pd.DataFrame(compiled_metadata)

    def invoke_proxy(self, pi_first_name: str, pi_last_name: str, fiscal_years: typing.List) -> typing.Dict:
        if pi_first_name is None or pi_last_name is None:
            raise ValueError("pi_first_name and pi_last_name cannot be None")
        payload = self.build_payload(pi_first_name, pi_last_name, fiscal_years)
        return self.proxy.call_reporter_api(payload)

    def get_project_number(self, project: typing.Dict) -> str:
        """
        Extract unique project number from API response segment
        :param project: JSON w/ project metadata
        :return: project number
        """
        return self.safe_get_field(project, "project_num")

    def get_abstract_text(self, project: typing.Dict) -> str:
        """
        Extract abstract text from API response segment
        :param project: JSON w/ project metadata
        :return: abstract text
        """
        return self.safe_get_field(project, "abstract_text")

    def get_terms(self, project: typing.Dict) -> datetime.date:
        """
        Extract terms from API response segment
        :param project: JSON w/ project metadata
        :return list of key terms relevant to project
        """
        return self.safe_get_field(project, "terms")

    def get_project_start_date(self, project: typing.Dict) -> datetime.date:
        """
        Extract project start date from API response segment
        :param project: JSON w/ project metadata
        :return: project start date
        """
        raw_start_date = self.safe_get_field(project, "project_start_date")
        return self.process_date_string(raw_start_date)

    def get_project_end_date(self, project: typing.Dict) -> str:
        """
        Extract project end date from API response segment
        :param project: JSON w/ project metadata
        :return: project end date
        """
        raw_end_date = self.safe_get_field(project, "project_end_date")
        return self.process_date_string(raw_end_date)

    def get_agency_ic_admin(self, project: typing.Dict) -> str:
        """
        Extract NIH agency administering project from API response segment
        :param project: JSON w/ project metadata
        :return: NIH agency
        """
        return self.safe_get_field(project, "agency_ic_admin")

    def get_activity_code(self, project: typing.Dict) -> str:
        """
        Extract activity code from API response segment
        :param project: JSON w/ project metadata
        :return: activity code
        """
        return self.safe_get_field(project, "activity_code")

    @staticmethod
    def process_date_string(raw_date: str) -> datetime.date:
        try:
            parsed_datetime = datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S")
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
