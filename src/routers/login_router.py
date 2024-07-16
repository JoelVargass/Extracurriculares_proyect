from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import jwt
from ..data.database import get_db, close_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = "clave"
ALGORITHM = "HS256"

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        connection, cursor = get_db()
        cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (data["username"],))
        user = cursor.fetchone()
        close_db(connection)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    connection, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (form_data.username,))
    user = cursor.fetchone()
    close_db(connection)
    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token = encode_token({"username": user["enrollment_number"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user
