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

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from enum import Enum
import re
from app.database import get_db
from app.models import (
    Ticket,
    User,
    Epic,
    TicketStatus,
    TicketEvent,
    TicketEventType,
    Subtask,
    TicketComment,
    Tag,
)
from app.schemas import (
    TicketResponse,
    TicketCreate,
    TicketUpdate,
    TicketEventResponse,
    TicketQuestion,
    TicketCommentCreate,
    TicketCommentUpdate,
    TicketCommentResponse,
    TicketTagsUpdate,
)
from app.services import ticket_state_machine, timer_service, notification_service

from app.services.ticket_permissions import (
    assert_can_manage_ticket,
    assert_is_current_assignee,
    claim_or_assert_assignee,
    get_user_id,
    is_admin_or_leader,
    require_admin_or_leader,
    require_non_admin,
)
from app.middleware.auth import get_current_user

# Router para tickets con prefijo y etiqueta
router = APIRouter(prefix="/tickets", tags=["Tickets"])

def extract_mentions(content: str) -> list[str]:
    """
    Extrae posibles menciones con formato @Nombre.

    Ejemplo:
        "@Administrador revisa este comentario"

    Retorna:
        ["Administrador"]
    """
    matches = re.findall(
        r"@([A-Za-zÁÉÍÓÚáéíóúÑñÜü0-9_.-]+)",
        content,
    )

    return list(dict.fromkeys(matches))

async def resolve_mentions(
    mention_candidates: list[str],
    db: AsyncSession,
) -> list[User]:
    """
    Resuelve las menciones contra usuarios activos de CoreStream.

    La comparación se realiza usando el nombre completo o el correo
    electrónico del usuario, ignorando mayúsculas y minúsculas.
    """
    if not mention_candidates:
        return []

    result = await db.execute(
        select(User).where(
            User.is_active.is_(True)
        )
    )

    users = result.scalars().all()

    resolved_users: list[User] = []

    for candidate in mention_candidates:
        candidate_normalized = candidate.strip().lower()

        for user in users:
            full_name_normalized = user.full_name.strip().lower()
            email_normalized = user.email.strip().lower()

            if (
                full_name_normalized == candidate_normalized
                or email_normalized == candidate_normalized
            ):
                if user not in resolved_users:
                    resolved_users.append(user)

    return resolved_users

def _ticket_query():
    """
    Consulta base de Ticket con las relaciones que serializa TicketResponse.

    `assignee` y `subtasks` son relaciones (lazy por defecto): si no se cargan
    aquí, Pydantic intenta resolverlas al construir la respuesta y el lazy-load
    ocurre fuera del contexto async -> MissingGreenlet (HTTP 500). Cargarlas de
    forma explícita es además la convención documentada en app/models/base.py.
    """
    return select(Ticket).options(
        selectinload(Ticket.assignee),
        selectinload(Ticket.subtasks),
        selectinload(Ticket.tags),
    )


async def _load_ticket(db: AsyncSession, ticket_id) -> Optional[Ticket]:
    """Recarga un ticket por id con todas sus relaciones ya cargadas."""
    result = await db.execute(_ticket_query().where(Ticket.id == ticket_id))
    return result.scalar_one_or_none()


def _json_safe(value):
    """
    Normaliza valores ORM (UUID, Enum, datetime) para guardarlos en el JSON
    `detail` de un TicketEvent (WEB-11).
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    return str(value)


@router.get(
    "/",
    response_model=List[TicketResponse],
    summary="Listar tickets",
    description="Obtiene tickets, opcionalmente filtrados por épica y estado"
    )
async def list_tickets(
    epic_id: Optional[UUID] = Query(None, description="Filtrar por épica"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TicketStatus] = Query(
        None, description="Filtrar por estado (TODO, IN_PROGRESS, BLOCKED, REDIRECTED, DONE)"
    ),
    tag_ids: Optional[List[UUID]] = Query(None, description="Filtrar por una o más etiquetas"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TicketResponse]:
    """
    Lista tickets con filtros opcionales de épica y estado.

    Returns:
        List[TicketResponse]: Tickets con sus relaciones precargadas
    """
    query = _ticket_query()

    if epic_id is not None:
        query = query.where(Ticket.epic_id == epic_id)

    if status_filter:
        query = query.where(Ticket.status == status_filter)

    if tag_ids:
        query = query.join(Ticket.tags).where(Tag.id.in_(tag_ids)).distinct()

    # Orden estable (antes no había ORDER BY y PostgreSQL podía devolver las
    # filas en otro orden tras un UPDATE: los tickets "saltaban" al editarlos).
    result = await db.execute(
        query.order_by(Ticket.order_index.asc(), Ticket.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    tickets = result.scalars().all()

    return [TicketResponse.from_orm(ticket) for ticket in tickets]


@router.get(
    "/by-epic/{epic_id}",
    response_model=List[TicketResponse],
    summary="Listar tickets de una épica",
    description="Obtiene todos los tickets de una épica específica con sus detalles"
)
async def get_epic_tickets(
    epic_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TicketStatus] = Query(
        None, description="Filtrar por estado (TODO, IN_PROGRESS, BLOCKED, REDIRECTED, DONE)"
    ),
    tag_ids: Optional[List[UUID]] = Query(None, description="Filtrar por una o más etiquetas"),
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

    # Construir consulta base (con relaciones ya cargadas)
    query = _ticket_query().where(Ticket.epic_id == epic_id)

    # Aplicar filtro de estado si se proporciona
    if status_filter:
        query = query.where(Ticket.status == status_filter)

    if tag_ids:
        query = query.join(Ticket.tags).where(Tag.id.in_(tag_ids)).distinct()

    # Ejecutar con paginación y orden estable dentro de la épica
    result = await db.execute(
        query.order_by(Ticket.order_index.asc(), Ticket.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    tickets = result.scalars().all()

    return [TicketResponse.from_orm(ticket) for ticket in tickets]


@router.put("/{ticket_id}/tags", response_model=TicketResponse)
async def update_ticket_tags(
    ticket_id: UUID,
    data: TicketTagsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    ticket = await _load_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    assert_can_manage_ticket(ticket, current_user)
    result = await db.execute(select(Tag).where(Tag.id.in_(data.tag_ids)))
    tags = result.scalars().all()
    if len(tags) != len(set(data.tag_ids)):
        raise HTTPException(status_code=404, detail="Una o más etiquetas no existen")
    ticket.tags = tags
    await db.commit()

    # WEB-11: el cambio de etiquetas también queda en el historial, con los
    # nombres para que el detalle del ticket sea legible.
    tag_names = [tag.name for tag in tags]
    await ticket_state_machine.log_ticket_event(
        db, ticket_id, TicketEventType.UPDATED,
        get_user_id(current_user),
        {
            "message": "Etiquetas actualizadas: "
            + (", ".join(tag_names) if tag_names else "sin etiquetas"),
            "tags": tag_names,
        },
    )

    return TicketResponse.from_orm(await _load_ticket(db, ticket_id))


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
    # Construir consulta para obtener tickets asignados (con relaciones cargadas)
    query = _ticket_query().where(Ticket.assignee_id == UUID(get_user_id(current_user)))

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

    # WEB-08: crear tickets es una acción de gestión -> ADMIN o TEAM_LEADER.
    require_admin_or_leader(current_user)

    # `get_current_user` devuelve el TokenPayload del JWT (sub/role/exp), no la
    # fila del usuario: `current_user.id` / `.name` no existen y la creación
    # fallaba con 400. Se resuelve el usuario real a partir del claim `sub`.
    actor_id = getattr(current_user, "id", None) or getattr(current_user, "sub", None)
    try:
        actor_uuid = actor_id if isinstance(actor_id, UUID) else UUID(str(actor_id))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de usuario inválido"
        )

    actor_result = await db.execute(select(User).where(User.id == actor_uuid))
    actor = actor_result.scalar_one_or_none()
    actor_name = actor.full_name if actor else "Sistema"

    try:
        # Orden estable dentro de la épica: el ticket nuevo va al final.
        # Antes NO se asignaba `order_index`, así que todos los tickets quedaban
        # en 0 y el orden dependía del plan de PostgreSQL (cambiaba solo).
        max_order = await db.execute(
            select(func.max(Ticket.order_index)).where(
                Ticket.epic_id == ticket_data.epic_id
            )
        )
        current_max = max_order.scalar()
        next_order = 0 if current_max is None else int(current_max) + 1

        # Crear nuevo ticket. `status` viene del payload (por defecto TODO) y la
        # autoría se guarda en la FK `created_by_id`: `created_by` es la relación
        # ORM, no una columna, y asignarle un UUID la rompía.
        new_ticket = Ticket(
            **ticket_data.model_dump(),
            created_by_id=actor_uuid,
            order_index=next_order,
        )
        db.add(new_ticket)
        await db.commit()

        # Registrar evento de creación
        await ticket_state_machine.log_ticket_event(
            db, new_ticket.id, TicketEventType.CREATED,
            actor_uuid, f"Ticket creado por {actor_name}"
        )

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        created_ticket = await _load_ticket(db, new_ticket.id)
        return TicketResponse.from_orm(created_ticket)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear ticket: {str(e)}"
        )


@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear comentario en ticket",
    description="Crea un comentario asociado al ticket y al usuario autenticado",
)
async def create_ticket_comment(
    ticket_id: UUID,
    comment_data: TicketCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketCommentResponse:

    # Verificar que el ticket existe
    ticket_result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = ticket_result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado",
        )

    mention_candidates = extract_mentions(comment_data.content)

    mentioned_users = await resolve_mentions(
        mention_candidates,
        db,
    )

    print(
    "MENCIONES DETECTADAS:",
    mention_candidates,
    )

    print(
        "USUARIOS MENCIONADOS:",
        [
            {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
            }
            for user in mentioned_users
        ],
    )

    # Obtener el UUID real del usuario desde el JWT
    try:
        actor_id = get_user_id(current_user)
        actor_uuid = (
            actor_id
            if isinstance(actor_id, UUID)
            else UUID(str(actor_id))
        )
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de usuario inválido",
        )

    # Verificar que el usuario exista en PostgreSQL
    user_result = await db.execute(
        select(User).where(User.id == actor_uuid)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario autenticado no encontrado",
        )

    try:
        new_comment = TicketComment(
            ticket_id=ticket_id,
            user_id=actor_uuid,
            content=comment_data.content,
        )

        db.add(new_comment)
        await db.commit()

        # Crear notificaciones para los usuarios mencionados
        for mentioned_user in mentioned_users:

            # No notificar al propio autor del comentario
            if mentioned_user.id == actor_uuid:
                continue

            await notification_service.NotificationService.create_notification(
                db=db,
                user_id=str(mentioned_user.id),
                title="Te mencionaron en un comentario",
                message=(
                    f"{user.full_name} te mencionó en un comentario "
                    f"del ticket: {ticket.title}"
                ),
                notification_type="SYSTEM",
                ticket_id=str(ticket_id),
            )

        comment_result = await db.execute(
            select(TicketComment)
            .options(selectinload(TicketComment.user))
            .where(TicketComment.id == new_comment.id)
        )

        created_comment = comment_result.scalar_one()

        return TicketCommentResponse.from_orm(created_comment)

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear comentario: {str(e)}",
        )


@router.get(
    "/{ticket_id}/comments",
    response_model=List[TicketCommentResponse],
    summary="Obtener comentarios de un ticket",
    description="Obtiene el historial de comentarios asociados a un ticket, ordenados por fecha de creación",
)
async def get_ticket_comments(
    ticket_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[TicketCommentResponse]:

    # Verificar que el ticket existe
    ticket_result = await db.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    ticket = ticket_result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado",
        )

    # Obtener comentarios junto con el usuario que los creó
    comments_result = await db.execute(
        select(TicketComment)
        .options(selectinload(TicketComment.user))
        .where(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at.asc())
    )

    comments = comments_result.scalars().all()

    return [
        TicketCommentResponse.from_orm(comment)
        for comment in comments
    ]


@router.put(
    "/{ticket_id}/comments/{comment_id}",
    response_model=TicketCommentResponse,
    summary="Editar comentario de un ticket",
    description="Permite al autor editar su propio comentario.",
)
async def update_ticket_comment(
    ticket_id: UUID,
    comment_id: UUID,
    comment_data: TicketCommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TicketCommentResponse:

    result = await db.execute(
        select(TicketComment)
        .options(selectinload(TicketComment.user))
        .where(
            and_(
                TicketComment.id == comment_id,
                TicketComment.ticket_id == ticket_id,
            )
        )
    )

    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado",
        )

    # get_user_id() entrega el UUID como string en el TokenPayload.
    # Lo convertimos a UUID para compararlo con comment.user_id.
    current_user_id = UUID(get_user_id(current_user))

    if comment.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para editar este comentario",
        )

    comment.content = comment_data.content

    await db.commit()

    # Recargar incluyendo el usuario para la respuesta
    result = await db.execute(
        select(TicketComment)
        .options(selectinload(TicketComment.user))
        .where(TicketComment.id == comment_id)
    )

    updated_comment = result.scalar_one()

    return TicketCommentResponse.from_orm(updated_comment)
    
@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Obtener detalle de un ticket",
    description="Devuelve el ticket con épica, asignado, subtareas y etiquetas"
)
async def get_ticket(
    ticket_id: UUID,
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
    ticket = await _load_ticket(db, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    # Las relaciones ya vienen precargadas por _load_ticket/_ticket_query:
    # refrescar aquí volvía a expirarlas y provocaba el 500 por MissingGreenlet
    # al construir la respuesta.
    return TicketResponse.from_orm(ticket)


@router.delete(
    "/{ticket_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar comentario de un ticket",
    description="Permite al autor eliminar su propio comentario.",
)
async def delete_ticket_comment(
    ticket_id: UUID,
    comment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(TicketComment).where(
            and_(
                TicketComment.id == comment_id,
                TicketComment.ticket_id == ticket_id,
            )
        )
    )

    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado",
        )

    current_user_id = UUID(get_user_id(current_user))

    if comment.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este comentario",
        )

    await db.delete(comment)
    await db.commit()

    return None

@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
    summary="Actualizar ticket",
    description="Modifica los datos de un ticket (título, descripción, prioridad)"
)
async def update_ticket(
    ticket_id: UUID,
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

    # WEB-08: ADMIN/TEAM_LEADER siempre; un DEVELOPER solo sobre sus propios tickets
    assert_can_manage_ticket(ticket, current_user)

    # Estado previo: permite distinguir un cambio de estado de una edición normal
    previous_status = ticket.status

    try:
        # Aplicar solo los campos enviados (actualización parcial)
        update_data = ticket_update.model_dump(exclude_unset=True)

        # El orden SOLO cambia con el drag & drop (PATCH /{id}/reorder): si se
        # aplicara aquí, cualquier edición de campos podría reordenar el tablero.
        update_data.pop("order_index", None)

        # WEB-11: datos relevantes de la acción -> diff de los campos cambiados
        changes: dict = {}
        for field, value in update_data.items():
            current_value = getattr(ticket, field, None)
            if current_value != value:
                changes[field] = {
                    "from": _json_safe(current_value),
                    "to": _json_safe(value),
                }
            setattr(ticket, field, value)

        await db.commit()
        await db.refresh(ticket)

        # Auditar el cambio: un cambio de estado se registra como STATUS_CHANGED,
        # un cambio de asignado como TICKET_ASSIGNED y cualquier otra edición de
        # campos como UPDATED (WEB-08/WEB-11: historial de eventos).
        if previous_status != ticket.status:
            previous_value = getattr(previous_status, "value", previous_status)
            current_value = getattr(ticket.status, "value", ticket.status)
            await ticket_state_machine.log_ticket_event(
                db, ticket_id, TicketEventType.STATUS_CHANGED,
                get_user_id(current_user),
                {
                    "message": f"Estado cambiado: {previous_value} -> {current_value}",
                    "from_status": str(previous_value),
                    "to_status": str(current_value),
                    "changes": changes,
                },
            )
        elif "assignee_id" in changes:
            await ticket_state_machine.log_ticket_event(
                db, ticket_id, TicketEventType.TICKET_ASSIGNED,
                get_user_id(current_user),
                {"message": "Asignación del ticket actualizada", "changes": changes},
            )
        else:
            await ticket_state_machine.log_ticket_event(
                db, ticket_id, TicketEventType.UPDATED,
                get_user_id(current_user),
                {
                    "message": "Ticket actualizado: "
                    + (", ".join(changes) if changes else "sin cambios"),
                    "changes": changes,
                },
            )

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    ticket_id: UUID,
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

    # WEB-08: el borrado es permanente y en cascada -> solo ADMIN/TEAM_LEADER
    require_admin_or_leader(current_user)

    try:
        # Detener temporizador si está activo (si el servicio expone la función:
        # `timer_service` solo tiene métodos de clase, ver /start)
        stop_timer = getattr(timer_service, "stop_timer", None)
        if callable(stop_timer):
            await stop_timer(ticket_id, db)

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
    ticket_id: UUID,
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

    # WEB-08: mover de épica es una acción de gestión -> ADMIN/TEAM_LEADER o el asignado
    assert_can_manage_ticket(ticket, current_user)

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

        # Al cambiar de épica el ticket va al FINAL de la destino: con el índice
        # viejo podría caer en medio de una lista ajena. Desde ahí solo lo mueve
        # el drag & drop (PATCH /{id}/reorder).
        max_order = await db.execute(
            select(func.max(Ticket.order_index)).where(Ticket.epic_id == new_epic_id)
        )
        current_max = max_order.scalar()
        ticket.order_index = 0 if current_max is None else int(current_max) + 1

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento de movimiento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.MOVED,
            get_user_id(current_user), f"Ticket movido de épica {old_epic_id} a {new_epic_id}"
        )

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al mover ticket: {str(e)}"
        )


@router.patch(
    "/{ticket_id}/reorder",
    response_model=TicketResponse,
    summary="Reordenar ticket dentro de su épica",
    description="Mueve el ticket a la posición indicada (drag & drop) y renumera el resto de la épica"
)
async def reorder_ticket(
    ticket_id: UUID,
    new_order: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Cambia el orden de un ticket dentro de su épica.

    Es la ÚNICA vía que modifica `order_index`: cualquier otro endpoint deja el
    orden intacto, de modo que los tickets solo se mueven con drag & drop.

    Args:
        ticket_id (UUID): ID del ticket a mover
        new_order (dict): Contiene 'new_index' con la posición destino (0-based)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket con su nueva posición

    Raises:
        HTTPException: Si el ticket no existe (404), el índice no es válido (422)
                       o hay error al guardar (400)
    """
    ticket = await _load_ticket(db, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket con ID {ticket_id} no encontrado"
        )

    # WEB-08: reordenar es una acción de gestión -> ADMIN/TEAM_LEADER o el asignado
    assert_can_manage_ticket(ticket, current_user)

    try:
        new_index = int(new_order.get("new_index", 0))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'new_index' debe ser un número entero"
        )

    try:
        # Todos los hermanos de la épica, en el mismo orden que se muestra en la UI
        siblings_result = await db.execute(
            select(Ticket)
            .where(Ticket.epic_id == ticket.epic_id)
            .order_by(Ticket.order_index.asc(), Ticket.created_at.asc())
        )
        siblings = list(siblings_result.scalars().all())

        current_index = next(
            (index for index, item in enumerate(siblings) if item.id == ticket.id),
            0,
        )
        # Se acota el destino para no dejar huecos
        new_index = max(0, min(new_index, len(siblings) - 1))

        if new_index != current_index:
            siblings.pop(current_index)
            siblings.insert(new_index, ticket)

            # Renumerar 0..n-1: normaliza los tickets antiguos que quedaron
            # todos con order_index=0 (por eso el orden parecía aleatorio).
            for index, item in enumerate(siblings):
                item.order_index = index

            await db.commit()

            # WEB-11: el reordenado queda registrado en el historial
            await ticket_state_machine.log_ticket_event(
                db, ticket_id, TicketEventType.UPDATED,
                get_user_id(current_user),
                {
                    "message": f"Orden cambiado: {current_index} -> {new_index}",
                    "action": "REORDERED",
                    "from_index": current_index,
                    "to_index": new_index,
                },
            )

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al reordenar ticket: {str(e)}"
        )


@router.post(
    "/{ticket_id}/start",
    response_model=TicketResponse,
    summary="Iniciar trabajo en ticket",
    description="Cambia estado TODO -> IN_PROGRESS e inicia el temporizador"
)
async def start_ticket_work(
    ticket_id: UUID,
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

    # WEB-08: iniciar trabajo es una acción "de trabajo". Un DEVELOPER solo
    # puede iniciar un ticket libre o ya asignado a él; los managers
    # (ADMIN/TEAM_LEADER) SÍ pueden iniciarlo desde /admin/builder, que es una
    # vista de administración (antes respondía 403 para el propio ADMIN, que es
    # el caso que reportó el equipo: "El botón de iniciar no aparece / da 403").
    if not is_admin_or_leader(current_user):
        require_non_admin(current_user)
        claim_or_assert_assignee(ticket, current_user)
    actor_id = get_user_id(current_user)

    # Validar que el ticket está en estado TODO
    if ticket.status != TicketStatus.TODO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede iniciar un ticket en estado TODO, actual: {ticket.status}"
        )

    try:
        # Utilizar máquina de estados para cambiar estado
        await ticket_state_machine.transition_to_in_progress(ticket, current_user, db)

        # Iniciar temporizador. `timer_service` solo expone métodos de clase
        # (no existe `timer_service.start_timer`) y el modelo Ticket tampoco
        # tiene columna de timer, así que se llama solo si está disponible: el
        # cambio de estado no debe caerse por una pieza sin implementar.
        start_timer = getattr(timer_service, "start_timer", None)
        if callable(start_timer):
            await start_timer(ticket_id, actor_id, db)

        await db.commit()
        await db.refresh(ticket)

        # Enviar notificación (misma situación: `notify_ticket_started` no existe
        # todavía en notification_service, así que se omite sin romper el flujo).
        notify_started = getattr(notification_service, "notify_ticket_started", None)
        if callable(notify_started):
            await notify_started(ticket, current_user, db)

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    description="Cambia estado IN_PROGRESS -> COMPLETED (el enlace de pull request es opcional)"
)
async def complete_ticket(
    ticket_id: UUID,
    completion_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Completa un ticket. El enlace de pull request es opcional; si se envía,
    debe ser una URL http(s) válida.

    Args:
        ticket_id (int): ID del ticket a completar
        completion_data (dict): Puede incluir 'pr_link' con el enlace al pull request
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TicketResponse: Ticket con estado actualizado a COMPLETED

    Raises:
        HTTPException: Si el ticket no existe (404), no está en IN_PROGRESS (400),
                      o el PR informado no es una URL válida (400)
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

    # WEB-08: completar es una acción "de trabajo" -> solo el asignado actual.
    # Los managers (ADMIN/TEAM_LEADER) pueden completarlo desde /admin/builder.
    if not is_admin_or_leader(current_user):
        require_non_admin(current_user)
        assert_is_current_assignee(ticket, current_user)
    actor_id = get_user_id(current_user)

    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede completar un ticket en IN_PROGRESS, actual: {ticket.status}"
        )

    pr_link = (completion_data.get("pr_link") or "").strip()
    # El PR es OPCIONAL: hay tickets que se cierran legítimamente sin PR
    # (spikes, cambios de configuración, tickets cancelados o duplicados), y
    # exigirlo bloqueaba al propio desarrollador asignado (400). Si se informa
    # un enlace, sí se valida que sea una URL http(s).
    if pr_link and not pr_link.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace del Pull Request debe empezar por http:// o https://"
        )

    try:
        # Detener temporizador (si el servicio expone la función; ver /start)
        stop_timer = getattr(timer_service, "stop_timer", None)
        if callable(stop_timer):
            await stop_timer(ticket_id, db)

        # Utilizar máquina de estados para cambiar estado
        await ticket_state_machine.transition_to_completed(
            ticket, current_user, pr_link, db
        )

        await db.commit()
        await db.refresh(ticket)

        # Enviar notificación (si existe; `notify_ticket_completed` no está
        # implementada en notification_service todavía)
        notify_completed = getattr(notification_service, "notify_ticket_completed", None)
        if callable(notify_completed):
            await notify_completed(ticket, current_user, db)

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    ticket_id: UUID,
    question_data: TicketQuestion,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TicketResponse:
    """
    Plantea una pregunta bloqueante en un ticket (pausa el temporizador).

    Args:
        ticket_id (int): ID del ticket
        question_data (TicketQuestion): Texto de la pregunta (mínimo 10 caracteres)
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

    # WEB-08: plantear una pregunta bloqueante es una acción "de trabajo"
    require_non_admin(current_user)
    assert_is_current_assignee(ticket, current_user)
    actor_id = get_user_id(current_user)

    if ticket.status != TicketStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se puede plantear pregunta en IN_PROGRESS, actual: {ticket.status}"
        )

    try:
        # Pausar temporizador (si el servicio expone la función; ver /start)
        pause_timer = getattr(timer_service, "pause_timer", None)
        if callable(pause_timer):
            await pause_timer(ticket_id, db)

        # Marcar como bloqueado
        ticket.is_blocked = True
        ticket.blocked_reason = question_data.question_text

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.QUESTION_RAISED,
            actor_id, question_data.question_text
        )

        # Notificar al líder de equipo (si existe; ver /start)
        notify_question = getattr(notification_service, "notify_question_raised", None)
        if callable(notify_question):
            await notify_question(ticket, current_user, db)

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    ticket_id: UUID,
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

    # WEB-08: resolver la pregunta es del asignado; si es ajena, requiere gestión
    if str(ticket.assignee_id) != get_user_id(current_user):
        require_admin_or_leader(current_user)

    if not ticket.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ticket no está bloqueado por una pregunta"
        )

    try:
        # Desbloquear ticket
        ticket.is_blocked = False
        ticket.blocked_reason = None

        # Reanudar temporizador (si el servicio expone la función; ver /start)
        resume_timer = getattr(timer_service, "resume_timer", None)
        if callable(resume_timer):
            await resume_timer(ticket_id, db)

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.QUESTION_RESOLVED,
            get_user_id(current_user), resolution_data.get("resolution", "Pregunta resuelta")
        )

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    ticket_id: UUID,
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

    # WEB-08: solo el asignado actual (o ADMIN/TEAM_LEADER) puede redirigir
    if ticket.assignee_id is not None and str(ticket.assignee_id) != get_user_id(current_user):
        require_admin_or_leader(current_user)

    # La API acepta las dos formas de nombrar los campos: 'to_user_id' (contrato
    # de los tests de integración) y 'target_user_id'/'reason' (forma histórica).
    target_user_id = redirect_data.get("to_user_id") or redirect_data.get("target_user_id")
    reason = (
        redirect_data.get("justification")
        or redirect_data.get("reason")
        or "Sin motivo especificado"
    )

    if not target_user_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Se requiere 'to_user_id' con el usuario destino"
        )

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
        old_assignee = ticket.assignee_id
        ticket.assignee_id = target_user_id

        # Pausar temporizador si estaba activo (si el servicio expone la función)
        pause_timer = getattr(timer_service, "pause_timer", None)
        if ticket.status == TicketStatus.IN_PROGRESS and callable(pause_timer):
            await pause_timer(ticket_id, db)

        await db.commit()
        await db.refresh(ticket)

        # Registrar evento de redirección
        await ticket_state_machine.log_ticket_event(
            db, ticket_id, TicketEventType.REDIRECTED,
            get_user_id(current_user), f"Ticket redirigido de {old_assignee} a {target_user_id}: {reason}"
        )

        # Notificar al nuevo asignado (si existe; ver /start)
        notify_redirected = getattr(notification_service, "notify_ticket_redirected", None)
        if callable(notify_redirected):
            await notify_redirected(ticket, current_user, db)

        # Recargar con relaciones antes de serializar (evita el 500 por lazy-load)
        return TicketResponse.from_orm(await _load_ticket(db, ticket_id))

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
    ticket_id: UUID,
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

    # WEB-11: historial en orden cronológico (el más antiguo primero; el `id`
    # como desempate mantiene el orden determinista cuando varios eventos
    # comparten `created_at`). El autor se precarga porque
    # `TicketEventResponse.user` es un UserResponse: sin el eager-load, el
    # lazy-load fuera del contexto async revienta con MissingGreenlet (500).
    # Ojo: `User.role` es una COLUMNA (enum), no una relación, así que no hay
    # que (ni se puede) cargarla aparte.
    result = await db.execute(
        select(TicketEvent)
        .options(selectinload(TicketEvent.user))
        .where(TicketEvent.ticket_id == ticket_id)
        .order_by(TicketEvent.created_at.asc(), TicketEvent.id.asc())
        .offset(skip)
        .limit(limit)
    )
    events = result.scalars().all()

    return [TicketEventResponse.model_validate(event) for event in events]
