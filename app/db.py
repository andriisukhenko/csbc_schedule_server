from typing import Generator
from app.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from datetime import datetime

engine = create_engine(settings.db.CONNECTION_STRING)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class SoftDeleteMixin(generate_soft_delete_mixin_class()): deleted_at: datetime

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