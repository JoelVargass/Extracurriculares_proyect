from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

# ROUTERS
from .src.routers import users_router
from .src.routers import clubs_router
from .src.routers import categories_router

templates = Jinja2Templates(directory="src/pages/user")

app = FastAPI()
app.include_router(users_router.router)
app.include_router(clubs_router.router)
app.include_router(categories_router.router)

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