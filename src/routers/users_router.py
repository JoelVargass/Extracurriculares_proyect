from fastapi import APIRouter, Depends, Request, HTTPException
from ..dependencies.database import get_db_connection
from ..models.common import ApiResponse
from ..models.user import UserRequest, UserListResponse, UserResponse, EnrollmentRequest
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError
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
            users.nationality, users.contact, roles.title AS role, users.club_id, users.degree_id
        FROM users
        JOIN roles ON users.role_id = roles.id
        LEFT JOIN university_degrees ON users.degree_id = university_degrees.id
    """)
    users = cursor.fetchall()
    
    return templates.TemplateResponse("users/index.html.jinja", {"request": request, "users": users, "current_year": current_year})

# Crear usuario (Formulario)
@router.get("/create", response_class=HTMLResponse)
async def create_user(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()
    
    return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"roles": roles, "clubs": clubs, "degrees": degrees, "current_year": current_year})

# Guardar nuevo usuario
@router.post("", response_class=HTMLResponse)
async def save_user(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        form_data = UserRequest(**form_dict)
        
        cursor.execute(
            "INSERT INTO users (firstname, lastname, enrollment_number, email, institutional_email, curp, date_of_birth, nationality, password, contact, role_id, club_id, degree_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (form_data.firstname, form_data.lastname, form_data.enrollment_number, form_data.email, form_data.institutional_email, form_data.curp, form_data.date_of_birth, form_data.nationality, form_data.password, form_data.contact, form_data.role_id, form_data.club_id, form_data.degree_id)
        )
        connection.commit()
        return RedirectResponse(url="/dashboard/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        
        cursor.execute("SELECT * FROM university_degrees")
        degrees = cursor.fetchall()
                
        error_messages = format_errors(e.errors(), UserRequest)
            
        return templates.TemplateResponse(request=request, name="users/create.html.jinja", context={"errors": error_messages, "roles": roles, "clubs": clubs, "degrees": degrees, "current_year": current_year})

@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user(request: Request, user_id: int, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    
    cursor.execute(
        "SELECT id, enrollment_number, firstname, lastname, email, institutional_email, curp, date_of_birth, nationality, contact, password, role_id, club_id, degree_id FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
        
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM clubs")
    clubs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()
    
    return templates.TemplateResponse("users/edit.html.jinja", {"request": request, "user": user, "roles": roles, "clubs": clubs, "degrees": degrees, "current_year": datetime.now().year})

@router.post("/{user_id}/edit", response_class=HTMLResponse)
async def update_user(user_id: int, request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        user_data = UserRequest(**form_dict)

        cursor.execute("""
            UPDATE users SET firstname = %s, lastname = %s, enrollment_number = %s, 
                email = %s, institutional_email = %s, curp = %s, date_of_birth = %s, 
                nationality = %s, password = %s, contact = %s, role_id = %s, club_id = %s, degree_id = %s
            WHERE id = %s
        """, (
            user_data.firstname, user_data.lastname, user_data.enrollment_number, 
            user_data.email, user_data.institutional_email, user_data.curp, 
            user_data.date_of_birth, user_data.nationality, 
            user_data.password, user_data.contact, user_data.role_id, user_data.club_id, user_data.degree_id,
            user_id
        ))
        connection.commit()
        return RedirectResponse(url="/dashboard/users", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM roles")
        roles = cursor.fetchall()
        
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        
        cursor.execute("SELECT * FROM university_degrees")
        degrees = cursor.fetchall()
        
        error_messages = format_errors(e.errors(), UserRequest)
            
        return templates.TemplateResponse(request=request, name="users/edit.html.jinja", context={"errors": error_messages, "roles": roles, "clubs": clubs, "degrees": degrees, "current_year": current_year})

@router.get("/{user_id}/delete", response_class=HTMLResponse)
async def delete_user(user_id: int, request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    connection.commit()
    return RedirectResponse(url="/dashboard/users", status_code=303)

# Guardar inscripciones
@router.post("/enroll", response_class=HTMLResponse)
async def save_enrollment(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        enrollment_data = EnrollmentRequest(**form_dict)

        cursor.execute("""
            INSERT INTO enrollments (user_id, club_id, university_degree, cuatri, group_number, tutor_name, seguro_social, blood_type, medical_conditions, emergency_contact_name, emergency_contact_phone, contact_relationship)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            enrollment_data.user_id, enrollment_data.club_id, enrollment_data.university_degree, enrollment_data.cuatri, enrollment_data.group_number, enrollment_data.tutor_name, enrollment_data.seguro_social, enrollment_data.blood_type, enrollment_data.medical_conditions, enrollment_data.emergency_contact_name, enrollment_data.emergency_contact_phone, enrollment_data.contact_relationship
        ))
        connection.commit()
        return RedirectResponse(url="/dashboard/users", status_code=303)
    
    except ValidationError as e:
        error_messages = format_errors(e.errors(), EnrollmentRequest)
            
        return templates.TemplateResponse(request=request, name="users/enroll.html.jinja", context={"errors": error_messages, "current_year": current_year})
