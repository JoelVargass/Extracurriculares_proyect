from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError, EmailStr
from typing import List
from ..dependencies.database import get_db_connection
from ..models.club import ClubRequest
from ..utility.functions import format_errors

router = APIRouter(
    prefix="/dashboard/clubs",
    tags=["clubs"]
)

templates = Jinja2Templates(directory="src/pages/admin")
current_year = datetime.now().year

# Listar clubes
@router.get("", response_class=HTMLResponse)
async def list_clubs(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT clubs.id, clubs.club_name, clubs.description, clubs.location, clubs.init_hour, clubs.finish_hour, 
        clubs.quota, clubs.teacher_name, clubs.teacher_email, categories.title AS category
        FROM clubs
        JOIN categories ON clubs.category_id = categories.id
    """)
    clubs = cursor.fetchall()
    
    return templates.TemplateResponse("clubs/index.html.jinja", {"request": request, "clubs": clubs, "current_year": current_year})

# Crear club (Formulario)
@router.get("/create", response_class=HTMLResponse)
async def create_club(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    return templates.TemplateResponse("clubs/create.html.jinja", {"request": request, "categories": categories, "current_year": current_year})

# Guardar nuevo club
@router.post('/create', response_class=HTMLResponse)
async def save_club(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        club_data = ClubRequest(**form_dict)
        
        cursor.execute("""
            INSERT INTO clubs (club_name, description, location, init_hour, finish_hour, quota, teacher_name, teacher_email, category_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            club_data.club_name, club_data.description, club_data.location, club_data.init_hour, 
            club_data.finish_hour, club_data.quota, club_data.teacher_name, 
            club_data.teacher_email, club_data.category_id
        ))
        connection.commit()
        return RedirectResponse(url="/dashboard/clubs", status_code=303)
    
    except ValidationError as e:
        error_messages = format_errors(e.errors(), ClubRequest)
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        return templates.TemplateResponse(
            "clubs/create.html.jinja", 
            {"request": request, "errors": error_messages, "categories": categories, "current_year": current_year}
        )

    except Exception as e:
        print(f"Error al guardar el club: {e}")
        return templates.TemplateResponse(
            "clubs/create.html.jinja", 
            {"request": request, "errors": [str(e)], "categories": [], "current_year": current_year}
        )

# Ver detalles de un club
@router.get("/{club_id}", response_class=HTMLResponse)
async def get_club(request: Request, club_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT clubs.id, clubs.club_name, clubs.description, clubs.location, clubs.init_hour, clubs.finish_hour, 
        clubs.quota, clubs.teacher_name, clubs.teacher_email, categories.title AS category
        FROM clubs
        JOIN categories ON clubs.category_id = categories.id
        WHERE clubs.id = %s
    """, (club_id,))
    club = cursor.fetchone()

    if not club:
        return templates.TemplateResponse("clubs/details.html.jinja", {"request": request, "club": None, "current_year": current_year})

    return templates.TemplateResponse("clubs/details.html.jinja", {"request": request, "club": club, "current_year": current_year})

# Editar club (Formulario)
@router.get("/{club_id}/edit", response_class=HTMLResponse)
async def edit_club(request: Request, club_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT clubs.id, clubs.club_name, clubs.description, clubs.location, clubs.init_hour, clubs.finish_hour, 
        clubs.quota, clubs.teacher_name, clubs.teacher_email, categories.title AS category
        FROM clubs
        JOIN categories ON clubs.category_id = categories.id
        WHERE clubs.id = %s
    """, (club_id,))
    club = cursor.fetchone()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    
    return templates.TemplateResponse("clubs/edit.html.jinja", {"request": request, "club": club, "categories": categories, "current_year": current_year})

# Actualizar club
@router.post("/{club_id}/edit", response_class=HTMLResponse)
async def update_club(request: Request, club_id: int, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        club_data = ClubRequest(**form_dict)
        
        cursor.execute("""
            UPDATE clubs SET club_name = %s, description = %s, location = %s, init_hour = %s, 
                finish_hour = %s, quota = %s, teacher_name = %s, 
                teacher_email = %s, category_id = %s
            WHERE id = %s
        """, (
            club_data.club_name, club_data.description, club_data.location, club_data.init_hour, 
            club_data.finish_hour, club_data.quota, club_data.teacher_name, 
            club_data.teacher_email, club_data.category_id, club_id
        ))
        connection.commit()
    
        return RedirectResponse(url="/dashboard/clubs", status_code=303)
    
    except ValidationError as e:
        cursor.execute("""
            SELECT clubs.id, clubs.club_name, clubs.description, clubs.location, clubs.init_hour, clubs.finish_hour, 
            clubs.quota, clubs.teacher_name, clubs.teacher_email, categories.title AS category
            FROM clubs
            JOIN categories ON clubs.category_id = categories.id
            WHERE clubs.id = %s
        """, (club_id,))
        club = cursor.fetchone()

        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        error_messages = format_errors(e.errors(), ClubRequest)

        return templates.TemplateResponse(
            "clubs/edit.html.jinja", 
        {"request": request, "errors": error_messages, "club": club, "categories": categories, "current_year": current_year}
        )

# Eliminar club
@router.post("/{club_id}/delete", response_class=HTMLResponse)
async def delete_club(club_id: int, method: str = Form(...), db: tuple = Depends(get_db_connection)):
    if method.lower() != "delete":
        return {"status": 400, "message": "Invalid request method"}

    connection, cursor = db
    cursor.execute("SELECT * FROM clubs WHERE id = %s", (club_id,))
    club = cursor.fetchone()
    if not club:
        return {"status": 404, "message": "Club not found"}

    cursor.execute("DELETE FROM clubs WHERE id = %s", (club_id,))
    connection.commit()

    return RedirectResponse(url="/dashboard/clubs", status_code=303)
