from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
from ..data.database import get_db, close_db
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

SECRET_KEY = "clave"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class EnrollmentRequest(BaseModel):
    cuatri: str
    group_number: str
    tutor_name: str
    seguro_social: str
    blood_type: Optional[str]
    medical_conditions: Optional[str]
    emergency_contact_name: str
    emergency_contact_phone: str
    contact_relationship: str

templates = Jinja2Templates(directory="src/pages/user")

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/user/enroll/{club_id}", response_class=HTMLResponse)
async def submit_enroll_form(request: Request, club_id: int):
    return templates.TemplateResponse("formulario.html.jinja", {"request": request, "club_id": club_id})

@router.post("/user/enroll/{club_id}")
async def enroll_user(
    request: Request,
    club_id: int,
    token: str = Depends(oauth2_scheme),
    cuatri: str = Form(...),
    group_number: str = Form(...),
    tutor_name: str = Form(...),
    seguro_social: str = Form(...),
    blood_type: Optional[str] = Form(None),
    medical_conditions: Optional[str] = Form(None),
    emergency_contact_name: str = Form(...),
    emergency_contact_phone: str = Form(...),
    contact_relationship: str = Form(...)
):
    payload = decode_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # Verificar si el usuario ya está inscrito en el club
    connection, cursor = get_db()
    cursor.execute("SELECT * FROM enrollments WHERE user_id = %s AND club_id = %s", (user_id, club_id))
    enrollment = cursor.fetchone()

    if enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already enrolled in this club")

    # Insertar la inscripción en la base de datos
    cursor.execute(
        """
        INSERT INTO enrollments (user_id, club_id, cuatri, group_number, tutor_name, seguro_social,
                                blood_type, medical_conditions, emergency_contact_name, emergency_contact_phone, contact_relationship)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id, club_id, cuatri, group_number, tutor_name, seguro_social, blood_type,
            medical_conditions, emergency_contact_name, emergency_contact_phone, contact_relationship
        )
    )
    connection.commit()
    close_db(connection)
    return templates.TemplateResponse("home.html", {"request": request})
