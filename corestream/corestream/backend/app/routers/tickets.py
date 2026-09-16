"""
Router Principal de Tickets - Gestión del Ciclo de Vida Completo.

Este es el router más importante de CoreStream que maneja:
- CRUD de tickets (crear, leer, actualizar, eliminar)
- Transiciones de estado: TODO -> IN_PROGRESS -> COMPLETED
- Gestor de temporizador de trabajo (timer)
- Preguntas bloqueantes y resolución de preguntas
- Redirección de tickets a otros usuarios
- Historial de eventos de tickets
- Validación de pull requests antes de completar

Cada operación de cambio de estado utiliza la máquina de estados (ticket_state_machine)
para garantizar transiciones válidas y consistencia de datos.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import (
    Ticket, User, Epic, TicketStatus, TicketEvent, 
    TicketEventType, Subtask
)
from app.schemas import (
    TicketResponse, TicketCreate, TicketUpdate, 
    TicketEventResponse
)
from app.services import ticket_state_machine, timer_service, notification_service
from app.middleware.auth import get_current_user

# Router para tickets con prefijo y etiqueta
router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get(
    "/by-epic/{epic_id}",
    response_model=List[TicketResponse],
    summary="Listar tickets de una épica",
    description="Obtiene todos los tickets de una épica específica con sus detalles"
)
async def get_epic_tickets(
    epic_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filtrar por estado de ticket"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TicketResponse]:
    """
    Lista todos los tickets pertenecientes a una épica específica.

    Args:
        epic_id (int): ID de la épica
        skip (int): Número de registros a omitir
        limit (int): Máximo de registros a retornar
        status_filter (str): Filtro opcional por estado (TODO, IN_PROGRESS, COMPLETED)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[TicketResponse]: Lista de tickets con información de asignación y estado

    Raises:
        HTTPException: Si la épica no existe (404)
    """
    # Verificar que la épica existe
    from app.models import Epic
    epic_check = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    if not epic_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    # Construir consulta base
    query = select(Ticket).where(Ticket.epic_id == epic_id)

    # Aplicar filtro de estado si se proporciona
    if status_filter:
        query = query.where(Ticket.status == status_filter)

    # Ejecutar con paginación
    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    tickets = result.scalars().all()

    return [TicketResponse.from_orm(ticket) for ticket in tickets]


@router.get(
    "/my-workbench",
    response_model=List[TicketResponse],
    summary="Obtener banco de trabajo personal",
    description="Retorna todos los tickets asignados al usuario actual ordenados por prioridad"
)
async def get_my_workbench(
    status_filter: Optional[str] = Query(None),
    priority_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TicketResponse]:
    """
    Obtiene el banco de trabajo personal del usuario con tickets asignados.

    Args:
        status_filter (str): Filtro opcional por estado
        priority_filter (str): Filtro opcional por prioridad
        current_user (User): Usuario autenticado (obtenido de token)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[TicketResponse]: Tickets asignados al usuario ordenados por prioridad
    """
    # Construir consulta para obtener tickets asignados
    query = select(Ticket).where(Ticket.assigned_to == current_user.id)

    # Aplicar filtros si se proporcionan
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority_filter:
        query = query.where(Ticket.priority == priority_filter)

    # Ordenar por prioridad y fecha de creación
    result = await db.execute(
        query.order_by(Ticket.priority.desc(), Ticket.created_at.desc())
    )
    tickets = result.scalars().all()

    return [TicketResponse.from_orm(ticket) for ticket in tickets]


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo ticket",
    description="Crea un nuevo ticket en una épica específica"
)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Crea un nuevo ticket en una épica.

    Args:
        ticket_data (TicketCreate): Datos del nuevo ticket
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket creado

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en creación (400)
    """
    # Verificar que la épica existe
    from app.models import Epic
    epic_check = await db.execute(
        select(Epic).where(Epic.id == ticket_data.epic_id)
    )
    if not epic_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {ticket_data.epic_id} no encontrada"
        )

    try:
        # Crear nuevo ticket con estado inicial TODO
        new_ticket = Ticket(
            **ticket_data.dict(),
            status=TicketStatus.TODO,
            created_by=current_user.id
        )
        db.add(new_ticket)
        await db.commit()
        await db.refresh(new_ticket)

        # Registrar evento de creación
        await ticket_state_machine.log_ticket_event(
            db, new_ticket.id, TicketEventType.CREATED,
            current_user.id, f"Ticket creado por {current_user.name}"
        )

        return TicketResponse.from_orm(new_ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear ticket: {str(e)}"
        )


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Obtener ticket por ID",
    description="Recupera todos los detalles de un ticket incluyendo subtareas y asignado"
)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Obtiene los detalles completos de un ticket específico.

    Args:
        ticket_id (int): ID del ticket a obtener
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Datos del ticket con información de asignación y subtareas

    Raises:
        HTTPException: Si el ticket no existe (404)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    # Precargar información relacionada
    await db.refresh(ticket)

    return TicketResponse.from_orm(ticket)


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Actualizar ticket",
    description="Modifica los datos de un ticket (título, descripción, prioridad)"
)
async def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Actualiza los datos de un ticket.

    Args:
        ticket_id (int): ID del ticket a actualizar
        ticket_update (TicketUpdate): Nuevos datos del ticket
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket actualizado

    Raises:
        HTTPException: Si el ticket no existe (404) o hay error en actualización (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    try:
        # Aplicar cambios a los campos proporcionados
        update_data = ticket_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket, field, value)

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento de actualización
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.UPDATED,
            current_user.id, "Ticket actualizado"
        )

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar ticket: {str(e)}"
        )


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ticket",
    description="Elimina un ticket del sistema de forma permanente"
)
async def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina un ticket del sistema.

    Args:
        ticket_id (int): ID del ticket a eliminar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si el ticket no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    try:
        # Detener temporizador si está activo
        await timer_service.stop_timer(ticket_id, db)

        # Eliminar ticket y sus relaciones en cascada
        await db.delete(ticket)
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar ticket: {str(e)}"
        )


@router.patch(
    "/{ticket_id}/move",
    response_model=TicketResponse,
    summary="Mover ticket a otra épica",
    description="Permite arrastra-soltar (drag-drop) de tickets entre épicas"
)
async def move_ticket_to_epic(
    ticket_id: int,
    move_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Mueve un ticket de una épica a otra.

    Args:
        ticket_id (int): ID del ticket a mover
        move_data (dict): Contiene 'epic_id' con la épica destino
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket con épica actualizada

    Raises:
        HTTPException: Si el ticket o épica no existen (404) o hay error (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    new_epic_id = move_data.get("epic_id")

    # Verificar que la nueva épica existe
    from app.models import Epic
    epic_check = await db.execute(
        select(Epic).where(Epic.id == new_epic_id)
    )
    if not epic_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {new_epic_id} no encontrada"
        )

    try:
        old_epic_id = ticket.epic_id
        ticket.epic_id = new_epic_id

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento de movimiento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.MOVED,
            current_user.id, f"Ticket movido de épica {old_epic_id} a {new_epic_id}"
        )

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al mover ticket: {str(e)}"
        )


@router.post(
    "/{ticket_id}/start",
    response_model=TicketResponse,
    summary="Iniciar trabajo en ticket",
    description="Cambia estado TODO -> IN_PROGRESS e inicia el temporizador"
)
async def start_ticket_work(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Inicia el trabajo en un ticket (transición TODO -> IN_PROGRESS).

    Args:
        ticket_id (int): ID del ticket a iniciar
        current_user (User): Usuario autenticado (se convierte en asignado)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket con estado actualizado a IN_PROGRESS

    Raises:
        HTTPException: Si el ticket no existe (404) o no está en TODO (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    # Validar que el ticket está en estado TODO
    if ticket.status != TicketStatus.TODO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede iniciar un ticket en estado TODO, actual: {ticket.status}"
        )

    try:
        # Utilizar máquina de estados para cambiar estado
        await ticket_state_machine.transition_to_in_progress(ticket, current_user, db)

        # Iniciar temporizador
        await timer_service.start_timer(ticket_id, current_user.id, db)

        await db.commit()
        await db.refresh(ticket)

        # Enviar notificación
        await notification_service.notify_ticket_started(ticket, current_user, db)

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al iniciar ticket: {str(e)}"
        )


@router.post(
    "/{ticket_id}/complete",
    response_model=TicketResponse,
    summary="Completar ticket",
    description="Cambia estado IN_PROGRESS -> COMPLETED (requiere pull request link válido)"
)
async def complete_ticket(
    ticket_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Completa un ticket validando que hay un pull request link.

    Args:
        ticket_id (int): ID del ticket a completar
        completion_data (dict): Contiene 'pr_link' con el enlace al pull request
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket con estado actualizado a COMPLETED

    Raises:
        HTTPException: Si el ticket no existe (404), no está en IN_PROGRESS (400),
                      o no tiene PR link válido (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede completar un ticket en IN_PROGRESS, actual: {ticket.status}"
        )

    pr_link = completion_data.get("pr_link")
    if not pr_link or not pr_link.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pull request link inválido requerido para completar ticket"
        )

    try:
        # Detener temporizador
        await timer_service.stop_timer(ticket_id, db)

        # Utilizar máquina de estados para cambiar estado
        await ticket_state_machine.transition_to_completed(
            ticket, current_user, pr_link, db
        )

        await db.commit()
        await db.refresh(ticket)

        # Enviar notificación
        await notification_service.notify_ticket_completed(ticket, current_user, db)

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al completar ticket: {str(e)}"
        )


@router.post(
    "/{ticket_id}/question",
    response_model=TicketResponse,
    summary="Plantear pregunta bloqueante",
    description="Pausa el trabajo bloqueando el ticket con una pregunta"
)
async def raise_ticket_question(
    ticket_id: int,
    question_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Plantea una pregunta bloqueante en un ticket (pausa el temporizador).

    Args:
        ticket_id (int): ID del ticket
        question_data (dict): Contiene 'question' con el texto de la pregunta
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket marcado como bloqueado por pregunta

    Raises:
        HTTPException: Si el ticket no existe (404) o no está en IN_PROGRESS (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede plantear pregunta en IN_PROGRESS, actual: {ticket.status}"
        )

    try:
        # Pausar temporizador
        await timer_service.pause_timer(ticket_id, db)

        # Marcar como bloqueado
        ticket.is_blocked = True
        ticket.blocked_reason = question_data.get("question", "Pregunta sin especificar")

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.QUESTION_RAISED,
            current_user.id, question_data.get("question", "Pregunta planteada")
        )

        # Notificar al líder de equipo
        await notification_service.notify_question_raised(ticket, current_user, db)

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al plantear pregunta: {str(e)}"
        )


@router.post(
    "/{ticket_id}/resolve-question",
    response_model=TicketResponse,
    summary="Resolver pregunta bloqueante",
    description="Resuelve una pregunta y reanuda el temporizador"
)
async def resolve_ticket_question(
    ticket_id: int,
    resolution_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Resuelve una pregunta bloqueante y reanuda el trabajo.

    Args:
        ticket_id (int): ID del ticket
        resolution_data (dict): Contiene 'resolution' con la respuesta
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket desbloqueado y temporizador reanudado

    Raises:
        HTTPException: Si el ticket no existe (404) o no está bloqueado (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    if not ticket.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ticket no está bloqueado por una pregunta"
        )

    try:
        # Desbloquear ticket
        ticket.is_blocked = False
        ticket.blocked_reason = None

        # Reanudar temporizador
        await timer_service.resume_timer(ticket_id, db)

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.QUESTION_RESOLVED,
            current_user.id, resolution_data.get("resolution", "Pregunta resuelta")
        )

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al resolver pregunta: {str(e)}"
        )


@router.post(
    "/{ticket_id}/redirect",
    response_model=TicketResponse,
    summary="Redirigir ticket a otro usuario",
    description="Transfiere un ticket a otro usuario con motivo documentado"
)
async def redirect_ticket(
    ticket_id: int,
    redirect_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Redirige un ticket a otro usuario documentando el motivo.

    Args:
        ticket_id (int): ID del ticket a redirigir
        redirect_data (dict): Contiene 'target_user_id' y 'reason'
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket reasignado

    Raises:
        HTTPException: Si el ticket o usuario destino no existen (404) o hay error (400)
    """
    result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    target_user_id = redirect_data.get("target_user_id")
    reason = redirect_data.get("reason", "Sin motivo especificado")

    # Verificar que el usuario destino existe
    user_check = await db.execute(
        select(User).where(User.id == target_user_id)
    )
    if not user_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {target_user_id} no encontrado"
        )

    try:
        old_assignee = ticket.assigned_to
        ticket.assigned_to = target_user_id

        # Pausar temporizador si estaba activo
        if ticket.status == TicketStatus.IN_PROGRESS:
            await timer_service.pause_timer(ticket_id, db)

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento de redirección
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.REDIRECTED,
            current_user.id, f"Ticket redirigido de {old_assignee} a {target_user_id}: {reason}"
        )

        # Notificar al nuevo asignado
        await notification_service.notify_ticket_redirected(ticket, current_user, db)

        return TicketResponse.from_orm(ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al redirigir ticket: {str(e)}"
        )


@router.get(
    "/{ticket_id}/events",
    response_model=List[TicketEventResponse],
    summary="Obtener historial de eventos del ticket",
    description="Retorna todos los eventos registrados de un ticket (creación, cambios de estado, etc.)"
)
async def get_ticket_events(
    ticket_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TicketEventResponse]:
    """
    Obtiene el historial de eventos de un ticket.

    Args:
        ticket_id (int): ID del ticket
        skip (int): Número de eventos a omitir
        limit (int): Máximo de eventos a retornar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[TicketEventResponse]: Historial de eventos ordenado cronológicamente

    Raises:
        HTTPException: Si el ticket no existe (404)
    """
    # Verificar que el ticket existe
    ticket_check = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    if not ticket_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    # Obtener eventos ordenados por fecha descendente
    result = await db.execute(
        select(TicketEvent)
        .where(TicketEvent.ticket_id == ticket_id)
        .order_by(TicketEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    events = result.scalars().all()

    return [TicketEventResponse.from_orm(event) for event in events]
