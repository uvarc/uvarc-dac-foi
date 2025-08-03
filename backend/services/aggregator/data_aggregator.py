import typing
import logging
from datetime import date
from backend.services.embedding.embedding_service import EmbeddingService
from backend.services.nih.nih_reporter_service import NIHReporterService
from backend.services.nsf.nsf_service import NSFService
from backend.services.scraper.scraper_service import ScraperService
from backend.models.models import *

logger = logging.getLogger(__name__)

class DataAggregator:
    def __init__(self,
                 scraper_service: ScraperService,
                 nih_service: NIHReporterService,
                 embedding_service: EmbeddingService,
                 nsf_service: NSFService = None):
        self.scraper_service = scraper_service
        self.nih_service = nih_service
        self.embedding_service = embedding_service
        self.nsf_service = nsf_service

    def aggregate_school_faculty_data(self, school: str) -> typing.List[Faculty]:
        """
        Aggregate faculty data for school from scrapers, NIH RePORTER API, generate embeddings
        Outputs are DB commit-ready
        :param school: school acronym
        :return: dictionary of department faculty data stored as Faculty model objects
        """
        school_faculty_df = self.scraper_service.get_school_faculty_data(school)
        school_faculty = dict()

        for dept, dept_faculty_df in school_faculty_df.items():
            for faculty_profile in dept_faculty_df.itertuples():
                faculty_identifier = (faculty_profile.Faculty_Name, faculty_profile.School, faculty_profile.Email_Address)

                if faculty_identifier in school_faculty:
                    school_faculty[faculty_identifier] = self._update_faculty_department(school_faculty[faculty_identifier], faculty_profile.Department)

                else:
                    faculty = self._build_faculty_model(faculty_profile)
                    faculty.embedding_id = self.embedding_service.generate_and_store_embedding(faculty)
                    school_faculty[faculty_identifier] = faculty

        return list(school_faculty.values())

    def _build_faculty_model(self, faculty_profile: typing.Tuple) -> Faculty:
        """
        Build faculty model from faculty profile
        :param faculty_profile: faculty data
        :return: faculty model
        """
        first_name, last_name = self._extract_names(faculty_profile)
        logger.info(f"Fetching NIH project information for {first_name} {last_name}.")
        projects = self._get_projects(first_name, last_name)

        faculty = Faculty(
            name=faculty_profile.Faculty_Name,
            school=faculty_profile.School,
            department=faculty_profile.Department,
            about=faculty_profile.About_Section,
            email=faculty_profile.Email_Address,
            profile_url=faculty_profile.Profile_URL,
            projects=projects,
            has_funding=self._has_funding(projects),
            embedding_id=-1,
        )
        return faculty

    def _get_projects(self, pi_first_name: str, pi_last_name: str) -> typing.List[Project]:
        """
        Retrieve NIH-funded projects from NIH RePORTER API and convert to Project model object
        :param pi_first_name: PI first name
        :param pi_last_name: PI last name
        :return: list of Project model objects
        """
        projects_df = self.nih_service.compile_project_metadata(pi_first_name, pi_last_name)
        return [self._convert_to_project_model(project) for project in projects_df.itertuples()]

    @staticmethod
    def _convert_to_project_model(project: typing.Tuple) -> Project:
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
    def _extract_names(faculty_profile: typing.Tuple) -> typing.Tuple[str, str]:
        """
        Extract faculty names from NamedTuple
        :param faculty_profile: named tuple w/ faculty information
        :return: first and last name of faculty member
        """
        names = faculty_profile.Faculty_Name.split(" ")
        return names[0], names[-1]

    @staticmethod
    def _update_faculty_department(faculty: Faculty, new_department: str) -> Faculty:
        """
        Update faculty department field, used when faculties are encountered more than once across dept pages
        :param faculty: Faculty object
        :param new_department: faculty department field
        """
        faculty.department = ",".join(sorted(set(faculty.department.split(",") + [new_department])))
        return faculty

    def _has_funding(self, projects: typing.List[Project]) -> bool:
        """
        Check if any projects have active funding
        :param projects: list of Project objects
        :return: True if any projects have active funding else False
        """
        return any(self._is_project_funded(project) for project in projects)

    @staticmethod
    def _is_project_funded(project: Project) -> bool | None:
        """Helper function to check if project has active funding"""
        if not project.start_date or not project.end_date:
            return None
        return project.start_date <= date.today() <= project.end_date