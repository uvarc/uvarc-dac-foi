import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    # TODO: set SQLALCHEMY_DATABASE_URI
