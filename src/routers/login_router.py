from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import jwt

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

users = {
    "pablo": {"username": "pablo", "email": "pablo@gmail.com", "password": "fakepass"},
    "user2": {"username": "user2", "email": "user2@gmail.com", "password": "user2"}
}

SECRET_KEY = "clave"
ALGORITHM = "HS256"

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = users.get(data["username"])
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.post("/login")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = users.get(form_data.username)
    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token = encode_token({"username": user["username"], "email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users/profile")
def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user
