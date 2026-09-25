# Esquemas de validación para equipos (Team)
# Los equipos agrupan miembros (por email) y aplicaciones; el workbench los usa
# para decidir qué ve cada líder y a quién puede asignar tickets.

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TeamBase(BaseModel):
    """
    Esquema base con la información común de un equipo.

    Atributos:
        name: Nombre del equipo
        description: Descripción opcional
        member_emails: Emails de los miembros del equipo
        application_ids: IDs de las aplicaciones asignadas al equipo
    """

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    member_emails: List[str] = Field(default_factory=list)
    application_ids: List[str] = Field(default_factory=list)

    @field_validator("member_emails")
    @classmethod
    def normalize_member_emails(cls, values: List[str]) -> List[str]:
        """Normaliza los emails (minúsculas, sin espacios, sin duplicados)."""
        normalized = []
        for value in values:
            email = (value or "").strip().lower()
            if email and email not in normalized:
                normalized.append(email)
        return normalized


class TeamCreate(TeamBase):
    """Esquema para crear un equipo (solo ADMIN)."""


class TeamUpdate(BaseModel):
    """
    Esquema para actualizar un equipo.

    Todos los campos son opcionales: el frontend envía solo lo que cambia
    (por ejemplo, únicamente `application_ids` al asignar un proyecto).
    """

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    member_emails: Optional[List[str]] = None
    application_ids: Optional[List[str]] = None

    @field_validator("member_emails")
    @classmethod
    def normalize_member_emails(cls, values: Optional[List[str]]) -> Optional[List[str]]:
        if values is None:
            return None
        normalized = []
        for value in values:
            email = (value or "").strip().lower()
            if email and email not in normalized:
                normalized.append(email)
        return normalized


class TeamResponse(TeamBase):
    """
    Esquema de respuesta al consultar un equipo.

    Atributos:
        id: Identificador único del equipo
    """

    id: UUID

    model_config = {"from_attributes": True}
