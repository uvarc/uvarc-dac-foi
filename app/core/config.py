import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "../../rc-DACFOI.env")
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = "../static"
    TEMPLATES_FOLDER = "../templates"