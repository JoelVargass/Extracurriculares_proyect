from pydantic import BaseModel, ConfigDict, Field, EmailStr
from fastapi import Form

class Model(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True
    )

class LoginRequest(BaseModel):
    enrollment_number: str = Field(..., title="Matrícula", description="The user's enrollment number", min_length=8, max_length=8)
    password: str = Field(..., title="password", min_length=8, max_length=20)

class UserCreate(BaseModel):
    enrollment_number: str
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    contact: str
    role_id: int
    club_id: int = None

class User(BaseModel):
    id: int
    enrollment_number: str
    firstname: str
    lastname: str
    email: EmailStr
    contact: str
    role_id: int
    club_id: int = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    enrollment_number: str = None
    role_id: int = None
    
class UserInDB(User):
    hashed_password: str
    
