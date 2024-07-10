from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

# Configuración de Jinja2Templates para las páginas de usuario
templates = Jinja2Templates(directory="src/pages/user")

# Rutas para las vistas de usuario
@router.get("/culturales", response_class=HTMLResponse)
async def cultural_page(request: Request):
    return templates.TemplateResponse("culturales.html", {"request": request})

@router.get("/deportivos", response_class=HTMLResponse)
async def deportivos_page(request: Request):
    return templates.TemplateResponse("deportivos.html", {"request": request})

@router.get("/personalizados", response_class=HTMLResponse)
async def personalized_page(request: Request):
    return templates.TemplateResponse("personalizados.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
