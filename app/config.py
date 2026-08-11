import os
from dotenv import load_dotenv

load_dotenv()

APP_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    DB_PATH = os.path.join(APP_DIR, os.getenv("DB_PATH", "bici.db"))

    UPLOAD_FOLDER = os.path.join(APP_DIR, os.getenv("UPLOAD_FOLDER", "static/uploads"))

    MAX_MINUTOS_SESION = int(os.getenv("MAX_MINUTOS_SESION", "30"))
