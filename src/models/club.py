from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from pydantic import EmailStr
from datetime import time

class Model(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True
    )

class ClubRequest(Model):
    club_name: str = Field(..., title="Nombre del Club", description="El nombre del club", min_length=2, max_length=100)
    description: str = Field(..., title="Descripción", description="Una descripción breve del club", min_length=5, max_length=255)
    location: str = Field(..., title="Ubicación", description="Ubicación del club", min_length=5, max_length=255)
    init_hour: time = Field(..., title="Hora de Inicio", description="La hora de inicio del club")
    finish_hour: time = Field(..., title="Hora de Fin", description="La hora de finalización del club")
    quota: int = Field(..., title="Cupo", description="El número máximo de participantes")
    teacher_name: str = Field(..., title="Nombre del Maestro", description="El nombre del maestro encargado del club", min_length=5, max_length=100)
    teacher_email: EmailStr = Field(..., title="Correo Electrónico del Maestro", description="El correo electrónico del maestro encargado del club")
    image_path: Optional[str] = Field(None, title="Imagen", description="Ruta de la imagen")
    category_id: int = Field(..., title="ID de la Categoría", description="El ID de la categoría a la que pertenece el club")

class ClubResponse(Model):
    id: int
    club_name: str
    description: str
    location: str
    init_hour: time
    finish_hour: time
    quota: int
    teacher_name: str
    teacher_email: EmailStr
    image_path: str
    category: str

class ClubListResponse(Model):
    clubs: list[ClubResponse]
    items_count: int
