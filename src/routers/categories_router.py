from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from ..dependencies.database import get_db_connection
from ..models.categories import CategoryRequest, CategoryResponse, CategoryListResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from ..utility.functions import format_errors
import shutil
import os

router = APIRouter(
    prefix="/dashboard/categories",
    tags=["categories"]
)

templates = Jinja2Templates(directory="src/pages/admin")
current_year = datetime.now().year

# Listar categorías
@router.get("", response_class=HTMLResponse)
async def list_categories(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT id, title, description, image_path
        FROM categories
    """)
    categories = cursor.fetchall()
    return templates.TemplateResponse("categories/index.html.jinja", {"request": request, "categories": categories, "current_year": current_year})

# Crear categoría (Formulario)
@router.get("/create", response_class=HTMLResponse)
async def create_category(request: Request):
    return templates.TemplateResponse("categories/create.html.jinja", {"request": request, "current_year": current_year})

# Guardar categoría
@router.post('/create', response_class=HTMLResponse)
async def save_category(request: Request, file: UploadFile = File(...), db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        category_data = CategoryRequest(**form_dict)

        # Guardar la imagen en el servidor
        if file:
            upload_folder = f"src/data/store/categories/{category_data.title}"
            os.makedirs(upload_folder, exist_ok=True)

            file_location = os.path.join(upload_folder, file.filename)
            
            # Guardar la imagen
            with open(file_location, "wb") as image:
                shutil.copyfileobj(file.file, image)
                
            # Guardar la ruta de la imagen relativa en la base de datos
            file_location = os.path.relpath(file_location, "src/data/store")

        # Insertar datos de la categoría en la base de datos
        cursor.execute("""
            INSERT INTO categories (title, description, image_path)
            VALUES (%s, %s, %s)
        """, (
            category_data.title, category_data.description, file_location
        ))
        connection.commit()

        return RedirectResponse(url="/dashboard/categories", status_code=303)

    except Exception as e:
        error_messages = format_errors(e.errors(), CategoryRequest)
        return templates.TemplateResponse(
            "categories/create.html.jinja",
            {"request": request, "errors": error_messages, "current_year": current_year}
        )

# Ver detalles de una categoría
@router.get("/{category_id}", response_class=HTMLResponse)
async def get_category(request: Request, category_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT id, title, description
        FROM categories
        WHERE id = %s
    """, (category_id,))
    category = cursor.fetchone()
    
    return templates.TemplateResponse("categories/details.html.jinja", {"request": request, "category": category, "current_year": current_year})

# Editar categoría (Formulario)
@router.get("/{category_id}/edit", response_class=HTMLResponse)
async def edit_category(request: Request, category_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT id, title, description, image_path
        FROM categories
        WHERE id = %s
    """, (category_id,))
    category = cursor.fetchone()
    
    return templates.TemplateResponse("categories/edit.html.jinja", {"request": request, "category": category, "current_year": current_year})

# Actualizar categoría
@router.post("/{category_id}", response_class=HTMLResponse)
async def update_category(
    request: Request,
    category_id: int,
    db: tuple = Depends(get_db_connection),
    file: UploadFile = File(None)
):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        category_data = CategoryRequest(**form_dict)

        # Obtener la ruta actual de la imagen
        cursor.execute("""
            SELECT image_path
            FROM categories
            WHERE id = %s
        """, (category_id,))
        current_image_path = cursor.fetchone()["image_path"]

        # Manejar la nueva imagen si se proporciona
        if file and file.filename:
            upload_folder = f"src/data/store/categories/{category_data.title}"
            os.makedirs(upload_folder, exist_ok=True)

            new_file_location = os.path.join(upload_folder, file.filename)

            # Guardar la nueva imagen
            with open(new_file_location, "wb") as image:
                shutil.copyfileobj(file.file, image)

            # Eliminar la imagen anterior si existe
            if current_image_path and os.path.exists(current_image_path):
                os.remove(current_image_path)

            new_file_location = os.path.relpath(new_file_location, "src/data/store")
        else:
            new_file_location = current_image_path

        cursor.execute("""
            UPDATE categories SET title = %s, description = %s, image_path = %s
            WHERE id = %s
        """, (
            category_data.title, category_data.description, new_file_location, category_id
        ))
        connection.commit()

        return RedirectResponse(url="/dashboard/categories", status_code=303)

    except ValidationError as e:
        cursor.execute("""
            SELECT id, title, description, image_path
            FROM categories
            WHERE id = %s
        """, (category_id,))
        category = cursor.fetchone()
        error_messages = format_errors(e.errors(), CategoryRequest)

        return templates.TemplateResponse(
            "categories/edit.html.jinja",
            {"request": request, "errors": error_messages, "category": category, "current_year": current_year}
        )
    
# Eliminar categoría
@router.post("/{category_id}/delete", response_class=HTMLResponse)
async def delete_category(category_id: int, method: str = Form(...), db: tuple = Depends(get_db_connection)):
    if method.lower() != "delete":
        return {"status": 400, "message": "Invalid request method"}

    connection, cursor = db
    cursor.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()
    if not category:
        return {"status": 404, "message": "Category not found"}

    cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    connection.commit()

    return RedirectResponse(url="/dashboard/categories", status_code=303)
