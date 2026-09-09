"""
Router de Notificaciones.

Maneja el sistema de notificaciones para usuarios:
- Obtener notificaciones del usuario actual (paginadas)
- Obtener contador de notificaciones no leídas
- Marcar notificaciones como leídas (individuales o todas)
- Las notificaciones se generan cuando ocurren eventos como:
  * Asignación de tickets
  * Cambios de estado de tickets
  * Preguntas planteadas en tickets
  * Menciones de otros usuarios
"""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Notification, User
from app.schemas import NotificationResponse

# Router para notificaciones
router = APIRouter(tags=["Notificaciones"])


@router.get(
    "/",
    response_model=List[NotificationResponse],
    summary="Obtener notificaciones del usuario",
    description="Retorna notificaciones del usuario actual con paginación"
)
async def get_user_notifications(
    skip: int = Query(0, ge=0, description="Número de notificaciones a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de notificaciones a retornar"),
    unread_only: bool = Query(False, description="Mostrar solo notificaciones no leídas"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[NotificationResponse]:
    """
    Obtiene las notificaciones del usuario autenticado.

    Args:
        skip (int): Número de registros a omitir para paginación
        limit (int): Máximo de registros a retornar
        unread_only (bool): Si es True, retorna solo notificaciones no leídas
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[NotificationResponse]: Lista paginada de notificaciones ordenadas por fecha descendente
    """
    # Construir consulta base
    query = select(Notification).where(
        Notification.user_id == current_user.id
    )

    # Filtrar por estado de lectura si se solicita.
    # `not Notification.is_read` evaluaba a un bool de Python (False) en tiempo
    # de construcción de la query, no a una condición SQL — el filtro no hacía
    # nada. Se usa `~` (NOT SQL) sobre la columna.
    if unread_only:
        query = query.where(~Notification.is_read)

    # Ordenar por fecha de creación descendente (más recientes primero)
    result = await db.execute(
        query.order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = result.scalars().all()

    return [NotificationResponse.from_orm(notif) for notif in notifications]


@router.get(
    "/unread-count",
    summary="Obtener cantidad de notificaciones no leídas",
    description="Retorna el número de notificaciones no leídas del usuario"
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Obtiene el contador de notificaciones no leídas.

    Args:
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con 'unread_count' (número de notificaciones no leídas)
    """
    # Contar notificaciones no leídas del usuario
    result = await db.execute(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                ~Notification.is_read
            )
        )
    )
    unread_count = result.scalar() or 0

    return {
        "unread_count": unread_count,
        "user_id": current_user.id
    }


@router.post(
    "/mark-read",
    summary="Marcar notificaciones como leídas",
    description="Marca un conjunto de notificaciones específicas como leídas"
)
async def mark_notifications_as_read(
    notification_ids: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Marca notificaciones específicas como leídas.

    Args:
        notification_ids (dict): Contiene 'notification_ids' lista de IDs
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con cantidad de notificaciones marcadas

    Raises:
        HTTPException: Si hay error en la operación (400)
    """
    ids = notification_ids.get("notification_ids", [])

    if not ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista de IDs de notificaciones vacía"
        )

    try:
        # Obtener notificaciones del usuario actual
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.id.in_(ids),
                    Notification.user_id == current_user.id
                )
            )
        )
        notifications = result.scalars().all()

        # Marcar como leídas
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1

        await db.commit()

        return {
            "marked_as_read": count,
            "total_requested": len(ids)
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al marcar notificaciones: {str(e)}"
        )


@router.post(
    "/mark-all-read",
    summary="Marcar todas las notificaciones como leídas",
    description="Marca todas las notificaciones no leídas del usuario como leídas"
)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Marca todas las notificaciones no leídas como leídas.

    Args:
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        dict: Diccionario con cantidad de notificaciones marcadas

    Raises:
        HTTPException: Si hay error en la operación (400)
    """
    try:
        # Obtener todas las notificaciones no leídas del usuario
        result = await db.execute(
            select(Notification).where(
                and_(
                    Notification.user_id == current_user.id,
                    ~Notification.is_read
                )
            )
        )
        notifications = result.scalars().all()

        # Marcar todas como leídas
        count = 0
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            count += 1

        await db.commit()

        return {
            "marked_as_read": count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al marcar todas las notificaciones: {str(e)}"
        )


@router.delete(
    "/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar notificaciones leídas",
    description="Elimina todas las notificaciones ya leídas del usuario actual",
)
async def delete_read_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Ruta fija /read: debe registrarse ANTES de /{notification_id} para que
    FastAPI no intente interpretar "read" como un UUID.
    """
    await db.execute(
        sa_delete(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read,
            )
        )
    )
    await db.commit()


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una notificación",
    description="Elimina una notificación específica del usuario actual",
)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notificación con ID {notification_id} no encontrada",
        )

    await db.delete(notification)
    await db.commit()
