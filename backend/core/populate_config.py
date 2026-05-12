import os
import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "..", "..", "instance", "index.faiss")

# Whether to keep existing schools in the database and only (re)add new ones
# or to clear all data and re-populate from scratch
KEEP_EXISTING_SCHOOLS = True

# Whether to rebuild the FAISS index after populating the database
# (only takes effect if KEEP_EXISTING_SCHOOLS is True)
REBUILD_INDEX = False

SCHOOLS_TO_SCRAPE = ["DARDEN"]

SCHOOL_DEPARTMENT_DATA = {
    "NURSING": {
        "base_url": "",
        "add_nih_data": False,
        "departments": {
            "Nursing (all)": {
                "people_url": "https://nursing.virginia.edu/research/faculty-research/"
            }
        }
    },
    "BATTEN": {
        "base_url": "",
        "add_nih_data": False,
        "departments": {
            "Batten (all)": {
                "people_url": "https://batten.virginia.edu/faculty-research/faculty"
            }
        }
    },
    "DARDEN": {
        "base_url": "",
        "add_nih_data": False,
        "departments": {
            "Darden (all)": {
                "people_url": "https://www.darden.virginia.edu/faculty-research/directory?faculty_type=Faculty&page="
            }
        }
    },
    "SEAS": {
        "base_url": "https://engineering.virginia.edu",
        "departments": {
            "Biomedical Engineering": {
                "people_url": "https://engineering.virginia.edu/department/biomedical-engineering/people?keyword=&position=2&impact_area=All&research_area=All",
            },
            "Chemical Engineering": {
                "people_url": "https://engineering.virginia.edu/department/chemical-engineering/people?keyword=&position=2&impact_area=All&research_area=All",
            },
            "Civil and Environmental Engineering": {
                "people_url": "https://engineering.virginia.edu/department/civil-and-environmental-engineering/people?keyword=&position=2&impact_area=All&research_area=All",
            },
            "Computer Engineering": {
                "people_url": "https://engineering.virginia.edu/offices-programs/computer-engineering-program/faculty?keyword=&position=2&impact_area=All&research_area=All",
            },
            "Computer Science": {
                "people_url": "https://engineering.virginia.edu/department/computer-science/people?keyword=&position=2&impact_area=All&research_area=All"
            },
            "Electrical and Computer Engineering": {
                "people_url": "https://engineering.virginia.edu/department/electrical-and-computer-engineering/faculty?keyword=&position=2&impact_area=All&research_area=All"
            },
            "Engineering and Society": {
                "people_url": "https://engineering.virginia.edu/department/engineering-and-society/people?keyword=&position=2&impact_area=All&research_area=All",
            },
            "Materials Science and Engineering": {
                "people_url": "https://engineering.virginia.edu/department/materials-science-and-engineering/people?impact_area=All&keyword=&position=2&research_area=All",
            },
            "Mechanical and Aerospace Engineering": {
                "people_url": "https://engineering.virginia.edu/department/mechanical-and-aerospace-engineering/people?keyword=&position=2&impact_area=All&research_area=All"
            },
            "Systems and Information Engineering": {
                "people_url": "https://engineering.virginia.edu/department/systems-and-information-engineering/people?keyword=&position=2&impact_area=All&research_area=All",
            },
        },
    },

    "SOM": {
        "base_url": "https://med.virginia.edu",
        "departments": {
            "Cell Biology": {
                "people_url": "https://med.virginia.edu/cell-biology/department-faculty/",
             },
            "Biochemistry and Molecular Genetics": {
                "people_url": "https://med.virginia.edu/bmg/faculty/",
            },
            "Microbiology, Immunology, Cancer Biology": {
                "people_url": "https://med.virginia.edu/mic/faculty/primary-faculty/",
            },
            "Molecular Physiology and Biological Physics": {
                "people_url": "https://med.virginia.edu/physiology-biophysics/faculty/",
            },
            "Pharmacology": {
                "people_url": "https://med.virginia.edu/pharm/primary-faculty/",
            },
        },
    },
}

DEFAULT_FISCAL_YEARS = list(range(datetime.datetime.now().year - 5, datetime.datetime.now().year + 1))

NIH_REPORTER_PAYLOAD = {
    "criteria": {
        "use_relevance": True,
        "fiscal_years": [],
        "include_active_projects": True,
        "pi_names": [
            {
                "first_name": "",
                "last_name": "",
            }
        ],
        "org_names": [
            "UNIVERSITY OF VIRGINIA",
            "University of Virginia"
        ],
    },
}

OPENAI_CONFIG = {
    "EMBEDDING_MODEL": "text-embedding-ada-002",
    "MAX_TOKENS": 8192,
    "EMBEDDING_DIMENSIONS": 1536,
}
