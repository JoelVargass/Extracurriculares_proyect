from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from fastapi import Form

class Model(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True
    )

class UserRequest(Model):
    firstname: str = Field(..., title="Nombre", description="The user's first name", min_length=2, max_length=50)
    lastname: str = Field(..., title="Apellidos", description="The user's last name", min_length=2, max_length=50)
    enrollment_number: str = Field(..., title="Matrícula", description="The user's enrollment number", min_length=8, max_length=8)
    email: EmailStr = Field(..., title="Correo", description="The user's email address", min_length=5, max_length=255)
    institutional_email: EmailStr = Field(..., title="Correo Institucional", description="The user's institutional email address", min_length=5, max_length=100)
    curp: str = Field(..., title="CURP", description="The user's CURP", min_length=18, max_length=18)
    date_of_birth: str = Field(..., title="Fecha de Nacimiento", description="The user's date of birth")
    nationality: str = Field(..., title="Nacionalidad", description="The user's nationality", min_length=2, max_length=100)
    password: str = Field(..., title="Contraseña", description="The user's password", min_length=5, max_length=50)
    contact: str = Field(..., title="Contacto", description="The user's contact number", min_length=5, max_length=10)
    role_id: int = Field(..., title="Rol", description="The user's role ID")
    club_id: int
    degree_id: int

class UserResponse(Model):
    id: int
    firstname: str
    lastname: str
    enrollment_number: str
    email: EmailStr
    institutional_email: EmailStr
    curp: str
    date_of_birth: str
    nationality: str
    contact: str
    role: str
    club_id: int
    degree_id: int

class UserListResponse(Model):
    users: list[UserResponse]
    items_count: int

class EnrollmentRequest(Model):
    user_id: int
    club_id: int
    university_degree: str = Field(..., title="Carrera Universitaria", min_length=2, max_length=100)
    cuatri: str = Field(..., title="Cuatri", min_length=1, max_length=10)
    group_number: str = Field(..., title="Número de Grupo", min_length=1, max_length=10)
    tutor_name: str = Field(..., title="Nombre del Tutor", min_length=2, max_length=255)
    seguro_social: str = Field(..., title="Seguro Social", min_length=1, max_length=20)
    blood_type: str = Field(None, title="Tipo de Sangre", max_length=10)
    medical_conditions: str = Field(None, title="Condiciones Médicas", max_length=200)
    emergency_contact_name: str = Field(..., title="Nombre del Contacto de Emergencia", min_length=2, max_length=255)
    emergency_contact_phone: str = Field(..., title="Teléfono del Contacto de Emergencia", min_length=5, max_length=255)
    contact_relationship: str = Field(..., title="Relación del Contacto", min_length=2, max_length=255)
