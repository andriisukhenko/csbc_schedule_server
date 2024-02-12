from fastapi import HTTPException, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Optional
from enum import Enum
from app.settings import settings, TokenSettings
from app.db import db
from users.models import User, Token as TokenDBModel
from users import schemas
from dataclasses import dataclass
from typing import Callable, List

class TokenScopes(Enum):
    ACCESS='access_token'
    REFRESH='refresh_token'

class Password:
    def __init__(self, pwd_context: CryptContext):
        self.pwd_context = pwd_context

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify(self, password: str, hash: str) -> bool:
        return self.pwd_context.verify(password, hash)
    
@dataclass
class TokenCoder:
    encode: Callable[[dict, str, str], str]
    decode: Callable[[str, str, List[str]], dict]
    error: Exception
    
class Token:
    def __init__(self, secret: str, config: TokenSettings, coder: TokenCoder) -> None:
        self.config = config
        self.coder = coder
        self.secret = secret
         
    async def create(self, data: dict, scope: TokenScopes, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        to_encode_data = data.copy()
        now = datetime.utcnow()
        expired = now + timedelta(minutes=expires_delta) if expires_delta else now + timedelta(minutes=self.config.DEFAULT_EXPIRED)
        to_encode_data.update({"iat": now, "exp": expired, "scope": scope.value})
        token = self.coder.encode(to_encode_data, self.secret, algorithm=self.config.ALGORITHM)
        return { "token": token, "expired_at": expired, "scope": scope.value }
    
    async def decode(self, token: str, scope: TokenScopes) -> dict:
        try:
            payload = self.coder.decode(token, self.secret, algorithms=[self.config.ALGORITHM])
            if payload['scope'] == scope.value:
                return payload
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except self.coder.error as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def create_access(self, data: dict, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        return await self.create(data=data, scope=TokenScopes.ACCESS, expires_delta=expires_delta or self.config.ACCESS_EXPIRED)
    
    async def create_refresh(self, data: dict, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        return await self.create(data=data, scope=TokenScopes.REFRESH, expires_delta=expires_delta or self.config.REFRESH_EXPIRED)

    async def decode_access(self, token: str) -> dict:
        return await self.decode(token, TokenScopes.ACCESS)

    async def decode_refresh(self, token: str) -> dict:
        return await self.decode(token, TokenScopes.REFRESH)

class Auth:
    oauth2_scheme = OAuth2PasswordBearer(settings.token.URL)
    user_model = User
    tokens_model = TokenDBModel
    invalid_credential_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    invalid_refresh_token_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    credentionals_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    def __init__(self, password: Password, token: Token) -> None:
        self.password = password
        self.token = token

    def validate(self, user: user_model | None, credentials: OAuth2PasswordRequestForm) -> bool:
        if user is None:
            return False
        if not self.password.verify(credentials.password, user.password):
            return False
        return True
    
    async def refresh(self, refres_token_str: str, db: Session) -> schemas.TokenPairModel:
        payload = await self.token.decode_refresh(refres_token_str)
        refres_token = db.query(self.tokens_model).filter(
            self.tokens_model.token==refres_token_str,
            self.tokens_model.scope==TokenScopes.REFRESH.value
            ).options(joinedload(self.tokens_model.user)).first()
        user = await self.__get_user(payload["email"], db)
        if refres_token:
            db.delete(refres_token)
            db.commit()
        print(user, refres_token)
        if user is None or refres_token is None or refres_token.user != user:
            raise self.credentionals_exception
        return await self.__generate_tokens(user, db)
        
    async def authenticate(self, credentials: OAuth2PasswordRequestForm, db: Session) -> schemas.TokenModel:
        user = await self.__get_user(credentials.username, db)
        if not self.validate(user, credentials):
            raise self.invalid_credential_error
        return await self.__generate_tokens(user, db)
    
    async def __generate_tokens(self, user: user_model, db: Session) -> schemas.TokenPairModel:
        access_token_data = await self.token.create_access({"email": user.email})
        refresh_token_data = await self.token.create_refresh({"email": user.email})
        refresh_token = self.tokens_model(**refresh_token_data)
        access_token = self.tokens_model(**access_token_data)
        user.tokens.append(refresh_token)
        user.tokens.append(access_token)
        db.commit()
        return { 
            "access": { "token": access_token.token, "expired": access_token.expired_at }, 
            "refresh": { "token": refresh_token.token, "expired": refresh_token.expired_at }, 
            "type": "bearer"
        }
        
    async def __get_user(self, username: str, db: Session) -> user_model | None:
        return db.query(self.user_model).filter(or_(
            self.user_model.email == username,
            self.user_model.username == username,
            self.user_model.phone_number == username
            )).first()

    async def __call__(self, token: str = Depends(oauth2_scheme), db: Session = Depends(db)) -> user_model:
        pyload = await self.token.decode_access(token)
        if pyload["email"] is None:
            raise self.credentionals_exception
        user = await self.__get_user(pyload["email"], db)
        stored_token = db.query(self.tokens_model).filter(self.user_model == user, self.tokens_model.scope == TokenScopes.ACCESS.value).first()
        if stored_token is None:
            raise self.credentionals_exception
        return user
        

auth: Auth = Auth(
    password=Password(CryptContext(schemes=['bcrypt'], deprecated='auto')),
    token=Token(secret=settings.app.SECRET, config=settings.token, coder=TokenCoder(encode=jwt.encode, decode=jwt.decode, error=JWTError))
)