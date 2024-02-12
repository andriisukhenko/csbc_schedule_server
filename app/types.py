from sqlalchemy.orm import Session
from fastapi import Depends
from app.db import db
from app.services.auth import auth
from typing import Annotated

AuthDep = Annotated[auth, Depends(auth)]
DBConnectionDep = Annotated[db, Depends(db)]