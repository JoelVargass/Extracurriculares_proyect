from typing import Annotated
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

# ROUTERS
from .src.routers import users_router
from .src.routers import clubs_router
from .src.routers import categories_router
from .src.routers import views_router
from .src.routers import login_router

templates = Jinja2Templates(directory="src/pages/user")

app = FastAPI()
app.include_router(users_router.router)
app.include_router(clubs_router.router)
app.include_router(categories_router.router)
app.include_router(views_router.router)
app.include_router(login_router.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = "clave"
ALGORITHM = "HS256"

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

@app.get("/dashboard/users", response_class=HTMLResponse)
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
    '''
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    '''
    if "Authorization" not in request.headers and "access_token" in request.cookies:
        access_token = request.cookies["access_token"]
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
        
        request.state.user = decode_token(access_token)  # Almacena el payload del token en request.state.user

    # Verificar el rol del usuario para restringir acceso a /dashboard
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