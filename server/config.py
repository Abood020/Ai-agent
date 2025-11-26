import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

DB_PATH = os.path.join(BASE_DIR, "library.db")
DB_PATH = DB_PATH.replace("\\", "/")

DATABASE_URL = f"sqlite:///{DB_PATH}"
