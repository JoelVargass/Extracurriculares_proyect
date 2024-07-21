import os
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError
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

@router.get("/clubs")
async def get_clubs(db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    return JSONResponse(content=clubs)

@router.get("", response_class=HTMLResponse)
async def list_clubs(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT * FROM clubs
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
async def save_club(request: Request, db: tuple = Depends(get_db_connection), image: UploadFile = File(None)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        club_data = ClubRequest(**form_dict)
        
        # Guardar la imagen si se proporciona
        image_path = None
        if image:
            image_dir = "static/img"  # Directorio relativo
            image_path = os.path.join(image_dir, image.filename)
            
            # Crear el directorio si no existe
            os.makedirs(image_dir, exist_ok=True)
            
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())

            # Usar solo la ruta relativa
            image_path = os.path.join("img", image.filename)
        
        cursor.execute("""
            INSERT INTO clubs (club_name, description, location, init_hour, finish_hour, quota, teacher_name, teacher_email, category_id, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            club_data.club_name, club_data.description, club_data.location, club_data.init_hour, 
            club_data.finish_hour, club_data.quota, club_data.teacher_name, 
            club_data.teacher_email, club_data.category_id, image_path
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

@router.get("/{club_id}/edit", response_class=HTMLResponse)
async def edit_club(request: Request, club_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT clubs.id, clubs.club_name, clubs.description, clubs.location, clubs.init_hour, clubs.finish_hour,
            clubs.quota, clubs.teacher_name, clubs.teacher_email, clubs.category_id, categories.title AS category
        FROM clubs
        JOIN categories ON clubs.category_id = categories.id
        WHERE clubs.id = %s
    """, (club_id,))
    club = cursor.fetchone()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    return templates.TemplateResponse(
        "clubs/edit.html.jinja",
        {"request": request, "club": club, "categories": categories, "current_year": current_year}
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
