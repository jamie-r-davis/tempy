import os

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DB_URI", f"sqlite:///{os.path.join(basedir, 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
    OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = "CelloBarn <noreply@cellobarn.com>"
    SCHEDULER_API_ENABLED = True
    TEMPY_MAIL_SUBJECT_PREFIX = "[CelloBarn] "
    TEMPY_MAIL_SENDER = "CelloBarn <noreply@cellobarn.com>"
