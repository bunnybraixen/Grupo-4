# Esquemas de validación para operaciones relacionadas con subtareas
# Una subtarea es un paso más pequeño dentro de un ticket individual

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class SubtaskCreate(BaseModel):
    """
    Esquema para crear una nueva subtarea dentro de un ticket.
    Las subtareas permiten desglosar un ticket en pasos más pequeños.
    
    Atributos:
        title: Título descriptivo de la subtarea (requerido)
        ticket_id: UUID del ticket padre al que pertenece la subtarea
    """
    title: str
    ticket_id: UUID

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """
        Valida que el título de la subtarea no esté vacío.
        
        Args:
            v: Título a validar
            
        Returns:
            El título validado
            
        Raises:
            ValueError: Si el título está vacío o contiene solo espacios
        """
        if not v or not v.strip():
            raise ValueError("El título de la subtarea no puede estar vacío")
        return v.strip()


class SubtaskUpdate(BaseModel):
    """
    Esquema para actualizar datos de una subtarea existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Atributos:
        title: Nuevo título (opcional)
        is_completed: Nuevo estado de completación (opcional)
        order_index: Índice para ordenar subtareas dentro del ticket (opcional)
    """
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    order_index: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que el título, si se proporciona, no esté vacío.
        
        Args:
            v: Título a validar
            
        Returns:
            El título validado o None
            
        Raises:
            ValueError: Si el título está vacío
        """
        if v is not None and not v.strip():
            raise ValueError("El título de la subtarea no puede estar vacío")
        return v.strip() if v else v

    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v: Optional[int]) -> Optional[int]:
        """
        Valida que el índice de orden sea no negativo.
        
        Args:
            v: Índice a validar
            
        Returns:
            El índice validado o None
            
        Raises:
            ValueError: Si el índice es negativo
        """
        if v is not None and v < 0:
            raise ValueError("El índice de orden no puede ser negativo")
        return v


class SubtaskResponse(BaseModel):
    """
    Esquema de respuesta al consultar datos de una subtarea.
    Incluye información de estado y fechas de auditoría.
    
    Atributos:
        id: Identificador único en formato UUID
        title: Título de la subtarea
        is_completed: Indica si la subtarea está completada
        order_index: Índice para ordenamiento dentro del ticket
        completed_at: Fecha y hora cuando se marcó como completada (opcional)
    """
    id: UUID
    title: str
    is_completed: bool
    order_index: int
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
