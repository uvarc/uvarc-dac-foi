"""
Backfill NSF grants for faculty already stored in the application database.

This script is intended for one-off maintenance after faculty rows already
exist. It reads each faculty member's school from the database and consults
``backend.core.populate_config.SCHOOL_DEPARTMENT_DATA`` before calling the NSF
API. NSF grants are fetched only when at least one of the faculty member's
configured schools has ``add_nsf_data`` set to ``True``. Schools missing from
the config, or schools with ``add_nsf_data`` set to ``False``, are skipped.

Running the script:
    python add_grants_to_db.py

The script appends newly fetched grants and then updates ``Faculty.has_funding``
based on whether the faculty member has any grants.
"""

import logging
from backend.services.nsf.nsf_service import NSFService
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.models.models import Grant, Faculty
import requests
from backend.core.extensions import db
from backend.core.populate_config import SCHOOL_DEPARTMENT_DATA
from backend.app import app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _get_faculty_schools(faculty):
    """
    Return normalized school names for a faculty record.

    Faculty rows can contain one school (``"SEAS"``) or merged schools as a
    comma-separated string (``"SEAS,SOM"``). Empty values are ignored.
    """
    if not faculty.school:
        return []
    return [school.strip() for school in faculty.school.split(",") if school.strip()]


def _should_add_nsf_grants(faculty):
    """
    Return True when NSF grant backfill is enabled for this faculty member.

    A faculty member is eligible if at least one of their configured schools has
    ``add_nsf_data=True`` in ``SCHOOL_DEPARTMENT_DATA``. Unknown schools are
    skipped because this script should not add NSF grants unless the populate
    config explicitly opts the school in.
    """
    schools = _get_faculty_schools(faculty)
    for school in schools:
        school_config = SCHOOL_DEPARTMENT_DATA.get(school)
        if school_config and school_config.get("add_nsf_data", True):
            return True
    return False


def add_grants_to_db():
    """
    Add NSF grants to eligible existing faculty members in the database.

    Eligibility is controlled by ``add_nsf_data`` in
    ``backend/core/populate_config.py``. Faculty in disabled or unknown schools
    are skipped without making NSF API calls.
    """
    with app.app_context():
        all_faculty = db.session.query(Faculty).all()
        nsf_service = NSFService(proxy=NSFProxy())
        for faculty in all_faculty:
            if not _should_add_nsf_grants(faculty):
                logger.info(
                    "Skipping NSF grants for %s because add_nsf_data is not enabled for school(s): %s",
                    faculty.name,
                    ", ".join(_get_faculty_schools(faculty)) or "unknown",
                )
                continue

            fetched_grants = nsf_service.compile_project_metadata(
                pi_first_name=faculty.name,
                pi_last_name=""
            )
            print(f"Number of grants found for {faculty.name}: {len(fetched_grants.index)}")
            if fetched_grants.empty:
                continue
            for _, row in fetched_grants.iterrows():
                grant = Grant(
                    nsf_id=row['id'],
                    date=nsf_service.process_date_string(row['date']), 
                    start_date=nsf_service.process_date_string(row['start_date']), 
                    title=row['title']
                )
                faculty.grants.append(grant)
                db.session.add(grant)
                print(f"Added grant {grant.nsf_id} ({grant.title})")
        db.session.commit()

def update_has_funding_bool():
    """Update each faculty member's ``has_funding`` value based on grants."""
    with app.app_context():
        all_faculty = db.session.query(Faculty).all()
        for faculty in all_faculty:
            print(f"Updating has_funding for {faculty.name}")
            faculty.has_funding = faculty.has_funding or len(faculty.grants if isinstance(faculty.grants, list) else faculty.grants.all()) > 0
            print(f"Faculty {faculty.name} has_funding set to {faculty.has_funding}")
        db.session.commit()

def check_recipient_inst_of_all_nsf_grants():
    """Print the recipient institution for each stored NSF grant."""
    with app.app_context():
        all_grants = db.session.query(Grant).all()
        for grant in all_grants:
            grant_id = grant.nsf_id
            endpt = f"https://api.nsf.gov/services/v1/awards/{grant_id}.json"
            try:
                response = requests.get(endpt)
                response.raise_for_status()
                data = response.json()
                inst = data['response']['award']
                for award in inst:
                    print(f"Grant {grant_id} recipient institution: {award['awardeeName']}")
            except requests.RequestException as e:
                print(f"Error fetching data for grant {grant_id}: {e}")
                continue

if __name__ == "__main__":
    add_grants_to_db()
    update_has_funding_bool()
    # check_recipient_inst_of_all_nsf_grants()
