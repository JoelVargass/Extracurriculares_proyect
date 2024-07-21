from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class UniversityDegree(BaseModel):
    id: int
    title: str
    abbreviation: str