from fastapi import APIRouter, Depends, Request, Form, HTTPException
from ..dependencies.database import get_db_connection
from ..models.common import ApiResponse
from ..models.user import UserRequest, UserListResponse, UserResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError, EmailStr
from ..utility.functions import format_errors
import re

router = APIRouter(
    prefix="/dashboard/users", 
    tags=["users"]
)

templates = Jinja2Templates(directory="src/pages/admin")
current_year = datetime.now().year

# Función para validar email
def is_valid_email(email):
    if not email or not isinstance(email, str):
        return False
    try:
        def domain_mapper(match):
            domain_name = match.group(2)
            return match.group(1) + domain_name.encode('idna').decode('utf-8')
        
        email = re.sub(r'(@)(.+)$', domain_mapper, email, flags=re.IGNORECASE)
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
            users.email, users.institutional_email, users.curp, users.date_of_birth, 
            users.nationality, users.contact, roles.title AS role
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
    
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()
    
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()

    return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"roles": roles, "degrees": degrees, "clubs": clubs, "current_year": current_year})

# Guardar nuevo usuario
@router.post("", response_class=HTMLResponse)
async def save_user(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        form_data = UserRequest(**form_dict)
        
        cursor.execute(
            "INSERT INTO users (enrollment_number, firstname, lastname, email, institutional_email, curp, date_of_birth, nationality, password, contact, role_id, club_id, degree_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (form_data.enrollment_number, form_data.firstname, form_data.lastname, form_data.email, form_data.institutional_email, form_data.curp, form_data.date_of_birth, form_data.nationality, form_data.password, form_data.contact, form_data.role_id, form_data.club_id, form_data.degree_id)
        )
        connection.commit()
        return RedirectResponse(url="/dashboard/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM university_degrees")
        degrees = cursor.fetchall()
        
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        
        error_messages = format_errors(e.errors(), UserRequest)
        
        return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"errors": error_messages, "roles": roles, "degrees": degrees, "clubs": clubs, "current_year": current_year})

# Editar usuario (Formulario GET)
@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user(request: Request, user_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    
    cursor.execute(
        "SELECT id, enrollment_number, firstname, lastname, email, institutional_email, curp, date_of_birth, nationality, contact, role_id, club_id, degree_id FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
        
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()
    
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse("users/edit.html.jinja", {"request": request, "user": user, "roles": roles, "degrees": degrees, "clubs": clubs, "current_year": datetime.now().year})

# Actualizar usuario
@router.post("/{user_id}/edit", response_class=HTMLResponse)
async def update_user(user_id: int, request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        user_data = UserRequest(**form_dict)

        cursor.execute("""
            UPDATE users SET enrollment_number = %s, firstname = %s, lastname = %s, 
                email = %s, institutional_email = %s, curp = %s, date_of_birth = %s, 
                nationality = %s, password = %s, contact = %s, role_id = %s, club_id = %s, degree_id = %s
            WHERE id = %s
        """, (
            user_data.enrollment_number, user_data.firstname, user_data.lastname,
            user_data.email, user_data.institutional_email, user_data.curp,
            user_data.date_of_birth, user_data.nationality, user_data.password,
            user_data.contact, user_data.role_id, user_data.club_id, user_data.degree_id,
            user_id
        ))
        connection.commit()
        
        return RedirectResponse(url="/dashboard/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("""
            SELECT id, enrollment_number, firstname, lastname, email, institutional_email, curp, date_of_birth, nationality, contact, role_id, club_id, degree_id FROM users WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()

        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM university_degrees")
        degrees = cursor.fetchall()
        
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        
        error_messages = format_errors(e.errors(), UserRequest)

        return templates.TemplateResponse("users/edit.html.jinja", {"request": request, "errors": error_messages, "user": user, "roles": roles, "degrees": degrees, "clubs": clubs, "current_year": datetime.now().year})

    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el usuario: {str(ex)}")

# Eliminar usuario
@router.post("/{user_id}/delete", response_class=HTMLResponse)
async def delete_user(user_id: int, method: str = Form(...), db: tuple = Depends(get_db_connection)):
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

    return RedirectResponse(url="/dashboard/users", status_code=303)

# Manejo de errores de validación
@router.post("/handle_validation_error", response_class=HTMLResponse, include_in_schema=False)
async def handle_validation_error(request: Request, exc):
    connection, cursor = await get_db_connection()
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()
    
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    
    return templates.TemplateResponse(
        "users/create.html.jinja",
        {
            "request": request,
            "errors": exc.errors(),
            "roles": roles,
            "degrees": degrees,
            "clubs": clubs,
            "current_year": current_year
        }
    )
