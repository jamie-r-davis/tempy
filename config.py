import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    BUCKET_KEY = os.getenv("BUCKET_KEY")
    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SENSOR_LOCATION_NAME = os.getenv("SENSOR_LOCATION_NAME")
    READING_INTERVAL = 300  # seconds between readings
