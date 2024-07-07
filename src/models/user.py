from pydantic import BaseModel, ConfigDict, Field
from pydantic import EmailStr
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
    password: str = Field(..., title="Contraseña", description="The user's password", min_length=5, max_length=50)
    contact: str  = Field(..., title="Contacto", description="The user's contact number", min_length=5, max_length=10)
    role_id: int  = Field(..., title="Rol", description="The user's role ID")

class UserResponse(Model):
    id: int
    firstname: str
    lastname: str
    enrollment_number: str
    email: EmailStr
    contact: str
    role: str
    
class UserListResponse(Model):
    users: list[UserResponse]
    items_count: int