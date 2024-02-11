from typing import Generator
from app.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

engine = create_engine(settings.db.CONNECTION_STRING)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


class DBSession:
    def __init__(self, BaseModel: DeclarativeBase, SessionLoc: sessionmaker) -> None:
        self.Base = BaseModel
        self.SessionLocal = SessionLoc
    
    def __call__(self) -> Generator[Session, None, None]:
        db: Session = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

db = DBSession(BaseModel=Base, SessionLoc=SessionLocal)