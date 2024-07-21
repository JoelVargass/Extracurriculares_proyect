from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from ..dependencies.database import get_db_connection
from ..models.register import UserCreateRequest
from ..utility.functions import format_errors

router = APIRouter(
    prefix="/register",
    tags=["register"]
)

templates = Jinja2Templates(directory="src/pages/user")

@router.get("", response_class=HTMLResponse)
async def register_form(request: Request, db: tuple = Depends(get_db_connection)):
    connection, cursor = db
    cursor.execute("SELECT * FROM university_degrees")
    degrees = cursor.fetchall()

    return templates.TemplateResponse("formulario.html.jinja", {"request": request, "degrees": degrees})

@router.post("", response_class=HTMLResponse)
async def register_user(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db
        
        user_data = UserCreateRequest(**form_dict)

        cursor.execute(
            "INSERT INTO users (firstname, lastname, enrollment_number, email, institutional_email, curp, date_of_birth, nationality, password, contact, role_id, degree_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_data.firstname, user_data.lastname, user_data.enrollment_number, user_data.email, user_data.institutional_email, user_data.curp, user_data.date_of_birth, user_data.nationality, user_data.password, user_data.contact, 2, user_data.degree_id)
        )
        connection.commit()
        return RedirectResponse(url="/success", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM university_degrees")
        degrees = cursor.fetchall()
                
        error_messages = format_errors(e.errors(), UserCreateRequest)
            
        return templates.TemplateResponse("formulario.html.jinja", {"errors": error_messages, "degrees": degrees})
