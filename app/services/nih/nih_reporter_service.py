import typing
from app.services.nih.nih_reporter_proxy import NIHReporterProxy

class NIHReporterService:

    def __init__(self, proxy: NIHReporterProxy):
        self.proxy = proxy

    def get_project_grants(self, first_name: str, last_name: str, fiscal_years: typing.List) -> typing.List:
        # TODO: Implement getter functions (not sure what data should be retrieved
        pass


