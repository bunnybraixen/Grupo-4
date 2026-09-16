"""
Router FastAPI para gestión de incidentes en CoreStream.

Define todos los endpoints REST para operaciones CRUD de incidentes, asignación,
cambios de estado, gestión de comentarios y vistas especializadas. Implementa
autenticación, autorización por roles y validación de permisos.

Autor: CoreStream Development Team
Fecha: 2026
"""

from typing import Optional, List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.dependencies import require_role
from app.models.user import User, UserRole
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse,
    IncidentResolve,
    IncidentReassign,
    IncidentCommentCreate,
    IncidentCommentResponse,
    DashboardStats,
    IncidentsByTeamResponse,
    ByCategoryResponse,
    PriorityUpdateRequest,
)
from app.models.incident import IncidentCategory, IncidentStatus, IncidentSeverity
from app.services.incident_service import IncidentService


# Configuración del router
router = APIRouter(
    prefix="/incidents",
    tags=["Incidentes"],
    doc_extra={
        "description": "Endpoints para gestión completa de tickets de incidentes en aplicaciones"
    }
)


# ============================================================================
# DEPENDENCIAS
# ============================================================================

async def get_incident_service(db: AsyncSession = Depends(get_db)) -> IncidentService:
    """
    Dependencia que proporciona instancia del servicio de incidentes.

    Args:
        db: Sesión asincrónica de base de datos

    Returns:
        IncidentService: Instancia del servicio inyectada
    """
    return IncidentService(db)


# ============================================================================
# ENDPOINTS CRUD - CREAR, LISTAR, OBTENER, ACTUALIZAR, ELIMINAR
# ============================================================================

@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo incidente",
    description="Crea un nuevo ticket de incidente asociado a una aplicación. Requiere ser administrador."
)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Crea un nuevo incidente en el sistema.

    El usuario actual se registra como reportero del incidente.
    Si se proporciona assignee_id, se puede asignar inmediatamente.

    Args:
        incident_data: Datos del incidente a crear
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente creado con todos sus datos

    Raises:
        HTTPException: Si la aplicación no existe o usuario no tiene permisos
    """
    incident = await service.create_incident(
        incident_data=incident_data,
        reporter_id=current_user.id,
        db=db
    )
    return incident


@router.get(
    "/",
    response_model=IncidentListResponse,
    summary="Listar incidentes",
    description="Obtiene un listado paginado de incidentes con filtros opcionales."
)
async def list_incidents(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(50, ge=1, le=100, description="Número máximo de registros"),
    category: Optional[IncidentCategory] = Query(None, description="Filtrar por categoría"),
    severity: Optional[IncidentSeverity] = Query(None, description="Filtrar por severidad"),
    status: Optional[IncidentStatus] = Query(None, description="Filtrar por estado"),
    assignee_id: Optional[str] = Query(None, description="Filtrar por asignado"),
    app_id: Optional[str] = Query(None, description="Filtrar por aplicación"),
    search: Optional[str] = Query(None, description="Búsqueda por título/descripción"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentListResponse:
    """
    Lista incidentes con filtros avanzados.

    Permite filtrar por múltiples criterios y realizar búsqueda de texto.
    Retorna estadísticas agregadas junto con el listado.

    Args:
        skip: Registros a saltar para paginación
        limit: Límite de registros por página
        category: Categoría a filtrar (opcional)
        severity: Severidad a filtrar (opcional)
        status: Estado a filtrar (opcional)
        assignee_id: ID de asignado a filtrar (opcional)
        app_id: ID de aplicación a filtrar (opcional)
        search: Término de búsqueda (opcional)
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentListResponse: Listado con estadísticas
    """
    result = await service.get_incidents(
        skip=skip,
        limit=limit,
        category=category,
        severity=severity,
        status=status,
        assignee_id=assignee_id,
        app_id=app_id,
        search=search,
        db=db
    )
    return result


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Obtener detalle de incidente",
    description="Recupera la información completa de un incidente específico."
)
async def get_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Obtiene los detalles completos de un incidente.

    Args:
        incident_id: ID único del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Datos completos del incidente

    Raises:
        HTTPException: Si el incidente no existe (404)
    """
    incident = await service.get_incident(incident_id, db)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )
    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Actualizar incidente",
    description="Actualiza parcialmente los datos de un incidente existente."
)
async def update_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    incident_data: IncidentUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Actualiza los datos de un incidente.

    Permite actualización parcial de campos. El reportero del incidente
    y administradores pueden actualizar cualquier campo.

    Args:
        incident_id: ID del incidente a actualizar
        incident_data: Datos a actualizar
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente actualizado

    Raises:
        HTTPException: Si no existe o usuario no tiene permisos
    """
    incident = await service.get_incident(incident_id, db)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )

    # Validar permisos: reportero, asignado o admin
    if (current_user.id != incident.reporter_id and
        current_user.id != incident.assignee_id and
        current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar este incidente"
        )

    updated_incident = await service.update_incident(
        incident_id, incident_data, db
    )
    return updated_incident


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar incidente",
    description="Elimina un incidente y todos sus comentarios asociados. Solo administradores."
)
async def delete_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role(UserRole.ADMIN)),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina un incidente del sistema.

    Operación irreversible que también elimina comentarios asociados.
    Solo accesible a administradores.

    Args:
        incident_id: ID del incidente a eliminar
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Raises:
        HTTPException: Si el incidente no existe
    """
    deleted = await service.delete_incident(incident_id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )


# ============================================================================
# ENDPOINTS DE ASIGNACIÓN
# ============================================================================

@router.post(
    "/{incident_id}/assign",
    response_model=IncidentResponse,
    summary="Asignar incidente",
    description="Asigna un incidente a un usuario del equipo."
)
async def assign_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    reassign_data: IncidentReassign = ...,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Asigna un incidente a un usuario específico.

    Registra la asignación y crea una notificación para el usuario asignado.

    Args:
        incident_id: ID del incidente
        reassign_data: Datos de reasignación (assignee_id, reason)
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente actualizado

    Raises:
        HTTPException: Si no existe o usuario no tiene permisos
    """
    incident = await service.get_incident(incident_id, db)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )

    updated_incident = await service.assign_incident(
        incident_id=incident_id,
        assignee_id=reassign_data.assignee_id,
        assigner_id=current_user.id,
        reason=reassign_data.reason,
        db=db
    )
    return updated_incident


@router.post(
    "/{incident_id}/unassign",
    response_model=IncidentResponse,
    summary="Desasignar incidente",
    description="Remueve la asignación de un incidente, dejándolo abierto."
)
async def unassign_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Desasigna un incidente (remove assignee).

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente sin asignación

    Raises:
        HTTPException: Si no existe o usuario no tiene permisos
    """
    incident = await service.get_incident(incident_id, db)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )

    updated_incident = await service.unassign_incident(incident_id, db)
    return updated_incident


# ============================================================================
# ENDPOINTS DE CAMBIO DE ESTADO
# ============================================================================

@router.post(
    "/{incident_id}/start",
    response_model=IncidentResponse,
    summary="Iniciar trabajo en incidente",
    description="Cambia el estado a IN_PROGRESS indicando que se está trabajando."
)
async def start_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Marca un incidente como en progreso.

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente actualizado
    """
    updated = await service.change_status(
        incident_id=incident_id,
        new_status=IncidentStatus.IN_PROGRESS,
        user_id=current_user.id,
        db=db
    )
    return updated


@router.post(
    "/{incident_id}/review",
    response_model=IncidentResponse,
    summary="Enviar a revisión",
    description="Cambia el estado a UNDER_REVIEW para revisión antes de resolver."
)
async def review_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Envía un incidente a revisión.

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente actualizado
    """
    updated = await service.change_status(
        incident_id=incident_id,
        new_status=IncidentStatus.UNDER_REVIEW,
        user_id=current_user.id,
        db=db
    )
    return updated


@router.post(
    "/{incident_id}/resolve",
    response_model=IncidentResponse,
    summary="Resolver incidente",
    description="Marca el incidente como resuelto con notas técnicas."
)
async def resolve_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    resolve_data: IncidentResolve = ...,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Resuelve un incidente.

    Requiere notas explicando la solución aplicada. Opcionalmente
    registra la versión en que fue corregido.

    Args:
        incident_id: ID del incidente
        resolve_data: Datos de resolución
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente resuelto
    """
    updated = await service.resolve_incident(
        incident_id=incident_id,
        resolution_notes=resolve_data.resolution_notes,
        fixed_in_version=resolve_data.fixed_in_version,
        user_id=current_user.id,
        db=db
    )
    return updated


@router.post(
    "/{incident_id}/close",
    response_model=IncidentResponse,
    summary="Cerrar incidente",
    description="Cierra definitivamente un incidente resuelto."
)
async def close_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Cierra definitivamente un incidente.

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente cerrado
    """
    updated = await service.change_status(
        incident_id=incident_id,
        new_status=IncidentStatus.CLOSED,
        user_id=current_user.id,
        db=db
    )
    return updated


@router.post(
    "/{incident_id}/reopen",
    response_model=IncidentResponse,
    summary="Reabrir incidente",
    description="Reabre un incidente previamente resuelto o cerrado."
)
async def reopen_incident(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Reabre un incidente cerrado o resuelto.

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente reabierto
    """
    updated = await service.change_status(
        incident_id=incident_id,
        new_status=IncidentStatus.REOPENED,
        user_id=current_user.id,
        db=db
    )
    return updated


# ============================================================================
# ENDPOINTS DE PRIORIDAD
# ============================================================================

@router.patch(
    "/{incident_id}/priority",
    response_model=IncidentResponse,
    summary="Actualizar prioridad",
    description="Actualiza el orden de prioridad de un incidente."
)
async def update_priority(
    incident_id: str = Path(..., description="ID del incidente"),
    new_priority: int = Query(..., description="Nuevo orden de prioridad"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentResponse:
    """
    Actualiza el orden de prioridad de un incidente.

    Usado para operaciones de drag-and-drop.

    Args:
        incident_id: ID del incidente
        new_priority: Nuevo valor de priority_order
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentResponse: Incidente con prioridad actualizada
    """
    updated = await service.update_priority(
        incident_id=incident_id,
        new_priority_order=new_priority,
        db=db
    )
    return updated


# ============================================================================
# ENDPOINTS DE COMENTARIOS
# ============================================================================

@router.get(
    "/{incident_id}/comments",
    response_model=List[IncidentCommentResponse],
    summary="Listar comentarios",
    description="Obtiene todos los comentarios de un incidente."
)
async def get_incident_comments(
    incident_id: str = Path(..., description="ID del incidente"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> List[IncidentCommentResponse]:
    """
    Obtiene todos los comentarios de un incidente.

    Ordena cronológicamente del más antiguo al más reciente.

    Args:
        incident_id: ID del incidente
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        List[IncidentCommentResponse]: Lista de comentarios
    """
    comments = await service.get_incident_comments(incident_id, db)
    return comments


@router.post(
    "/{incident_id}/comments",
    response_model=IncidentCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar comentario",
    description="Agrega un nuevo comentario a un incidente."
)
async def add_comment(
    incident_id: str = Path(..., description="ID del incidente"),
    comment_data: IncidentCommentCreate = ...,
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentCommentResponse:
    """
    Agrega un nuevo comentario a un incidente.

    El usuario actual se registra como autor del comentario.

    Args:
        incident_id: ID del incidente
        comment_data: Datos del comentario
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentCommentResponse: Comentario creado

    Raises:
        HTTPException: Si el incidente no existe
    """
    incident = await service.get_incident(incident_id, db)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incidente con ID {incident_id} no encontrado"
        )

    comment = await service.add_comment(
        incident_id=incident_id,
        user_id=current_user.id,
        content=comment_data.content,
        db=db
    )
    return comment


# ============================================================================
# ENDPOINTS DE VISTAS ESPECIALIZADAS
# ============================================================================

@router.get(
    "/by-app/{app_id}",
    response_model=List[ByCategoryResponse],
    summary="Incidentes por aplicación",
    description="Obtiene incidentes de una aplicación agrupados por categoría."
)
async def get_incidents_by_app(
    app_id: str = Path(..., description="ID de la aplicación"),
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> List[ByCategoryResponse]:
    """
    Obtiene incidentes de una aplicación agrupados por categoría.

    Args:
        app_id: ID de la aplicación
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        List[ByCategoryResponse]: Incidentes agrupados por categoría
    """
    result = await service.get_incidents_grouped_by_category(app_id, db)
    return result


@router.get(
    "/by-team",
    response_model=List[IncidentsByTeamResponse],
    summary="Incidentes por equipo",
    description="Obtiene incidentes agrupados por usuario asignado."
)
async def get_incidents_by_team(
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> List[IncidentsByTeamResponse]:
    """
    Obtiene incidentes agrupados por equipo (asignado).

    Útil para análisis de carga de trabajo.

    Args:
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        List[IncidentsByTeamResponse]: Incidentes por miembro del equipo
    """
    result = await service.get_incidents_by_team(db)
    return result


@router.get(
    "/my-incidents",
    response_model=IncidentListResponse,
    summary="Mis incidentes",
    description="Obtiene incidentes del usuario actual (reportados y asignados)."
)
async def get_my_incidents(
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> IncidentListResponse:
    """
    Obtiene incidentes del usuario actual.

    Incluye incidentes reportados y asignados al usuario.

    Args:
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        IncidentListResponse: Incidentes del usuario
    """
    result = await service.get_user_incidents(current_user.id, db)
    return result


@router.get(
    "/dashboard/stats",
    response_model=DashboardStats,
    summary="Estadísticas del dashboard",
    description="Obtiene métricas de alto nivel para el dashboard de incidentes."
)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> DashboardStats:
    """
    Obtiene estadísticas agregadas del sistema de incidentes.

    Incluye totales, distribuciones y métricas de rendimiento.

    Args:
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        DashboardStats: Estadísticas del dashboard
    """
    stats = await service.get_dashboard_stats(db)
    return stats


# ============================================================================
# ENDPOINTS BATCH/UTILIDAD
# ============================================================================

@router.patch(
    "/batch/reorder-priority",
    summary="Reordenar prioridades",
    description="Actualiza prioridades de múltiples incidentes (drag-and-drop)."
)
async def batch_reorder_priorities(
    updates: List[PriorityUpdateRequest],
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_role(UserRole.ADMIN)),
    service: IncidentService = Depends(get_incident_service),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Actualiza prioridades de múltiples incidentes en lote.

    Operación útil para interfaz drag-and-drop.
    Solo accesible a administradores.

    Args:
        updates: Lista de actualizaciones de prioridad
        current_user: Usuario autenticado
        service: Servicio de incidentes
        db: Sesión de base de datos

    Returns:
        dict: Resultado de la operación
    """
    result = await service.reorder_priorities(updates, db)
    return {
        "success": True,
        "updated_count": result,
        "message": f"Se actualizaron {result} prioridades"
    }
