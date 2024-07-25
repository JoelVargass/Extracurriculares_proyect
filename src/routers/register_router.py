from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
from ..data.database import get_db, close_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from icecream import ic
router = APIRouter()

SECRET_KEY = "clave"
ALGORITHM = "HS256"

class UserRegisterRequest(BaseModel):
    enrollment_number: str
    firstname: str
    lastname: str
    email: str
    institutional_email: Optional[str]
    password: str
    contact: str
    curp: Optional[str]
    date_of_birth: Optional[str]
    nationality: Optional[str]
    degree_id: int

templates = Jinja2Templates(directory="src/pages/user")

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.get("/user/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Depends = Depends(get_db)):

    connection, cursor = get_db()

    cursor.execute("""
        SELECT * FROM university_degrees
    """)

    degrees = cursor.fetchall()
    print(degrees)
    ic(degrees)

    return templates.TemplateResponse("register.html.jinja", {"request": request, "degrees": degrees})

@router.post("/user/register")
async def register_user(request: Request):

    form_data = await request.form()
    form_dict = dict(form_data)
    connection, cursor = get_db()

    form_data = UserRegisterRequest(**form_dict)
    
    cursor.execute("SELECT * FROM users WHERE enrollment_number = %s OR email = %s", 
                (form_data.enrollment_number, form_data.email))
    user = cursor.fetchone()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    cursor.execute(
        """
        INSERT INTO users (enrollment_number, firstname, lastname, email, institutional_email, 
                        password, contact, role_id, curp, date_of_birth, nationality, degree_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            form_data.enrollment_number, form_data.firstname, form_data.lastname, form_data.email,
            form_data.institutional_email, form_data.password, form_data.contact, 2,  # Role ID 2 for 'student'
            form_data.curp, form_data.date_of_birth, form_data.nationality, form_data.degree_id
        )
    )
    connection.commit()

    # cursor.execute("SELECT * FROM users WHERE enrollment_number = %s", (form_data.enrollment_number,))
    # new_user = cursor.fetchone()
    #
    # token = encode_token({
    #     "user_id": new_user["id"],
    #     "enrollment_number": new_user["enrollment_number"],
    #     "email": new_user["email"],
    #     "role_id": new_user["role_id"]
    # })

    close_db(connection)
    return templates.TemplateResponse("login.html.jinja", {"request": request})

# Código restante de tu archivo FastAPI
