# DAC Faculty Outreach Initiative
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
Then set database population options in `backend/core/populate_config.py`, then run:
```bash
python -m backend.core.populate
```
### Running the server
```bash
flask --app backend/app.py run --debug
```