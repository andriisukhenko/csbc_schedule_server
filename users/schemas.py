from pydantic import BaseModel, Field, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from app.settings import settings
from typing import Optional

PhoneNumber.phone_format = settings.app.PHONE_FORMAT

class UserCreationModel(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=16, pattern="^\\w+$")
    password: str = Field(min_length=8, max_length=50)
    phone_number: Optional[PhoneNumber] = Field(None, max_length=13)
    first_name: str = Field(min_length=1, max_length=20)
    second_name: Optional[str] = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)

class UserModel(BaseModel):
    id: int
    email: EmailStr
    username: str = Field(min_length=5, max_length=16, pattern="^\\w+$")
    phone_number: Optional[PhoneNumber] = Field(None, max_length=13)
    first_name: str = Field(min_length=1, max_length=20)
    second_name: Optional[str] = Field(min_length=1, max_length=20)
    last_name: str = Field(min_length=1, max_length=20)

class UserBaseResponse(UserModel):
    id: int
    password: str = Field(max_length=250)

    class Config:
        from_attributes = True
    

class TokenModel(BaseModel):
    token: str
    expired_at: str

class TokenPairModel(BaseModel):
    access: TokenModel
    refresh: TokenModel
    type: str = "bearer"