import typing

from app.services.embedding.embedding_service import EmbeddingService
from app.services.nih.nih_reporter_service import NIHReporterService
from app.services.scraper.scraper_service import ScraperService
from app.models.models import *


class DataAggregator:
    def __init__(self, scraper_service: ScraperService, nih_service: NIHReporterService, embedding_service: EmbeddingService):
        self.scraper_service = scraper_service
        self.nih_service = nih_service
        self.embedding_service = embedding_service

    def aggregate_school_faculty_data(self, school: str) -> typing.List[Faculty]:
        """
        Aggregate faculty data for school from scrapers, NIH RePORTER API, generate embeddings
        Outputs are DB commit-ready
        :param school: school acronym
        :return: dictionary of department faculty data stored as Faculty model objects
        """
        school_faculty_df = self.scraper_service.get_school_faculty_data(school)
        all_faculty = []
        for dept, dept_faculty_df in school_faculty_df.items():
            for faculty_profile in dept_faculty_df.itertuples():
                faculty = self.build_faculty_model(faculty_profile)
                all_faculty.append(faculty)
        return all_faculty

    def build_faculty_model(self, faculty_profile: typing.Tuple) -> Faculty:
        """
        Build faculty model from faculty profile
        :param faculty_profile: faculty data
        :return: faculty model
        """
        first_name, last_name = self.extract_faculty_names_from_profile(faculty_profile)
        projects = self.get_faculty_member_projects(first_name, last_name)
        faculty = self.convert_to_faculty_model(faculty_profile, projects)
        embedding_id = self.embedding_service.generate_and_store_embedding(faculty, projects)
        faculty.embedding_id = embedding_id
        return faculty

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
    def convert_to_faculty_model(faculty_profile: typing.Tuple, projects: typing.List[Project]) -> Faculty:
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
            embedding_id=-1,
        )