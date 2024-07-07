from fastapi import APIRouter, Depends, Request, Form, HTTPException
from ..dependencies.database import get_db_connection
from ..models.common import ApiResponse
from ..models.user import UserRequest, UserListResponse, UserResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from icecream import ic
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError, EmailStr
from ..utility.functions import format_errors
import re

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

templates = Jinja2Templates(directory="src/pages")
current_year = datetime.now().year

# Función para validar email
def is_valid_email(email):
    if not email or not isinstance(email, str):
        return False

    try:
        # Normalize the domain
        email = re.sub(r'(@)(.+)$', domain_mapper, email, flags=re.IGNORECASE)

        def domain_mapper(match):
            # Use idna encoding to convert Unicode domain names
            domain_name = match.group(2)
            return match.group(1) + domain_name.encode('idna').decode('utf-8')

    except Exception:
        return False

    try:
        return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email, flags=re.IGNORECASE))
    except re.error:
        return False

# Listar usuarios
@router.get("", response_class=HTMLResponse)
async def list_users(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("""
        SELECT users.id, users.enrollment_number, users.firstname, users.lastname, 
            users.email, users.password, users.contact, roles.title AS role
        FROM users
        JOIN roles ON users.role_id = roles.id
    """)
    users = cursor.fetchall()
    
    return templates.TemplateResponse("users/index.html.jinja", {"request": request, "users": users, "current_year": current_year})

# Crear usuario (Formulario)
@router.get("/create", response_class=HTMLResponse)
async def create_user(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"roles": roles, "current_year": current_year})

# Guardar nuevo usuario
@router.post('', response_class=HTMLResponse)
async def save_user(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        form_data = UserRequest(**form_dict)
        ic(form_data)
        
        cursor.execute(
            "INSERT INTO users (firstname, lastname, enrollment_number, email, password, contact, role_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (form_data.firstname, form_data.lastname, form_data.enrollment_number, form_data.email, form_data.password, form_data.contact, form_data.role_id)
        )
        connection.commit()
        return RedirectResponse(url="/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
                
        error_messages = format_errors(e.errors(), UserRequest)
            
        return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"errors": error_messages, "roles": roles, "current_year": current_year})


@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user(request: Request, user_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    
    cursor.execute(
        "SELECT id, enrollment_number, firstname, lastname, email, contact, password, role_id FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
        
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    return templates.TemplateResponse("users/edit.html.jinja", {"request": request, "user": user, "roles": roles, "current_year": datetime.now().year})

@router.post("/{user_id}/edit", response_class=HTMLResponse)
async def update_user(user_id: int, request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        user_data = UserRequest(**form_dict)
        ic(user_data.password)

        cursor.execute("""
            UPDATE users SET firstname = %s, lastname = %s, enrollment_number = %s, 
                email = %s, password = %s, contact = %s, role_id = %s
            WHERE id = %s
        """, (
            user_data.firstname, user_data.lastname, user_data.enrollment_number,
            user_data.email, user_data.password, user_data.contact, user_data.role_id,
            user_id
        ))
        connection.commit()
        
        return RedirectResponse(url=f"/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("""
            SELECT id, enrollment_number, firstname, lastname, email, contact, role_id FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        error_messages = format_errors(e.errors(), UserRequest)

        return templates.TemplateResponse("users/edit.html.jinja", {"request": request, "errors": error_messages, "user": user, "roles": roles, "current_year": datetime.now().year})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el usuario: {str(ex)}")


# Eliminar usuario
@router.post("/{user_id}/delete", response_class=HTMLResponse)
async def delete_user(user_id: int, method: str = Form(...), db: tuple = Depends(get_db_connection)):
    # Verificar que el método sea DELETE
    if method.lower() != "delete":
        return {"status": 400, "message": "Invalid request method"}

    connection, cursor = db
    
    # Verificar si el usuario existe
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        return {"status": 404, "message": "User not found"}

    # Eliminar el usuario
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()

    return RedirectResponse(url="/users", status_code=303)

# Manejo de errores de validación
@router.post("/handle_validation_error", response_class=HTMLResponse, include_in_schema=False)
async def handle_validation_error(request: Request, exc):
    connection, cursor = await get_db_connection()
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    return templates.TemplateResponse(
        "users/create.html.jinja",
        {
            "request": request,
            "errors": exc.errors(),
            "roles": roles,
            "current_year": current_year
        },
        status_code=400
    )
