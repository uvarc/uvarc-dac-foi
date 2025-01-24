import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    secret_key = os.getenv("SECRET_KEY")
    sqlalchemy_database_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
    sqlalchemy_track_modifications = False
    static_folder = "../static"
    templates_folder = "../templates"