from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError
from typing import List
import os
from ..dependencies.database import get_db_connection
from ..models.club import ClubRequest
from ..utility.functions import format_errors

router = APIRouter(
    prefix="/dashboard/clubs",
    tags=["clubs"]
)

templates = Jinja2Templates(directory="src/pages/admin")
current_year = datetime.now().year

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
            category_id = form_dict.get("category_id")
            if not category_id:
                raise HTTPException(status_code=400, detail="Category ID is required for image upload")

            category_dir = f"src/data/store/categories/{category_id}"
            os.makedirs(category_dir, exist_ok=True)
            image_path = f"{category_dir}/{image.filename}"
            
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())

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

@router.post("/{club_id}/edit", response_class=HTMLResponse)
async def update_club(request: Request, club_id: int, db: tuple = Depends(get_db_connection), image: UploadFile = File(None)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        club_data = ClubRequest(**form_dict)
        
        # Obtener la imagen actual para mantenerla si no se sube una nueva
        cursor.execute("SELECT image_path FROM clubs WHERE id = %s", (club_id,))
        current_image_path = cursor.fetchone()[0]

        image_path = current_image_path
        if image:
            category_id = form_dict.get("category_id")
            if not category_id:
                raise HTTPException(status_code=400, detail="Category ID is required for image upload")

            category_dir = f"src/data/store/categories/{category_id}"
            os.makedirs(category_dir, exist_ok=True)
            image_path = f"{category_dir}/{image.filename}"
            
            with open(image_path, "wb") as buffer:
                buffer.write(await image.read())

        cursor.execute("""
            UPDATE clubs SET club_name = %s, description = %s, location = %s, init_hour = %s, 
                finish_hour = %s, quota = %s, teacher_name = %s, 
                teacher_email = %s, category_id = %s, image_path = %s
            WHERE id = %s
        """, (
            club_data.club_name, club_data.description, club_data.location, club_data.init_hour, 
            club_data.finish_hour, club_data.quota, club_data.teacher_name, 
            club_data.teacher_email, club_data.category_id, image_path, club_id
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
