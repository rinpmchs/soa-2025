import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from confluent_kafka import Producer

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://users_service:8000")


class Settings(BaseSettings):
    users_service_url:       str = Field(..., env="USER_SERVICE_URL")
    statistics_service_url:  str = Field(..., env="STATISTICS_SERVICE_URL")
    kafka_bootstrap_servers: str = Field(..., env="KAFKA_BOOTSTRAP_SERVERS")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

kafka_producer = Producer({
    'bootstrap.servers': settings.kafka_bootstrap_servers
})