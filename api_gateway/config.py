import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from confluent_kafka import Producer

kafka_producer = Producer({
    'bootstrap.servers': 'kafka:9092'
})

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://users_service:8000")


class Settings(BaseSettings):
    users_service_url: str

    class Config:
        env_file = ".env"


settings = Settings()
