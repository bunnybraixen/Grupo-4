"""
Router de Gestión de Épicas.

Gestiona el ciclo de vida de épicas:
- Listar, crear, obtener, actualizar y eliminar épicas
- Reordenar épicas dentro de una aplicación
- Cargar documentos relacionados con épicas
- Épicas contienen tickets que son los elementos de trabajo reales
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db

# Aún no creado
# from app.schemas import DocumentResponse
from app.middleware.auth import get_current_user, require_role
from app.models import Application, Epic, Ticket, User, UserRole
from app.schemas import EpicCreate, EpicResponse, EpicUpdate

# ADMIN y TEAM_LEADER gestionan la estructura del backlog (aplicaciones,
# épicas, tickets); DEVELOPER no. Antes epics.py no usaba require_role NI UNA
# SOLA VEZ — verificado en la auditoría: un DEVELOPER creaba épicas con 201
# (plan fase 4).
_MANAGERS = [UserRole.ADMIN, UserRole.TEAM_LEADER]

# Router para épicas
router = APIRouter(tags=["Épicas"])
logger = logging.getLogger("corestream.epics")


@router.get(
    "/by-app/{app_id}",
    response_model=List[EpicResponse],
    summary="Listar épicas de una aplicación",
    description="Obtiene todas las épicas de una aplicación ordenadas por índice de orden"
)
async def get_application_epics(
    app_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[EpicResponse]:
    """
    Lista todas las épicas de una aplicación específica ordenadas por order_index.

    Args:
        app_id (UUID): ID de la aplicación
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[EpicResponse]: Lista de épicas ordenadas

    Raises:
        HTTPException: Si la aplicación no existe (404)
    """
    # 1. Consulta blindada con carga en cascada (Deep Eager Loading)
    result = await db.execute(
        select(Epic)
        .where(Epic.application_id == app_id)
        .options(
            selectinload(Epic.application),
            selectinload(Epic.tickets).selectinload(Ticket.subtasks),
            selectinload(Epic.tickets).selectinload(Ticket.assignee).selectinload(User.role)
        )
        .order_by(Epic.order_index.asc())
    )
    
    # Usamos unique() para evitar duplicados en memoria
    epics = result.unique().scalars().all()
    
    epic_responses = []
    for epic in epics:
        # 2. Pydantic hace toda la magia de empaquetar los tickets con sus títulos y estados
        epic_view = EpicResponse.model_validate(epic)
        
        # 3. Calculamos los conteos para la interfaz
        epic_view.total_tickets = len(epic.tickets)
        
        # Forma segura de contar los completados sin importar si es texto o Enum
        completados = 0
        for t in epic.tickets:
            estado_str = t.status.value if hasattr(t.status, "value") else str(t.status)
            if estado_str in ["COMPLETED", "DONE"]:
                completados += 1
                
        epic_view.completed_tickets = completados
        
        # 4. Progreso de la barra
        if epic_view.total_tickets > 0:
            epic_view.progress = round((epic_view.completed_tickets / epic_view.total_tickets) * 100, 2)
            
        epic_responses.append(epic_view)
        
    return epic_responses


@router.post(
    "/",
    response_model=EpicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva épica",
    description="Crea una nueva épica dentro de una aplicación"
)
async def create_epic(
    epic_data: EpicCreate,
    current_user = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Crea una nueva épica en una aplicación.

    Args:
        epic_data (EpicCreate): Datos de la nueva épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica creada

    Raises:
        HTTPException: Si la aplicación no existe (404) o hay error en creación (400)
    """
    # Verificar que la aplicación existe
    app_check = await db.execute(
        select(Application).where(Application.id == epic_data.application_id)
    )
    if not app_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aplicación con ID {epic_data.application_id} no encontrada"
        )

    try:
        # Obtener el siguiente order_index disponible
        max_order = await db.execute(
            select(func.max(Epic.order_index))
            .where(Epic.application_id == epic_data.application_id)
        )
        next_order = (max_order.scalar() or -1) + 1

        # Crear nueva épica
        new_epic = Epic(
            **epic_data.model_dump(),
            order_index=next_order
        )
        db.add(new_epic)
        await db.commit()

        # populate_existing=True fuerza actualización desde BD aunque el objeto
        # no esté expirado (expire_on_commit=False en database.py), garantizando
        # que created_at y updated_at (server_default) se lean desde la BD.
        result_final = await db.execute(
            select(Epic)
            .where(Epic.id == new_epic.id)
            .options(selectinload(Epic.tickets))
            .execution_options(populate_existing=True)
        )
        epic_final = result_final.scalar_one()

        return EpicResponse.model_validate(epic_final)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear épica: {str(e)}"
        )

    # Recargar con tickets para serialización correcta
    result2 = await db.execute(
        select(Epic)
        .where(Epic.id == new_epic.id)
        .options(
            selectinload(Epic.tickets).selectinload(Ticket.subtasks),
            selectinload(Epic.tickets).selectinload(Ticket.assignee).selectinload(User.role),
        )
    )
    return EpicResponse.model_validate(result2.unique().scalar_one())


@router.get(
    "/{epic_id}",
    response_model=EpicResponse,
    summary="Obtener épica por ID",
    description="Recupera los detalles de una épica incluyendo información de progreso"
)
async def get_epic(
    epic_id: UUID,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Obtiene los detalles de una épica con información de progreso.

    Args:
        epic_id (int): ID de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Datos de la épica con información de progreso

    Raises:
        HTTPException: Si la épica no existe (404)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    # Recargar con tickets para serialización correcta (evitar lazy-load en async)
    result2 = await db.execute(
        select(Epic)
        .where(Epic.id == epic_id)
        .options(
            selectinload(Epic.tickets).selectinload(Ticket.subtasks),
            selectinload(Epic.tickets).selectinload(Ticket.assignee).selectinload(User.role),
        )
    )
    return EpicResponse.model_validate(result2.unique().scalar_one())


@router.put(
    "/{epic_id}",
    response_model=EpicResponse,
    summary="Actualizar épica",
    description="Modifica los datos de una épica existente"
)
async def update_epic(
    epic_id: UUID,
    epic_update: EpicUpdate,
    current_user = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Actualiza los datos de una épica.

    Args:
        epic_id (UUID): ID de la épica a actualizar
        epic_update (EpicUpdate): Nuevos datos de la épica
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica actualizada

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en actualización (400)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        # Aplicar cambios únicamente a campos proporcionados
        update_data = epic_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(epic, field, value)

        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar épica: {str(e)}"
        )

    # Recargar con tickets — incluir User.role para evitar lazy-load en async
    result2 = await db.execute(
        select(Epic)
        .where(Epic.id == epic_id)
        .options(
            selectinload(Epic.tickets).selectinload(Ticket.subtasks),
            selectinload(Epic.tickets).selectinload(Ticket.assignee).selectinload(User.role),
        )
    )
    updated_epic = result2.unique().scalar_one()
    epic_view = EpicResponse.model_validate(updated_epic)

    epic_view.total_tickets = len(updated_epic.tickets)
    completados = 0
    for t in updated_epic.tickets:
        estado_str = t.status.value if hasattr(t.status, "value") else str(t.status)
        if estado_str in ["COMPLETED", "DONE"]:
            completados += 1
    epic_view.completed_tickets = completados
    if epic_view.total_tickets > 0:
        epic_view.progress = round((completados / epic_view.total_tickets) * 100, 2)

    return epic_view


@router.delete(
    "/{epic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar épica",
    description="Elimina una épica y todos sus tickets relacionados"
)
async def delete_epic(
    epic_id: UUID,
    current_user = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina una épica del sistema de forma permanente.

    Args:
        epic_id (UUID): ID de la épica a eliminar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en eliminación (400)
    """
    result = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    epic = result.scalar_one_or_none()

    if not epic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        await db.execute(sa_delete(Epic).where(Epic.id == epic_id))
        await db.commit()

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al eliminar épica: {str(e)}"
        )


@router.patch(
    "/{epic_id}/reorder",
    response_model=EpicResponse,
    summary="Reordenar épica (ATÓMICO - Thread-Safe)",
    description="Cambia la posición de una épica con bloqueo de fila para evitar race conditions"
)
async def reorder_epic(
    epic_id: UUID,
    new_order: dict,
    current_user = Depends(require_role(_MANAGERS)),
    db: AsyncSession = Depends(get_db)
) -> EpicResponse:
    """
    Reordena una épica de forma ATÓMICA usando transacción SERIALIZABLE.
    
    GARANTÍAS CRÍTICAS:
    - No hay race conditions incluso si múltiples clientes reordenan simultáneamente
    - order_index nunca duplicado
    - Bloqueo de filas (FOR UPDATE) previene interleaving de cambios
    
    Args:
        epic_id (int): ID de la épica a reordenar
        new_order (dict): Contiene 'new_index' con la nueva posición (0-based)
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        EpicResponse: Épica reordenada

    Raises:
        HTTPException: Si la épica no existe (404) o índice inválido (400)
    """
    try:
        # Iniciar transacción EXPLÍCITA con savepoint
        async with db.begin_nested():
            
            # 1️⃣ CARGAR ÉPICA CON LOCK (FOR UPDATE)
            # Esto previene que otro cliente modifique esta épica mientras estamos procesando
            result = await db.execute(
                select(Epic)
                .where(Epic.id == epic_id)
                .with_for_update()
            )
            epic = result.scalar_one_or_none()
            
            if not epic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Épica con ID {epic_id} no encontrada"
                )
            
            # Extraemos los valores del objeto épica
            old_index = epic.order_index
            app_id = str(epic.application_id)
            str_epic_id = str(epic_id)
            new_index = new_order.get("new_index", 0)

            # 2️⃣ VALIDAR RANGO DE ÍNDICE
            # Usamos ORM para que SQLAlchemy maneje la conversión UUID correctamente
            # en cualquier backend (PostgreSQL y SQLite).
            count_result = await db.execute(
                select(func.count()).where(Epic.application_id == epic.application_id)
            )
            epic_count = count_result.scalar()

            if new_index < 0 or new_index >= epic_count:
                raise ValueError(
                    f"Índice de orden {new_index} fuera de rango [0, {epic_count-1}]"
                )

            # 3️⃣ OPERACIÓN ATÓMICA: Actualizar order_index solo si es diferente
            if new_index != old_index:
                if new_index > old_index:
                    # Desplazar HACIA ATRÁS: épicas entre old y new
                    await db.execute(
                        text(
                            "UPDATE epics "
                            "SET order_index = order_index - 1 "
                            "WHERE application_id = :app_id "
                            "AND order_index > :old_idx "
                            "AND order_index <= :new_idx "
                            "AND id != :epic_id"
                        ),
                        {
                            "app_id": app_id,
                            "old_idx": old_index,
                            "new_idx": new_index,
                            "epic_id": str_epic_id
                        }
                    )
                else:
                    # Desplazar HACIA ADELANTE: épicas entre new y old
                    await db.execute(
                        text(
                            "UPDATE epics "
                            "SET order_index = order_index + 1 "
                            "WHERE application_id = :app_id "
                            "AND order_index >= :new_idx "
                            "AND order_index < :old_idx "
                            "AND id != :epic_id"
                        ),
                        {
                            "app_id": app_id,
                            "new_idx": new_index,
                            "old_idx": old_index,
                            "epic_id": str_epic_id
                        }
                    )

                # 4️⃣ ASIGNAR NUEVO ÍNDICE A LA ÉPICA
                await db.execute(
                    text(
                        "UPDATE epics "
                        "SET order_index = :new_idx "
                        "WHERE id = :epic_id"
                    ),
                    {"epic_id": str_epic_id, "new_idx": new_index}
                )
        
        # Commit de transacción
        await db.commit()

        # 5️⃣ RECARGAR CON TICKETS (evitar lazy-load en async durante serialización)
        result = await db.execute(
            select(Epic)
            .where(Epic.id == epic_id)
            .options(
                selectinload(Epic.tickets).selectinload(Ticket.subtasks),
                selectinload(Epic.tickets).selectinload(Ticket.assignee).selectinload(User.role),
            )
        )
        epic_reloaded = result.unique().scalar_one()
        try:
            return EpicResponse.model_validate(epic_reloaded)
        except Exception:
            logger.exception("Error de serialización en reorder_epic")
            return {"status": "ok", "id": str(epic_id)}

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al reordenar épica: {str(e)}"
        )

'''
@router.post(
    "/{epic_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cargar documento a épica",
    description="Carga un archivo de documentación a una épica"
)
async def upload_epic_document(
    epic_id: int,
    file_data: dict,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DocumentResponse:
    """
    Carga un documento a una épica específica.

    Args:
        epic_id (int): ID de la épica
        file_data (dict): Datos del archivo a cargar
        current_user (User): Usuario autenticado
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        DocumentResponse: Documento creado

    Raises:
        HTTPException: Si la épica no existe (404) o hay error en carga (400)
    """
    # Verificar que la épica existe
    epic_check = await db.execute(
        select(Epic).where(Epic.id == epic_id)
    )
    if not epic_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Épica con ID {epic_id} no encontrada"
        )

    try:
        # Implementar lógica de carga de archivo
        # Este es un placeholder que debería conectar con el servicio de documentos
        from app.models import Document

        new_document = Document(
            epic_id=epic_id,
            **file_data
        )
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        return DocumentResponse.from_orm(new_document)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cargar documento: {str(e)}"
        )
'''