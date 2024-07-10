from pydantic import BaseModel, ConfigDict, Field
from fastapi import Form
from typing import Optional

class Model(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_to_lower=True
    )

class CategoryRequest(BaseModel):
    title: str = Field(..., title="Título de la Categoría", description="El título de la categoría", min_length=5, max_length=255)
    description: str = Field(..., title="Descripción de la Categoría", description="Una breve descripción de la categoría", min_length=5, max_length=255)
    image_path: Optional[str] = Field(None, title="Imagen", description="Ruta de la imagen")

class CategoryResponse(BaseModel):
    id: int
    title: str
    description: str
    image_path: str

class CategoryListResponse(BaseModel):
    categories: list[CategoryResponse]
    items_count: int