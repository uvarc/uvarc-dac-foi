import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(BASE_DIR, "..", "..", "rc-DACFOI.env")
load_dotenv(dotenv_path=env_path)

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = "../../frontend/html/static/"
    TEMPLATES_FOLDER = "../../frontend/html/"