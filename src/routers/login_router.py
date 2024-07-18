from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from ..data.database import get_db, close_db

router = APIRouter()

templates = Jinja2Templates(directory="src/pages/user")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = "clave"
ALGORITHM = "HS256"

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        connection, cursor = get_db()
        cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (data["username"],))
        user = cursor.fetchone()
        close_db(connection)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def admin_required(user: dict = Depends(decode_token)):
    if user["role_id"] != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    return user

@router.get("/user/login")
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html.jinja", {"request": request})

@router.post("/user/login")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    connection, cursor = get_db()
    cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (form_data.username,))
    user = cursor.fetchone()
    close_db(connection)
    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    token = encode_token({"username": user["enrollment_number"], "email": user["email"], "role_id": user["role_id"]})
    response.set_cookie(key="access_token", value=token, httponly=True)
    if user["role_id"] == 1:  # Admin
        return {"redirect_url": "/dashboard/users"}
    return {"redirect_url": "/"}

@router.get("/user/profile")
async def profile(request: Request, my_user: dict = Depends(decode_token)):
    return templates.TemplateResponse("home.html", {"request": request, "user": my_user})

@router.get("/dashboard/users")
async def dashboard_users(request: Request, my_user: dict = Depends(admin_required)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": my_user})