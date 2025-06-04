import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from confluent_kafka import Producer


load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://users_service:8000")


class Settings(BaseSettings):
    users_service_url: str
    kafka_bootstrap_servers: str

    class Config:
        env_file = ".env"


settings = Settings()

kafka_producer = Producer({
    'bootstrap.servers': settings.kafka_bootstrap_servers
})

