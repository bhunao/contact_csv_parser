from pydantic_settings import BaseSettings
from fastapi.templating import Jinja2Templates


class Settings(BaseSettings):
    MONGO_INITDB_ROOT_USERNAME: str = "REPLACE"
    MONGO_INITDB_ROOT_PASSWORD: str = "REPLACE"
    TEMPLATES: Jinja2Templates = Jinja2Templates(directory="templates")


settings = Settings()
