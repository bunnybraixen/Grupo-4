# Esquemas de validación para operaciones relacionadas con tickets
# Un ticket representa una tarea individual que necesita ser completada

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl, field_validator

from app.schemas.user import UserResponse


class TicketCreate(BaseModel):
    """
    Esquema para crear un nuevo ticket en el sistema.
    Un ticket representa una unidad de trabajo individual.
    
    Atributos:
        title: Título descriptivo del ticket (requerido)
        description: Descripción detallada de la tarea (opcional)
        epic_id: UUID de la épica a la que pertenece el ticket
        assignee_id: UUID del usuario asignado (opcional)
        priority: Nivel de prioridad del ticket (default: MEDIUM) - CRITICAL, HIGH, MEDIUM, LOW
        due_date: Fecha límite para completar el ticket (opcional)
    """
    title: str
    description: Optional[str] = None
    epic_id: UUID
    assignee_id: Optional[UUID] = None
    priority: str = "MEDIUM"
    due_date: Optional[datetime] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """
        Valida que el título del ticket no esté vacío.
        
        Args:
            v: Título a validar
            
        Returns:
            El título validado
            
        Raises:
            ValueError: Si el título está vacío o contiene solo espacios
        """
        if not v or not v.strip():
            raise ValueError("El título del ticket no puede estar vacío")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """
        Valida que la prioridad sea uno de los valores aceptados.
        
        Args:
            v: Prioridad a validar
            
        Returns:
            La prioridad validada
            
        Raises:
            ValueError: Si la prioridad no es válida
        """
        valid_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        if v.upper() not in valid_priorities:
            raise ValueError(f"La prioridad debe ser una de: {', '.join(valid_priorities)}")
        return v.upper()


class TicketUpdate(BaseModel):
    """
    Esquema para actualizar datos de un ticket existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Atributos:
        title: Nuevo título (opcional)
        description: Nueva descripción (opcional)
        priority: Nueva prioridad (opcional)
        due_date: Nueva fecha límite (opcional)
        order_index: Índice para ordenar tickets dentro de la épica (opcional)
    """
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
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
        """
        if v is not None and not v.strip():
            raise ValueError("El título del ticket no puede estar vacío")
        return v.strip() if v else v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que la prioridad, si se proporciona, sea válida.
        
        Args:
            v: Prioridad a validar
            
        Returns:
            La prioridad validada o None
        """
        if v is None:
            return v
        valid_priorities = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        if v.upper() not in valid_priorities:
            raise ValueError(f"La prioridad debe ser una de: {', '.join(valid_priorities)}")
        return v.upper()


class TicketMoveEpic(BaseModel):
    """
    Esquema para mover un ticket a una épica diferente.
    Permite reorganizar tickets entre épicas de la misma aplicación.
    
    Atributos:
        new_epic_id: UUID de la épica destino
    """
    new_epic_id: UUID


class TicketComplete(BaseModel):
    """
    Esquema para marcar un ticket como completado.
    Requiere proporcionar un enlace a la solicitud de cambio (PR).
    
    Atributos:
        pr_link: URL válida a la solicitud de cambio en GitHub, GitLab o Bitbucket
    """
    pr_link: str

    @field_validator("pr_link")
    @classmethod
    def validate_pr_link(cls, v: str) -> str:
        """
        Valida que el enlace sea una URL válida hacia un repositorio soportado.
        Acepta URLs de GitHub, GitLab y Bitbucket.
        
        Args:
            v: URL del PR a validar
            
        Returns:
            La URL validada
            
        Raises:
            ValueError: Si la URL no es válida o no es de un repositorio soportado
        """
        valid_domains = ("github.com", "gitlab.com", "bitbucket.org")
        if not any(domain in v.lower() for domain in valid_domains):
            raise ValueError("El PR debe ser de GitHub, GitLab o Bitbucket")
        
        # Validar que sea una URL válida
        if not v.startswith(("http://", "https://")):
            raise ValueError("El PR debe ser una URL válida comenzando con http:// o https://")
        
        return v


class TicketQuestion(BaseModel):
    """
    Esquema para registrar una pregunta asociada a un ticket.
    Permite que los usuarios planteen dudas durante la ejecución de la tarea.
    
    Atributos:
        question_text: Texto de la pregunta (mínimo 10 caracteres)
    """
    question_text: str

    @field_validator("question_text")
    @classmethod
    def validate_question_length(cls, v: str) -> str:
        """
        Valida que la pregunta tenga una longitud mínima de 10 caracteres.
        
        Args:
            v: Pregunta a validar
            
        Returns:
            La pregunta validada
            
        Raises:
            ValueError: Si la pregunta es muy corta
        """
        if len(v.strip()) < 10:
            raise ValueError("La pregunta debe tener mínimo 10 caracteres")
        return v


class TicketRedirect(BaseModel):
    """
    Esquema para redirigir un ticket a otro usuario.
    Se utiliza cuando un usuario no puede completar la tarea y la deriva a otro.
    
    Atributos:
        to_user_id: UUID del usuario al que se redirige el ticket
        reason: Motivo de la redirección (mínimo 10 caracteres)
    """
    to_user_id: UUID
    reason: str

    @field_validator("reason")
    @classmethod
    def validate_reason_length(cls, v: str) -> str:
        """
        Valida que el motivo de redirección tenga una longitud mínima de 10 caracteres.
        
        Args:
            v: Motivo a validar
            
        Returns:
            El motivo validado
            
        Raises:
            ValueError: Si el motivo es muy corto
        """
        if len(v.strip()) < 10:
            raise ValueError("El motivo debe tener mínimo 10 caracteres")
        return v


class TicketResponse(BaseModel):
    """
    Esquema de respuesta al consultar datos de un ticket.
    Incluye información completa del ticket con datos relacionados denormalizados.
    
    Atributos:
        id: Identificador único en formato UUID
        title: Título del ticket
        description: Descripción detallada del ticket
        epic_id: UUID de la épica a la que pertenece
        assignee_id: UUID del usuario asignado (opcional)
        assignee: Datos completos del usuario asignado (opcional)
        priority: Nivel de prioridad del ticket
        due_date: Fecha límite del ticket
        order_index: Índice para ordenamiento
        status: Estado actual del ticket (OPEN, IN_PROGRESS, COMPLETED, BLOCKED)
        created_at: Fecha y hora de creación
        completed_at: Fecha y hora de completación (opcional)
        epic_title: Título de la épica (para contexto)
        app_name: Nombre de la aplicación (para contexto)
        subtasks: Lista de subtareas asociadas al ticket
    """
    id: UUID
    title: str
    description: Optional[str] = None
    epic_id: UUID
    assignee_id: Optional[UUID] = None
    assignee: Optional[UserResponse] = None
    priority: str
    due_date: Optional[datetime] = None
    order_index: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    epic_title: Optional[str] = None
    app_name: Optional[str] = None
    subtasks: list = []

    model_config = {"from_attributes": True}
