"""
Router de Gestión de Subtareas.

Las subtareas representan pasos más pequeños dentro de un ticket.
Permiten:
- Crear, actualizar y eliminar subtareas
- Marcar subtareas como completadas
- Reordenar subtareas dentro de un ticket
- Cada subtarea puede tener su propio progreso
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models import Subtask, Ticket, TicketEvent, TicketEventType
from app.schemas import SubtaskResponse, SubtaskCreate, SubtaskUpdate
from app.services import ticket_state_machine
from app.middleware.auth import get_current_user

# Router para subtareas
router = APIRouter(prefix="/subtasks", tags=["Subtareas"])


@router.post(
    "/",
    response_model=SubtaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva subtarea",
    description="Crea una subtarea dentro de un ticket específico"
)
async def create_subtask(
    subtask_data: SubtaskCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SubtaskResponse:
    """
    Crea una nueva subtarea dentro de un ticket.

    Args:
        subtask_data (SubtaskCreate): Datos de la nueva subtarea (título, ticket_id)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        SubtaskResponse: Subtarea creada

    Raises:
        HTTPException: Si el ticket no existe (404) o hay error en creación (400)
    """
    # Verificar que el ticket existe
    ticket_check = await db.execute(
        select(Ticket).where(Ticket.id == subtask_data.ticket_id)
    )
    if not ticket_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {subtask_data.ticket_id} no encontrado"
        )

    try:
        # Obtener el siguiente order_index disponible
        max_order = await db.execute(
            select(func.max(Subtask.order_index))
            .where(Subtask.ticket_id == subtask_data.ticket_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        # Crear nueva subtarea
        new_subtask = Subtask(
            **subtask_data.dict(),
            order_index=next_order,
            is_completed=False
        )
        db.add(new_subtask)
        await db.commit()
        await db.refresh(new_subtask)

        # Registrar evento en el ticket
        await ticket_state_machine.log_ticket_event(
            db, subtask_data.ticket_id, TicketEventType.SUBTASK_CREATED,
            current_user.id, f"Subtarea creada: {subtask_data.title}"
        )

        return SubtaskResponse.from_orm(new_subtask)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear subtarea: {str(e)}"
        )


@router.put(
    "/{subtask_id}",
    response_model=SubtaskResponse,
    summary="Actualizar subtarea",
    description="Modifica una subtarea (título, estado de completación)"
)
async def update_subtask(
    subtask_id: int,
    subtask_update: SubtaskUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SubtaskResponse:
    """
    Actualiza una subtarea existente.

    Args:
        subtask_id (int): ID de la subtarea a actualizar
        subtask_update (SubtaskUpdate): Datos a actualizar (título, is_completed)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        SubtaskResponse: Subtarea actualizada

    Raises:
        HTTPException: Si la subtarea no existe (404) o hay error en actualización (400)
    """
    result = await db.execute(
        select(Subtask).where(Subtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()

    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtarea con ID {subtask_id} no encontrada"
        )

    try:
        # Obtener ticket para registrar evento
        ticket = await db.execute(
            select(Ticket).where(Ticket.id == subtask.ticket_id)
        )
        ticket = ticket.scalar_one_or_none()

        # Aplicar cambios a los campos proporcionados
        update_data = subtask_update.dict(exclude_unset=True)
        old_completion_status = subtask.is_completed

        for field, value in update_data.items():
            setattr(subtask, field, value)

        await db.commit()
        await db.refresh(subtask)

        # Registrar evento si cambió el estado de completación
        if old_completion_status != subtask.is_completed and ticket:
            event_type = TicketEventType.SUBTASK_COMPLETED if subtask.is_completed else TicketEventType.UPDATED
            await ticket_state_machine.log_ticket_event(
                db, ticket.id, event_type,
                current_user.id, f"Subtarea {subtask.title} - Completada: {subtask.is_completed}"
            )

        return SubtaskResponse.from_orm(subtask)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar subtarea: {str(e)}"
        )


@router.delete(
    "/{subtask_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar subtarea",
    description="Elimina una subtarea del ticket"
)
async def delete_subtask(
    subtask_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina una subtarea de forma permanente.

    Args:
        subtask_id (int): ID de la subtarea a eliminar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si la subtarea no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Subtask).where(Subtask.id == subtask_id)
    )
    subtask = result.scalar_one_or_none()

    if not subtask:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtarea con ID {subtask_id} no encontrada"
        )

    try:
        ticket_id = subtask.ticket_id

        # Eliminar subtarea
        await db.delete(subtask)
        await db.commit()

        # Registrar evento en el ticket
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.SUBTASK_DELETED,
            current_user.id, f"Subtarea eliminada"
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar subtarea: {str(e)}"
        )


@router.patch(
    "/reorder",
    response_model=List[SubtaskResponse],
    summary="Reordenar subtareas",
    description="Cambia el orden de las subtareas dentro de un ticket (drag-drop)"
)
async def reorder_subtasks(
    reorder_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[SubtaskResponse]:
    """
    Reordena las subtareas dentro de un ticket.

    Args:
        reorder_data (dict): Contiene 'subtask_ids' lista en nuevo orden
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[SubtaskResponse]: Subtareas reordenadas

    Raises:
        HTTPException: Si hay error en reorden (400)
    """
    subtask_ids = reorder_data.get("subtask_ids", [])

    if not subtask_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lista de IDs de subtareas vacía"
        )

    try:
        # Obtener todas las subtareas en el nuevo orden
        subtasks = []
        for idx, subtask_id in enumerate(subtask_ids):
            result = await db.execute(
                select(Subtask).where(Subtask.id == subtask_id)
            )
            subtask = result.scalar_one_or_none()

            if not subtask:
                raise ValueError(f"Subtarea con ID {subtask_id} no encontrada")

            # Actualizar order_index
            subtask.order_index = idx
            subtasks.append(subtask)

        await db.commit()

        # Refrescar todas las subtareas
        for subtask in subtasks:
            await db.refresh(subtask)

        return [SubtaskResponse.from_orm(st) for st in subtasks]

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al reordenar subtareas: {str(e)}"
        )
