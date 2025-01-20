import typing
from app.services.nih.nih_reporter_service import NIHReporterService
from app.services.scraper.scraper_service import ScraperService
from app.models.models import *


class DataAggregator:
    def __init__(self, scraper_service: ScraperService, nih_service: NIHReporterService):
        self.scraper_service = scraper_service
        self.nih_service = nih_service
        """
        {
            dept1: [
                {
                    "faculty": FacultyObject
                    "embedding_id": int
                },
                {
                ...
                }
            ]
            dept2: [
                ...
            ]
            ...
        }
        :param school: 
        :return: 
        """

    def aggregate_school_faculty_data(self, school: str) -> typing.Dict:
        """
        Aggregate faculty data for school from scrapers, NIH RePORTER API, generate embeddings
        Outputs are DB commit-ready
        :param school: school acronym
        :return: dictionary of department faculty data stored as Faculty model objects
        """
        school_faculty_df = self.scraper_service.get_school_faculty_data(school)
        aggregated_faculty_data = {}
        for dept, dept_faculty_df in school_faculty_df.items():
            aggregated_faculty_data[dept] = []
            for faculty_profile in dept_faculty_df.itertuples():
                first_name, last_name = self.extract_faculty_names_from_profile(faculty_profile)
                projects = self.get_faculty_member_projects(first_name, last_name)
                # TODO: generate faculty embedding and return ID
                # faculty = self.convert_to_faculty_model(faculty_profile, projects, embedding_id)

    @staticmethod
    def extract_faculty_names_from_profile(faculty_profile: typing.Tuple) -> typing.Tuple[str, str]:
        """
        Extract faculty names from namedtuple
        :param faculty_profile: named tuple w/ faculty information
        :return: first and last name of faculty member
        """
        names = faculty_profile.Faculty_Name.split(" ")
        return names[0], names[-1]

    def get_faculty_member_projects(self, pi_first_name: str, pi_last_name: str) -> typing.List[Project]:
        """
        Retrieve NIH-funded projects from NIH RePORTER API and convert to Project model object
        :param pi_first_name: PI first name
        :param pi_last_name: PI last name
        :return: list of Project model objects
        """
        projects_df = self.nih_service.compile_project_metadata(pi_first_name, pi_last_name)
        return [self.convert_to_project_model(project) for project in projects_df.itertuples()]

    @staticmethod
    def convert_to_project_model(project: typing.Tuple) -> Project:
        """
        Convert namedtuple to Project model object
        :param project: namedtuple
        :return: Project model object
        """
        return Project(
            project_number=project.project_number,
            abstract=project.abstract_text,
            relevant_terms=project.terms,
            start_date=project.start_date,
            end_date=project.end_date,
            agency_ic_admin=project.agency_ic_admin,
            activity_code=project.activity_code
        )

    @staticmethod
    def convert_to_faculty_model(faculty_profile: typing.Tuple, projects: typing.List[Project], embedding_id: int) -> Faculty:
        """
        Use profile, RePORTER project data, and embedding ID to construct Faculty model object
        :param faculty_profile: namedtuple w/ faculty information
        :param projects: list of Project model objects
        :param embedding_id: embedding id
        :return: Faculty model object
        """
        return Faculty(
            name=faculty_profile.Faculty_Name,
            school=faculty_profile.School,
            department=faculty_profile.Department,
            about=faculty_profile.About_Section,
            email=faculty_profile.Email_Address,
            profile_url=faculty_profile.Profile_URL,
            projects=projects,
            embedding_id=embedding_id
        )


from app.utils.http_client import HttpClient
from app.services.nih.nih_reporter_proxy import NIHReporterProxy
from app.services.scraper.seas_scraper import SEASScraper
nih_service = NIHReporterService(NIHReporterProxy(HttpClient()))
scrapers = [
    SEASScraper(HttpClient())
]
scraper_service = ScraperService(scrapers)
aggregator = DataAggregator(scraper_service, nih_service)
dept_faculty_df = scraper_service.get_department_faculty_data("Biomedical Engineering")
for faculty_profile in dept_faculty_df.itertuples():
    first_name, last_name = aggregator.extract_faculty_names_from_profile(faculty_profile)
    projects = aggregator.get_faculty_member_projects(first_name, last_name)
    faculty = aggregator.convert_to_faculty_model(faculty_profile, projects)
