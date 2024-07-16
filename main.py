from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import jwt

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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
    status_code=500,
        content= {
        "title": "Internal Server Error",
            "message": str(exc)
        }
    )


@app.middleware("http")
async def create_auth_header(
    request: Request,
    call_next,):
    '''
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    requests y responses
    exists!)
    '''
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies
        ):
        access_token = request.cookies["Authorization"]
        
        
        user_data = jwt.decode(access_token, "password")
        
        
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies
        ): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                f"Bearer 12345".encode(),
            )
        )
        
    
    response = await call_next(request)
    
    
    return response   