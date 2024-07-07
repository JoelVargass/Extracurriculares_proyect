from fastapi import APIRouter, Depends, Request, Form
from ..dependencies.database import get_db_connection
from ..models.common import ApiResponse
from ..models.categories import CategoryRequest, CategoryResponse, CategoryListResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from icecream import ic
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from ..utility.functions import format_errors

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

templates = Jinja2Templates(directory="src/pages")
current_year = datetime.now().year

# Listar categorías
@router.get("", response_class=HTMLResponse)
async def list_categories(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT id, title, description
        FROM categories
    """)
    categories = cursor.fetchall()
    ic(categories)
    return templates.TemplateResponse("categories/index.html.jinja", {"request": request, "categories": categories, "current_year": current_year})

# Crear categoría (Formulario)
@router.get("/create", response_class=HTMLResponse)
async def create_category(request: Request):
    return templates.TemplateResponse("categories/create.html.jinja", {"request": request, "current_year": current_year})

# Guardar nueva categoría
@router.post('/create', response_class=HTMLResponse)
async def save_category(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        category_data = CategoryRequest(**form_dict)
        
        cursor.execute("""
            INSERT INTO categories (title, description)
            VALUES (%s, %s)
        """, (
            category_data.title, category_data.description
        ))
        connection.commit()
        return RedirectResponse(url="/categories", status_code=303)
    
    except ValidationError as e:
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
        SELECT id, title, description
        FROM categories
        WHERE id = %s
    """, (category_id,))
    category = cursor.fetchone()
    
    return templates.TemplateResponse("categories/edit.html.jinja", {"request": request, "category": category, "current_year": current_year})

# Actualizar categoría
@router.post("/{category_id}", response_class=HTMLResponse)
async def update_category(request: Request, category_id: int, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        category_data = CategoryRequest(**form_dict)
        
        cursor.execute("""
            UPDATE categories SET title = %s, description = %s
            WHERE id = %s
        """, (
            category_data.title, category_data.description, category_id
        ))
        connection.commit()
    
        return RedirectResponse(url="/categories", status_code=303)
    
    except ValidationError as e:
        cursor.execute("""
            SELECT id, title, description
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

    return RedirectResponse(url="/categories", status_code=303)
