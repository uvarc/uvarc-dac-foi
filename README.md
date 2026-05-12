# DAC Faculty Outreach Initiative
A program that scrapes faculty profiles from UVA websites, embeds them with OpenAI's embedding model, then serves a Flask web app that allows for non-exact keyword search of these profiles.
## Setup
### Populating the database
Set API keys in `rc-DACFOI.env`:
#### OpenAI API
```
OPENAI_API_KEY="your-api-key"
DATABASE_URL="sqlite:///database.db"
```
#### Azure OpenAI
```
OPENAI_API_KEY="your-api-key"
OPENAI_BASE_URL="https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1"
DATABASE_URL="sqlite:///database.db"
```
Note that your deployment of the Azure OpenAI embedding model should be named `text-embedding-ada-002`.

Then set database population options in `backend/core/populate_config.py`, then run:
```bash
python -m backend.core.populate
```
Note that you must be on the UVA network.
### Running the server
```bash
flask --app backend/app.py run --debug
```
## Adding a New School
To add a new school:
* create a new scraper class in `backend/services/scraper` that inherits from `BaseScraper` (use the existing scrapers as a template). 
    * Generally, the scraper's methods will consist of requests to the school's faculty directory, followed by lxml parsing of the returned HTML (using XPath queries) to extract faculty profile information. 
* import and add the scraper to ScraperService in `backend/core/populate.py`.
* add the new scraper to `SCHOOL_DEPARTMENT_DATA` and `SCHOOLS_TO_SCRAPE` in `backend/core/populate_config.py`, with the appropriate school and department URLs.
    * Keep `KEEP_EXISTING_SCHOOLS = True` and `REBUILD_INDEX = False` if you want the fastest way to preserve existing schools in the database and just add the new school.
* run the populate script to add the new school's faculty profiles to the database and index.
    * To get more verbose output on the scraping process, change the logging level at the top of `backend/utils/institution_utils.py` to `logging.DEBUG`.
* add the school to the `<select id="school">` element in `frontend/html/search.html` to make it available as a filter option in the search app. If there are multiple departments for the school, add these at the top of `frontend/html/static/js/search.js` in the `schoolDepartments` object.