
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pydantic import ValidationError
from ..dependencies.database import get_db_connection
from ..models.form import InscriptionRequest
from ..utility.functions import format_errors

router = APIRouter(
    prefix="/inscriptions",
    tags=["inscriptions"]
)

templates = Jinja2Templates(directory="src/pages")

current_year = datetime.now().year

# Guardar nueva inscripción
@router.post("/user/inscription", response_class=HTMLResponse)
async def save_inscription(request: Request, db: tuple = Depends(get_db_connection)):
    try:
        form_data = await request.form()
        form_dict = {key: value for key, value in form_data.items()}
        connection, cursor = db

        # Validar y guardar datos del formulario
        inscription_data = InscriptionRequest(**form_dict)

        cursor.execute("""
            INSERT INTO enrollments (user_id, club_id, cuatri, group_number, tutor_name, seguro_social, blood_type, medical_conditions, emergency_contact_name, emergency_contact_phone, contact_relationship)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.state.user_id,  # Asumiendo que el user_id está almacenado en request.state
            inscription_data.club_id, 
            inscription_data.cuatri, 
            inscription_data.group_number, 
            inscription_data.tutor_name, 
            inscription_data.seguro_social, 
            inscription_data.blood_type, 
            inscription_data.medical_conditions, 
            inscription_data.emergency_contact_name, 
            inscription_data.emergency_contact_phone, 
            inscription_data.contact_relationship
        ))
        connection.commit()
        return RedirectResponse(url="/", status_code=303)
    
    except ValidationError as e:
        cursor.execute("SELECT * FROM clubs")
        clubs = cursor.fetchall()
        
        error_messages = format_errors(e.errors(), InscriptionRequest)
            
        return templates.TemplateResponse("inscriptions/create.html", {"request": request, "errors": error_messages, "clubs": clubs, "current_year": current_year})