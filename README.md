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
### Running the server
```bash
flask --app backend/app.py run --debug
```