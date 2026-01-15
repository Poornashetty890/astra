import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    uri:str
    environment:str
    service_name: str
    mqtt_broker: str
    mqtt_port: str
    mqtt_username: str
    mqtt_password: str
    secret_key: str

    class Config:
        env_file = os.getcwd() + "/.env"

@lru_cache()
def get_settings():
    for k, v in Settings():
        os.environ[str(k).upper()] = v

    return Settings()