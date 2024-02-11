from dotenv import load_dotenv
from dataclasses import dataclass
import os

# load env variables
load_dotenv()

# APP VARIABLES
@dataclass(frozen=True)
class APPSettings:
    HOST: str = os.getenv("APP_HOST")
    PORT: int = os.getenv("APP_PORT")
    SECRET: str = os.getenv("APP_SECRET")
    URL_PREFIX: str = '/api'

# DB VARIABLES
@dataclass(frozen=True)
class DBSettings:
    ENGINE: str = os.getenv("DB_ENGINE")
    NAME: str = os.getenv("DB_NAME")
    USER: str = os.getenv("DB_USER")
    PASSWORD: str = os.getenv("DB_PASSWORD")
    HOST: str = os.getenv("DB_HOST")
    PORT: str = int(os.getenv("DB_PORT"))

    @property
    def CONNECTION_STRING(self):
        return f"{self.ENGINE}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

# Setting collection
@dataclass(frozen=True)
class Settings:
    app: APPSettings = APPSettings()
    db: DBSettings = DBSettings()

settings: Settings = Settings() 
