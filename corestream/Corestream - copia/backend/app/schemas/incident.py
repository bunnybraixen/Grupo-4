"""
Esquemas Pydantic v2 para validación y serialización de datos de incidentes.

Este módulo define los esquemas de solicitud y respuesta para operaciones CRUD,
asignación, cambio de estado y comentarios en incidentes. Incluye validadores
personalizados y configuración de campos para garantizar integridad de datos.

Autor: CoreStream Development Team
Fecha: 2026
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.incident import (
    IncidentCategory,
    IncidentStatus,
    IncidentSeverity
)


# ============================================================================
# ESQUEMAS DE USUARIO (PARA RESPUESTAS ANIDADAS)
# ============================================================================

class UserResponse(BaseModel):
    """
    Esquema de respuesta para datos de usuario en contexto de incidentes.

    Proporciona información básica del usuario sin exponer datos sensibles.
    Se utiliza como campo anidado en respuestas de incidentes.
    """

    id: str = Field(..., description="Identificador único del usuario")
    email: str = Field(..., description="Correo electrónico del usuario")
    full_name: str = Field(..., description="Nombre completo del usuario")
    avatar_url: Optional[str] = Field(
        None,
        description="URL del avatar o foto de perfil del usuario"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA CREACIÓN DE INCIDENTES
# ============================================================================

class IncidentCreate(BaseModel):
    """
    Esquema para la creación de nuevos incidentes.

    Valida que todos los campos requeridos estén presentes con contenido
    significativo. Los validadores aseguran que el título y descripción
    cumplan con longitudes mínimas para calidad de datos.
    """

    title: str = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Título del incidente (mínimo 5 caracteres)"
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Descripción detallada del incidente (mínimo 10 caracteres)"
    )

    application_id: str = Field(
        ...,
        description="Identificador de la aplicación/proyecto afectado"
    )

    category: IncidentCategory = Field(
        ...,
        description="Categoría del incidente"
    )

    severity: IncidentSeverity = Field(
        default=IncidentSeverity.MEDIUM,
        description="Nivel de severidad (por defecto: MEDIUM)"
    )

    assignee_id: Optional[str] = Field(
        None,
        description="ID del usuario a asignar (opcional)"
    )

    due_date: Optional[date] = Field(
        None,
        description="Fecha de vencimiento para resolución (opcional)"
    )

    environment: Optional[str] = Field(
        None,
        max_length=50,
        description="Entorno afectado: PRODUCCIÓN, STAGING, DESARROLLO, etc."
    )

    steps_to_reproduce: Optional[str] = Field(
        None,
        max_length=3000,
        description="Pasos detallados para reproducir el incidente"
    )

    expected_behavior: Optional[str] = Field(
        None,
        max_length=2000,
        description="Comportamiento esperado del sistema"
    )

    actual_behavior: Optional[str] = Field(
        None,
        max_length=2000,
        description="Comportamiento actual o incorrecto observado"
    )

    @field_validator("title")
    @classmethod
    def validate_title_content(cls, v: str) -> str:
        """
        Valida que el título no sea sólo espacios en blanco.

        Args:
            v: Valor del título a validar

        Returns:
            str: Título validado

        Raises:
            ValueError: Si el título contiene solo espacios
        """
        if not v or v.isspace():
            raise ValueError("El título no puede estar vacío o contener solo espacios")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description_content(cls, v: str) -> str:
        """
        Valida que la descripción no sea sólo espacios en blanco.

        Args:
            v: Valor de la descripción a validar

        Returns:
            str: Descripción validada

        Raises:
            ValueError: Si la descripción contiene solo espacios
        """
        if not v or v.isspace():
            raise ValueError("La descripción no puede estar vacía o contener solo espacios")
        return v.strip()

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[date]) -> Optional[date]:
        """
        Valida que la fecha de vencimiento sea futura.

        Args:
            v: Valor de fecha de vencimiento a validar

        Returns:
            Optional[date]: Fecha validada

        Raises:
            ValueError: Si la fecha de vencimiento es pasada
        """
        if v is not None and v < date.today():
            raise ValueError("La fecha de vencimiento no puede ser en el pasado")
        return v

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA ACTUALIZACIÓN DE INCIDENTES
# ============================================================================

class IncidentUpdate(BaseModel):
    """
    Esquema para la actualización parcial de incidentes existentes.

    Todos los campos son opcionales permitiendo actualizaciones parciales.
    Incluye validador especial para asegurar notas de resolución cuando
    el estado cambio a RESOLVED.
    """

    title: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255,
        description="Nuevo título del incidente"
    )

    description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=5000,
        description="Nueva descripción del incidente"
    )

    category: Optional[IncidentCategory] = Field(
        None,
        description="Nueva categoría del incidente"
    )

    severity: Optional[IncidentSeverity] = Field(
        None,
        description="Nuevo nivel de severidad"
    )

    status: Optional[IncidentStatus] = Field(
        None,
        description="Nuevo estado del incidente"
    )

    due_date: Optional[date] = Field(
        None,
        description="Nueva fecha de vencimiento"
    )

    environment: Optional[str] = Field(
        None,
        max_length=50,
        description="Nuevo entorno afectado"
    )

    steps_to_reproduce: Optional[str] = Field(
        None,
        max_length=3000,
        description="Nuevos pasos para reproducción"
    )

    expected_behavior: Optional[str] = Field(
        None,
        max_length=2000,
        description="Nuevo comportamiento esperado"
    )

    actual_behavior: Optional[str] = Field(
        None,
        max_length=2000,
        description="Nuevo comportamiento actual"
    )

    affected_version: Optional[str] = Field(
        None,
        max_length=50,
        description="Versión afectada"
    )

    @field_validator("status")
    @classmethod
    def validate_status_with_resolution(cls, v: Optional[IncidentStatus], info) -> Optional[IncidentStatus]:
        """
        Valida que si el estado es RESOLVED, debe existir nota de resolución.

        Args:
            v: Valor del estado a validar
            info: Contexto de validación con otros datos

        Returns:
            Optional[IncidentStatus]: Estado validado

        Raises:
            ValueError: Si estado es RESOLVED sin notas de resolución
        """
        if v == IncidentStatus.RESOLVED:
            data = info.data
            if not data.get("resolution_notes"):
                raise ValueError(
                    "Se requieren 'resolution_notes' cuando el estado es RESOLVED"
                )
        return v

    @field_validator("due_date")
    @classmethod
    def validate_due_date_update(cls, v: Optional[date]) -> Optional[date]:
        """
        Valida que la fecha de vencimiento sea futura.

        Args:
            v: Valor de fecha a validar

        Returns:
            Optional[date]: Fecha validada

        Raises:
            ValueError: Si la fecha es pasada
        """
        if v is not None and v < date.today():
            raise ValueError("La fecha de vencimiento no puede ser en el pasado")
        return v

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA RESOLUCIÓN DE INCIDENTES
# ============================================================================

class IncidentResolve(BaseModel):
    """
    Esquema específico para resolver un incidente.

    Requiere notas técnicas explicando cómo se resolvió el incidente
    y opcionalmente la versión en que fue corregido.
    """

    resolution_notes: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Notas técnicas sobre la resolución (mínimo 10 caracteres)"
    )

    fixed_in_version: Optional[str] = Field(
        None,
        max_length=50,
        description="Versión en la que se corrigió el incidente (opcional)"
    )

    @field_validator("resolution_notes")
    @classmethod
    def validate_resolution_content(cls, v: str) -> str:
        """
        Valida que las notas de resolución no sean solo espacios.

        Args:
            v: Notas de resolución a validar

        Returns:
            str: Notas validadas

        Raises:
            ValueError: Si las notas están vacías
        """
        if not v or v.isspace():
            raise ValueError("Las notas de resolución no pueden estar vacías")
        return v.strip()

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA REASIGNACIÓN DE INCIDENTES
# ============================================================================

class IncidentReassign(BaseModel):
    """
    Esquema para reasignar un incidente a otro usuario.

    Permite cambiar el responsable de resolver el incidente con una
    razón opcional que se registrará para auditoría.
    """

    assignee_id: str = Field(
        ...,
        description="ID del nuevo usuario a asignar"
    )

    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Razón de la reasignación (opcional)"
    )

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA COMENTARIOS EN INCIDENTES
# ============================================================================

class IncidentCommentCreate(BaseModel):
    """
    Esquema para crear un nuevo comentario en un incidente.

    Los comentarios permiten colaboración y seguimiento del progreso
    en la resolución del incidente.
    """

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Contenido del comentario"
    )

    @field_validator("content")
    @classmethod
    def validate_comment_content(cls, v: str) -> str:
        """
        Valida que el comentario no sea solo espacios en blanco.

        Args:
            v: Contenido a validar

        Returns:
            str: Contenido validado

        Raises:
            ValueError: Si el contenido está vacío
        """
        if not v or v.isspace():
            raise ValueError("El comentario no puede estar vacío")
        return v.strip()

    model_config = ConfigDict(from_attributes=True)


class IncidentCommentResponse(BaseModel):
    """
    Esquema de respuesta para un comentario en incidente.

    Proporciona toda la información del comentario incluyendo
    datos del usuario que lo escribió.
    """

    id: str = Field(..., description="Identificador único del comentario")
    incident_id: str = Field(..., description="ID del incidente")
    user: UserResponse = Field(..., description="Información del usuario comentarista")
    content: str = Field(..., description="Contenido del comentario")
    created_at: datetime = Field(..., description="Fecha y hora de creación")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA RESPUESTAS DE INCIDENTES
# ============================================================================

class IncidentResponse(BaseModel):
    """
    Esquema completo de respuesta para un incidente.

    Proporciona toda la información del incidente con datos anidados
    de usuarios y estadísticas derivadas calculadas dinámicamente.
    """

    id: str = Field(..., description="Identificador único")
    title: str = Field(..., description="Título del incidente")
    description: str = Field(..., description="Descripción del incidente")
    application_id: str = Field(..., description="ID de la aplicación")
    application_name: str = Field(..., description="Nombre de la aplicación")
    category: IncidentCategory = Field(..., description="Categoría")
    status: IncidentStatus = Field(..., description="Estado actual")
    severity: IncidentSeverity = Field(..., description="Nivel de severidad")
    priority_order: int = Field(..., description="Orden de prioridad")
    assignee: Optional[UserResponse] = Field(
        None,
        description="Usuario asignado (si existe)"
    )
    reporter: UserResponse = Field(..., description="Usuario que reportó")
    resolution_notes: Optional[str] = Field(
        None,
        description="Notas de resolución (si aplica)"
    )
    environment: Optional[str] = Field(None, description="Entorno afectado")
    steps_to_reproduce: Optional[str] = Field(
        None,
        description="Pasos para reproducir"
    )
    expected_behavior: Optional[str] = Field(
        None,
        description="Comportamiento esperado"
    )
    actual_behavior: Optional[str] = Field(
        None,
        description="Comportamiento actual"
    )
    affected_version: Optional[str] = Field(None, description="Versión afectada")
    fixed_in_version: Optional[str] = Field(
        None,
        description="Versión corregida"
    )
    due_date: Optional[date] = Field(None, description="Fecha de vencimiento")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")
    closed_at: Optional[datetime] = Field(None, description="Fecha de cierre")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")
    comment_count: int = Field(..., description="Número de comentarios")
    days_open: int = Field(..., description="Días abierto")
    is_overdue: bool = Field(..., description="¿Está vencido?")

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ESQUEMAS PARA LISTADOS Y ESTADÍSTICAS
# ============================================================================

class IncidentListResponse(BaseModel):
    """
    Esquema para respuesta de listados de incidentes con estadísticas.

    Proporciona un listado paginado junto con análisis agregados
    de incidentes agrupados por categoría y severidad.
    """

    items: List[IncidentResponse] = Field(
        ...,
        description="Lista de incidentes"
    )

    total: int = Field(
        ...,
        description="Número total de incidentes"
    )

    by_category: Dict[str, int] = Field(
        ...,
        description="Conteo de incidentes agrupados por categoría"
    )

    by_severity: Dict[str, int] = Field(
        ...,
        description="Conteo de incidentes agrupados por severidad"
    )

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    """
    Esquema para estadísticas del dashboard de incidentes.

    Proporciona métricas de alto nivel para monitoreo de salud
    y control de incidentes en el sistema.
    """

    total_incidents: int = Field(
        ...,
        description="Total de incidentes en el sistema"
    )

    open_incidents: int = Field(
        ...,
        description="Incidentes abiertos"
    )

    in_progress_incidents: int = Field(
        ...,
        description="Incidentes en progreso"
    )

    resolved_incidents: int = Field(
        ...,
        description="Incidentes resueltos"
    )

    by_status: Dict[str, int] = Field(
        ...,
        description="Distribución por estado"
    )

    by_severity: Dict[str, int] = Field(
        ...,
        description="Distribución por severidad"
    )

    by_category: Dict[str, int] = Field(
        ...,
        description="Distribución por categoría"
    )

    avg_resolution_time_days: Optional[float] = Field(
        None,
        description="Promedio de días para resolver incidentes"
    )

    overdue_count: int = Field(
        ...,
        description="Número de incidentes vencidos"
    )

    critical_unresolved: int = Field(
        ...,
        description="Incidentes críticos sin resolver"
    )

    model_config = ConfigDict(from_attributes=True)


class IncidentsByTeamResponse(BaseModel):
    """
    Esquema para incidentes agrupados por equipo/asignado.

    Proporciona análisis de carga de trabajo distribuida
    entre miembros del equipo.
    """

    assignee_id: str = Field(..., description="ID del usuario asignado")
    assignee_name: str = Field(..., description="Nombre del usuario")
    total_assigned: int = Field(..., description="Total asignado")
    open_count: int = Field(..., description="Conteo de abiertos")
    in_progress_count: int = Field(..., description="Conteo en progreso")
    by_severity: Dict[str, int] = Field(..., description="Distribución por severidad")
    incidents: List[IncidentResponse] = Field(..., description="Detalle de incidentes")

    model_config = ConfigDict(from_attributes=True)


class ByCategoryResponse(BaseModel):
    """
    Esquema para incidentes agrupados por categoría.

    Organiza incidentes para análisis por tipo de problema reportado.
    """

    category: IncidentCategory = Field(..., description="Categoría")
    count: int = Field(..., description="Número de incidentes")
    incidents: List[IncidentResponse] = Field(..., description="Lista de incidentes")

    model_config = ConfigDict(from_attributes=True)


class PriorityUpdateRequest(BaseModel):
    """
    Esquema para actualizar prioridades de múltiples incidentes.

    Permite reordenar incidentes mediante drag-and-drop,
    actualizando priority_order en lote.
    """

    incident_id: str = Field(..., description="ID del incidente")
    new_priority_order: int = Field(..., description="Nuevo orden de prioridad")

    model_config = ConfigDict(from_attributes=True)
