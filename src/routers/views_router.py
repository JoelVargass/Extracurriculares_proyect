from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..dependencies.services import get_user_info

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

templates = Jinja2Templates(directory="src/pages/user")

# Rutas para las vistas de usuario

@router.get("", response_class=HTMLResponse)
async def home_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@router.get("/culturales", response_class=HTMLResponse)
async def cultural_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("culturales.html", {"request": request, "user": user})

@router.get("/deportivos", response_class=HTMLResponse)
async def deportivos_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("deportivos.html", {"request": request, "user": user})

@router.get("/personalizados", response_class=HTMLResponse)
async def personalized_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("personalizados.html", {"request": request, "user": user})

@router.get("/support", response_class=HTMLResponse)
async def support_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("support.html", {"request": request, "user": user})

@router.get("/support_email", response_class=HTMLResponse)
async def support_email_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("support_email.html", {"request": request, "user": user})

@router.get("/login_pass", response_class=HTMLResponse)
async def recover_pass_page(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("login_pass.html.jinja", {"request": request, "user": user})

@router.get("/info", response_class=HTMLResponse)
async def profile_info(request: Request, user: dict | None = Depends(get_user_info)):
    return templates.TemplateResponse("perfil.html.jinja", {"request": request, "user": user})