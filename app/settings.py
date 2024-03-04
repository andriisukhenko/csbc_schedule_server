from dotenv import load_dotenv
from dataclasses import dataclass
from pathlib import Path
import os

# load env variables
load_dotenv()

# APP VARIABLES
@dataclass(frozen=True)
class APPSettings:
    VERSION: str = os.getenv("APP_VERSION")
    NAME: str = os.getenv("APP_NAME")
    HOST: str = os.getenv("APP_HOST")
    PORT: int = int(os.getenv("APP_PORT", '8000'))
    SECRET: str = os.getenv("APP_SECRET")
    ROOT: str = Path(__file__).parent.parent
    ENV: str = os.getenv("APP_ENV")
    URL_PREFIX: str = '/api'
    PHONE_FORMAT: str = 'E164'
    DATE_FORMAT: str = '%d-%m-%Y %H:%M:%S'

# DB VARIABLES
@dataclass(frozen=True)
class DBSettings:
    ENGINE: str = os.getenv("DB_ENGINE")
    NAME: str = os.getenv("DB_NAME")
    USER: str = os.getenv("DB_USER")
    PASSWORD: str = os.getenv("DB_PASSWORD")
    HOST: str = os.getenv("DB_HOST")
    PORT: int = int(os.getenv("DB_PORT", '5432'))

    @property
    def CONNECTION_STRING(self):
        return f"{self.ENGINE}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

# TOKEN VARIABLES
@dataclass
class TokenSettings:
    ALGORITHM: str = "HS256"
    DEFAULT_EXPIRED: int = 120
    ACCESS_EXPIRED: int = 15
    REFRESH_EXPIRED: int = 7 * 1440
    URL: str = '/api/session/'

# Setting collection
@dataclass(frozen=True)
class Settings:
    app: APPSettings = APPSettings()
    db: DBSettings = DBSettings()
    token: TokenSettings = TokenSettings

settings: Settings = Settings() 
