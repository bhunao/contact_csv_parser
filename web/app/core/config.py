from pydantic_settings import BaseSettings
from jinja2_fragments.fastapi import Jinja2Blocks


class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str = "REPLACE"
    MONGO_INITDB_ROOT_PASSWORD: str = "REPLACE"
    TEMPLATES: Jinja2Blocks = Jinja2Blocks(directory="templates")


settings = Settings()
