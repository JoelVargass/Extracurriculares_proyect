from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..dependencies.services import get_user_info
from icecream import ic

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

templates = Jinja2Templates(directory="src/pages/user")

# Rutas para las vistas de usuario
@router.get("/culturales", response_class=HTMLResponse)
async def cultural_page(request: Request, user: dict | None = Depends(get_user_info)):

    ic(user)

    return templates.TemplateResponse("culturales.html", {"request": request, "user": user})

@router.get("/deportivos", response_class=HTMLResponse)
async def deportivos_page(request: Request):
    return templates.TemplateResponse("deportivos.html", {"request": request})

@router.get("/personalizados", response_class=HTMLResponse)
async def personalized_page(request: Request):
    return templates.TemplateResponse("personalizados.html", {"request": request})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

@router.get("/support_email", response_class=HTMLResponse)
async def support_email_page(request: Request):
    return templates.TemplateResponse("support_email.html", {"request": request})

@router.get("/inscription", response_class=HTMLResponse)
async def submit_registration_form(request: Request):
    return templates.TemplateResponse("formulario.html.jinja", {"request": request})

@router.get("/login_pass", response_class=HTMLResponse)
async def recover_pass_page(request: Request):
    return templates.TemplateResponse("login_pass.html.jinja", {"request": request})