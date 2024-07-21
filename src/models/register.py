from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreateRequest(BaseModel):
    firstname: str
    lastname: str
    enrollment_number: str
    email: EmailStr
    institutional_email: EmailStr
    curp: str
    date_of_birth: date
    nationality: str
    password: str
    contact: str
    degree_id: int