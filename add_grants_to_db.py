import logging
from backend.services.nsf.nsf_service import NSFService
from backend.services.nsf.nsf_proxy import NSFProxy
from backend.models.models import Grant, Faculty

from backend.core.extensions import db
from backend.app import app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def add_grants_to_db():
    '''
    Add NSF grants to each existing faculty member in the database
    '''
    with app.app_context():
        all_faculty = db.session.query(Faculty).all()
        nsf_service = NSFService(proxy=NSFProxy())
        for faculty in all_faculty:
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
    ''' Update the has_funding boolean for each faculty member based on their grants
    '''
    with app.app_context():
        all_faculty = db.session.query(Faculty).all()
        for faculty in all_faculty:
            print(f"Updating has_funding for {faculty.name}")
            faculty.has_funding = faculty.has_funding or len(faculty.grants if isinstance(faculty.grants, list) else faculty.grants.all()) > 0
            print(f"Faculty {faculty.name} has_funding set to {faculty.has_funding}")
        db.session.commit()

if __name__ == "__main__":
    add_grants_to_db()
    # update_has_funding_bool()