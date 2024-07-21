import os
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from mysql.connector import connect

# ROUTERS
from .src.routers import users_router, clubs_router, categories_router, views_router, login_router, register_router, form_router

templates = Jinja2Templates(directory="src/pages/user")

app = FastAPI()
app.include_router(users_router.router)
app.include_router(clubs_router.router)
app.include_router(categories_router.router)
app.include_router(views_router.router)
app.include_router(login_router.router)
app.include_router(register_router.router)
app.include_router(form_router.router)

app.mount("/static", StaticFiles(directory="src/data/store/static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = "clave"
ALGORITHM = "HS256"

def save_image(file: UploadFile, category_id: int):
    upload_dir = f"src/data/store/static/img/category_{category_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return file.filename

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def admin_required(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token)
    if payload.get("role_id") != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    return payload

def user_required(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = decode_token(token)
    if payload.get("role_id") not in [1, 2]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    return payload

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = request.state.user if hasattr(request.state, "user") else None
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_users(request: Request, user: Annotated[dict, Depends(admin_required)]):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/user/profile", response_class=HTMLResponse)
async def user_profile(request: Request, user: Annotated[dict, Depends(user_required)]):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "title": "Internal Server Error",
            "message": str(exc)
        }
    )

@app.middleware("http")
async def create_auth_header(request: Request, call_next):
    if "Authorization" not in request.headers and "access_token" in request.cookies:
        access_token = request.cookies["access_token"]
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
        request.state.user = decode_token(access_token)
    
    if "/dashboard" in request.url.path:
        if "access_token" in request.cookies:
            access_token = request.cookies["access_token"]
            payload = decode_token(access_token)
            if payload.get("role_id") != 1:
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Access forbidden"})
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Not authenticated"})
    
    response = await call_next(request)
    return response

@app.middleware("http")
async def image_middleware(request: Request, call_next):
    if request.url.path.startswith("/static/"):
        image_path = os.path.join(os.getcwd(), request.url.path.lstrip("/"))
        if not os.path.isfile(image_path):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Image not found"})
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",  # Reemplaza con tu dominio
        "https://www.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    connection = connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = connection.cursor(dictionary=True)
    return connection, cursor

@app.get("/api/clubs")
def get_clubs():
    connection, cursor = get_db()
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    cursor.close()
    connection.close()
    return clubs
