from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from app.types import DBConnectionDep, AuthDep
from users.controllers import UserController
from users import schemas
from typing import Annotated
from app.services.auth import auth

security = HTTPBearer()

session_router = APIRouter(prefix="/session", tags=["session"])
user_router = APIRouter(prefix="/users", tags=["users"])

UserControllerDep = Annotated[UserController, Depends(UserController)]

@session_router.post("/", response_model=schemas.TokenPairModel, status_code=status.HTTP_201_CREATED)
async def create_session(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
    return await auth.authenticate(body, db)

@session_router.get("/", response_model=schemas.UserBaseResponse)
async def read_session(user: AuthDep):
    return user

@session_router.put("/", response_model=schemas.TokenPairModel)
async def update_session(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)

@session_router.delete("/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth)])
async def delete_session(db: DBConnectionDep, token: str = Depends(auth.oauth2_scheme)):
    return await auth.logout(token, db)

@user_router.post("/", response_model=schemas.UserBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(controller: UserControllerDep, db: DBConnectionDep, body: schemas.UserCreationModel):
    existing_user = await controller.get_user_by_email(body.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")
    return await controller.create(body, db)
