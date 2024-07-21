# src/models/formulario.py

from pydantic import BaseModel, Field
from typing import Optional

class InscriptionRequest(BaseModel):
    cuatri: str = Field(..., title="Cuatrimestre", description="Ingrese el cuatrimestre")
    group_number: str = Field(..., title="Número de Grupo", description="Ingrese el número de grupo")
    tutor_name: str = Field(..., title="Nombre del Tutor", description="Ingrese el nombre del tutor")
    seguro_social: str = Field(..., title="Número de Seguro Social", description="Ingrese el número de seguro social")
    blood_type: Optional[str] = Field(None, title="Tipo de Sangre", description="Ingrese el tipo de sangre")
    medical_conditions: Optional[str] = Field(None, title="Condiciones Médicas", description="Ingrese las condiciones médicas")
    emergency_contact_name: str = Field(..., title="Nombre del Contacto de Emergencia", description="Ingrese el nombre del contacto de emergencia")
    emergency_contact_phone: str = Field(..., title="Teléfono del Contacto de Emergencia", description="Ingrese el teléfono del contacto de emergencia")
    contact_relationship: str = Field(..., title="Relación con el Contacto de Emergencia", description="Ingrese la relación con el contacto de emergencia")
