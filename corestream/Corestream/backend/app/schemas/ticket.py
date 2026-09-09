# Esquemas de validación para operaciones relacionadas con tickets
# Un ticket representa una tarea individual que necesita ser completada

import re
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.subtask import SubtaskResponse
from app.schemas.user import UserResponse

_PLACEHOLDER_PR = re.compile(
    r'github\.com/owner/repo/|gitlab\.com/owner/repo/|bitbucket\.org/owner/repo/',
    re.IGNORECASE,
)

class TicketCreate(BaseModel):
    """
    Esquema para crear un nuevo ticket en el sistema.
    Un ticket representa una unidad de trabajo individual.
    
    Atributos:
        title: Título descriptivo del ticket (requerido)
        description: Descripción detallada de la tarea (opcional)
        epic_id: UUID de la épica a la que pertenece el ticket
        assignee_id: UUID del usuario asignado (opcional)
        priority: Nivel de prioridad del ticket (default: MEDIUM) - URGENT, HIGH, MEDIUM, LOW
        due_date: Fecha límite para completar el ticket (opcional)
    """
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    epic_id: UUID
    assignee_id: Optional[UUID] = None
    priority: str = "MEDIUM"
    due_date: Optional[datetime] = None
    estimated_time_seconds: Optional[int] = 0

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
        valid_priorities = {"URGENT", "HIGH", "MEDIUM", "LOW"}
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
        assignee_id: UUID del usuario asignado (opcional)
    """
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    order_index: Optional[int] = None
    estimated_time_seconds: Optional[int] = None
    time_spent_seconds: Optional[int] = None
    assignee_id: Optional[UUID] = None

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
        valid_priorities = {"URGENT", "HIGH", "MEDIUM", "LOW"}
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
    pr_link: str = Field(..., max_length=500)

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

        if _PLACEHOLDER_PR.search(v):
            raise ValueError("Por favor ingresa un enlace real de PR, no el placeholder de ejemplo")

        return v


class TicketQuestion(BaseModel):
    """
    Esquema para registrar una pregunta asociada a un ticket.
    Permite que los usuarios planteen dudas durante la ejecución de la tarea.
    
    Atributos:
        question_text: Texto de la pregunta (mínimo 10 caracteres)
    """
    question_text: str = Field(..., max_length=2_000)

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
    reason: str = Field(..., max_length=2_000)

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


class TicketReorder(BaseModel):
    """
    Esquema para reordenar un ticket dentro de la misma épica.
    Permite cambiar la posición relativa de un ticket respecto a otros en la épica.

    Atributos:
        new_index: Nueva posición del ticket en la épica (índice 0-basado)
    """
    new_index: int


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
        linked_ticket_title: Título del ticket que originó este ticket de soporte (si aplica)
        origin_epic_title: Título de la épica del ticket origen (si aplica)
    """
    id: UUID
    title: str
    description: Optional[str] = None
    epic_id: Optional[UUID] = None
    # Usuarios
    assignee_id: Optional[UUID] = None
    assignee: Optional[UserResponse] = None
    created_by_id: Optional[UUID] = None
    # Metadatos
    priority: str
    due_date: Optional[datetime] = None
    order_index: int
    status: str
    # Tiempos y bloqueos
    estimated_time_seconds: int = 0
    time_spent_seconds: int = 0
    timer_started_at: Optional[datetime] = None
    block_reason: Optional[str] = None
    blocked_question: Optional[str] = None
    blocked_at: Optional[datetime] = None
    pr_link: Optional[str] = None
    # Fechas
    created_at: datetime
    completed_at: Optional[datetime] = None
    # Contexto extra
    epic_title: Optional[str] = None
    app_name: Optional[str] = None
    subtasks: List[SubtaskResponse] = []
    # Campos de soporte (null para tickets de desarrollo)
    ticket_type: str = "DEVELOPMENT"
    severity: Optional[str] = None
    stack_trace: Optional[str] = None
    reproduction_steps: Optional[str] = None
    browser: Optional[str] = None
    operating_system: Optional[str] = None
    linked_ticket_id: Optional[UUID] = None
    linked_ticket_title: Optional[str] = None
    origin_epic_title: Optional[str] = None

    @field_validator("status", "ticket_type", mode="before")
    @classmethod
    def extract_enum_name(cls, v: Any) -> str:
        """Normaliza enums de SQLAlchemy o strings con prefijo a su valor string."""
        if hasattr(v, "name"):
            return v.name
        return str(v).split('.')[-1].upper()

    @field_validator("severity", mode="before")
    @classmethod
    def extract_severity_name(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if hasattr(v, "name"):
            return v.name
        return str(v).split('.')[-1].upper()

    # Configuración para permitir la lectura desde modelos de SQLAlchemy]
    model_config = {"from_attributes": True}

class TicketResolveQuestion(BaseModel):
    """Esquema para resolver una pregunta de un ticket"""
    resolution: str = Field(..., max_length=2_000)

    @field_validator("resolution")
    @classmethod
    def validate_resolution_length(cls, v: str) -> str:
        if len(v.strip()) < 5:
            raise ValueError("La resolución debe tener al menos 5 caracteres")
        return v
    
class SupportTicketCreate(BaseModel):
    """Esquema para crear un ticket de soporte (bug de producción)."""
    title: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    severity: str = "MEDIUM"
    stack_trace: Optional[str] = Field(None, max_length=20_000)
    reproduction_steps: Optional[str] = Field(None, max_length=5_000)
    browser: Optional[str] = Field(None, max_length=255)
    operating_system: Optional[str] = Field(None, max_length=255)
    linked_ticket_id: Optional[UUID] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El título del ticket de soporte no puede estar vacío")
        return v.strip()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        if v.upper() not in valid:
            raise ValueError(f"La severidad debe ser una de: {', '.join(valid)}")
        return v.upper()


class SupportTicketUpdate(BaseModel):
    """Esquema para actualizar campos de un ticket de soporte."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    severity: Optional[str] = None
    stack_trace: Optional[str] = Field(None, max_length=20_000)
    reproduction_steps: Optional[str] = Field(None, max_length=5_000)
    browser: Optional[str] = Field(None, max_length=255)
    operating_system: Optional[str] = Field(None, max_length=255)
    linked_ticket_id: Optional[UUID] = None

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El título no puede estar vacío")
        return v.strip() if v else v

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        if v.upper() not in valid:
            raise ValueError(f"La severidad debe ser una de: {', '.join(valid)}")
        return v.upper()


class SupportTicketAssign(BaseModel):
    """Esquema para asignar un ticket de soporte a un developer (solo TEAM_LEADER)."""
    assignee_id: UUID


class TicketEventResponse(BaseModel):
    """
    Esquema de respuesta para el historial de eventos de un ticket.
    Devuelve qué pasó, cuándo pasó y quién lo hizo.
    """
    id: UUID
    ticket_id: UUID
    event_type: str
    user_id: Optional[UUID] = None
    detail: Optional[dict] = None
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = {"from_attributes": True}
    