from fastapi import APIRouter, status, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from app.types import DBConnectionDep, AuthDep
from users.controllers import UserController
from users import schemas
from typing import Annotated
from app.services.auth import auth

security = HTTPBearer()

auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/users", tags=["users"])

UserControllerDep = Annotated[UserController, Depends(UserController)]

@auth_router.post("/login", response_model=schemas.TokenPairModel)
async def login(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
    return await auth.authenticate(body, db)

@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth)])
async def logout(db: DBConnectionDep, token: str = Depends(auth.oauth2_scheme)):
    return await auth.logout(token, db)

@auth_router.post("/refresh-token", response_model=schemas.TokenPairModel)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)

@user_router.get("/current", response_model=schemas.UserBaseResponse)
async def current_user(user: AuthDep):
    return user

@user_router.post("/", response_model=schemas.UserBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_user(controller: UserControllerDep, db: DBConnectionDep, body: schemas.UserCreationModel):
    existing_user = await controller.get_user_by_email(body.email, db)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exist")
    return await controller.create(body, db)
