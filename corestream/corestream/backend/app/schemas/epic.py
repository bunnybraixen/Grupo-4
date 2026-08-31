# Esquemas de validación para operaciones relacionadas con épicas
# Una épica es un conjunto de tickets relacionados dentro de una aplicación

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class EpicCreate(BaseModel):
    """
    Esquema para crear una nueva épica en el sistema.
    Una épica agrupa múltiples tickets relacionados por un objetivo común.
    
    Atributos:
        title: Título descriptivo de la épica (requerido)
        description: Descripción detallada del objetivo de la épica (opcional)
        application_id: UUID de la aplicación a la que pertenece la épica
        due_date: Fecha límite para completar la épica (opcional)
    """
    title: str
    description: Optional[str] = None
    application_id: UUID
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """
        Valida que el título de la épica no esté vacío.
        
        Args:
            v: Título a validar
            
        Returns:
            El título validado
            
        Raises:
            ValueError: Si el título está vacío o contiene solo espacios
        """
        if not v or not v.strip():
            raise ValueError("El título de la épica no puede estar vacío")
        return v.strip()


class EpicUpdate(BaseModel):
    """
    Esquema para actualizar datos de una épica existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Atributos:
        title: Nuevo título (opcional)
        description: Nueva descripción (opcional)
        order_index: Índice para ordenar épicas dentro de la aplicación (opcional)
        due_date: Nueva fecha límite (opcional)
        is_collapsed: Estado de colapso en la interfaz (opcional)
    """
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    due_date: Optional[datetime] = None
    is_collapsed: Optional[bool] = None

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
            raise ValueError("El título de la épica no puede estar vacío")
        return v.strip() if v else v

    @field_validator("order_index")
    @classmethod
    def validate_order_index(cls, v: Optional[int]) -> Optional[int]:
        """
        Valida que el índice de orden sea un número no negativo.
        
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


class EpicReorder(BaseModel):
    """
    Esquema para reordenar épicas dentro de una aplicación.
    Permite cambiar el orden de visualización de las épicas.
    
    Atributos:
        epic_id: UUID de la épica a reordenar
        new_index: Nuevo índice de posición para la épica
    """
    epic_id: UUID
    new_index: int

    @field_validator("new_index")
    @classmethod
    def validate_new_index(cls, v: int) -> int:
        """
        Valida que el nuevo índice sea no negativo.
        
        Args:
            v: Índice a validar
            
        Returns:
            El índice validado
            
        Raises:
            ValueError: Si el índice es negativo
        """
        if v < 0:
            raise ValueError("El nuevo índice no puede ser negativo")
        return v


class EpicResponse(BaseModel):
    """
    Esquema de respuesta al consultar datos de una épica.
    Incluye información de progreso y estadísticas de tickets.
    
    Atributos:
        id: Identificador único en formato UUID
        title: Título de la épica
        description: Descripción de la épica
        application_id: UUID de la aplicación propietaria
        order_index: Índice para ordenamiento visual
        due_date: Fecha límite de la épica
        is_collapsed: Indica si la épica está colapsada en la UI
        created_at: Fecha y hora de creación
        progress: Porcentaje de progreso (0-100) basado en tickets completados
        total_tickets: Número total de tickets en la épica
        completed_tickets: Número de tickets completados
    """
    id: UUID
    title: str
    description: Optional[str] = None
    application_id: UUID
    order_index: int
    due_date: Optional[datetime] = None
    is_collapsed: bool
    created_at: datetime
    progress: float
    total_tickets: int
    completed_tickets: int

    model_config = {"from_attributes": True}

    @field_validator("progress")
    @classmethod
    def validate_progress_range(cls, v: float) -> float:
        """
        Valida que el progreso esté en el rango válido de 0 a 100.
        
        Args:
            v: Valor del progreso a validar
            
        Returns:
            El progreso validado
            
        Raises:
            ValueError: Si el progreso no está entre 0 y 100
        """
        if not 0 <= v <= 100:
            raise ValueError("El progreso debe estar entre 0 y 100")
        return v
