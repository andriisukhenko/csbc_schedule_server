from sqlalchemy.orm import Session
from app.db import db as BDMaker
from users.models import Token
import schedule.models

db: Session = next(BDMaker())

user = db.query(Token).all()
print(user)
