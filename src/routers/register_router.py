from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
from ..data.database import get_db, close_db

router = APIRouter()

SECRET_KEY = "clave"
ALGORITHM = "HS256"

class UserRegisterRequest(BaseModel):
    enrollment_number: str
    firstname: str
    lastname: str
    email: str
    institutional_email: Optional[str]
    password: str
    contact: str
    curp: Optional[str]
    date_of_birth: Optional[str]
    nationality: Optional[str]
    degree_id: int  # Agregamos degree_id aquí

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/user/register")
async def register_user(request: UserRegisterRequest):
    connection, cursor = get_db()
    
    cursor.execute("SELECT * FROM users WHERE enrollment_number = %s OR email = %s", 
                (request.enrollment_number, request.email))
    user = cursor.fetchone()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    cursor.execute(
        """
        INSERT INTO users (enrollment_number, firstname, lastname, email, institutional_email, 
                        password, contact, role_id, curp, date_of_birth, nationality, degree_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            request.enrollment_number, request.firstname, request.lastname, request.email,
            request.institutional_email, request.password, request.contact, 2,  # Role ID 2 for 'student'
            request.curp, request.date_of_birth, request.nationality, request.degree_id
        )
    )
    connection.commit()

    cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (request.enrollment_number,))
    new_user = cursor.fetchone()
    
    token = encode_token({
        "user_id": new_user["id"],
        "enrollment_number": new_user["enrollment_number"],
        "email": new_user["email"],
        "role_id": new_user["role_id"]
    })

    close_db(connection)
    return {"token": token}

# Código restante de tu archivo FastAPI
