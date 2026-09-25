"""
Router de Equipos (Teams).

Antes los equipos vivían solo en el `localStorage` del navegador del ADMIN, así
que en cualquier sesión nueva (otro navegador, otro equipo, una ventana privada)
desaparecían, mientras las aplicaciones y las épicas seguían llegando del
backend. Estos endpoints los persisten para que sean los mismos para todos:

- `GET  /api/teams/`      cualquier autenticado: el workbench lo necesita para
                          saber qué proyectos ve cada usuario y a quién puede
                          asignarle tickets.
- `POST /api/teams/`      ADMIN (crear)
- `PUT  /api/teams/{id}`  ADMIN (renombrar, cambiar miembros o aplicaciones)
- `DEL  /api/teams/{id}`  ADMIN (eliminar)

Como la gestión de equipos vive en `/admin`, el resto de roles solo leen.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models import Team, UserRole
from app.schemas import TeamCreate, TeamUpdate, TeamResponse

# Router con prefijo y etiqueta para la documentación
router = APIRouter(prefix="/teams", tags=["Equipos"])


async def _get_team_or_404(team_id: UUID, db: AsyncSession) -> Team:
    """Recupera un equipo por id o lanza 404 si no existe."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipo con ID {team_id} no encontrado"
        )

    return team


@router.get(
    "/",
    response_model=List[TeamResponse],
    summary="Listar equipos",
    description="Devuelve todos los equipos. Disponible para cualquier usuario autenticado."
)
async def list_teams(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[TeamResponse]:
    """
    Lista todos los equipos del sistema.

    Lo consume el store de equipos del frontend para el workbench (filtrar
    proyectos por equipo y limitar la asignación de tickets a los miembros).

    Args:
        current_user (User): Usuario autenticado (cualquier rol)
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        List[TeamResponse]: Equipos ordenados por fecha de creación
    """
    result = await db.execute(select(Team).order_by(Team.created_at.asc()))
    return [TeamResponse.model_validate(team) for team in result.scalars().all()]


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear equipo",
    description="Crea un equipo con sus miembros y aplicaciones (requiere rol ADMIN)"
)
async def create_team(
    team_data: TeamCreate,
    current_user = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> TeamResponse:
    """
    Crea un equipo nuevo.

    Args:
        team_data (TeamCreate): Nombre, descripción, miembros y aplicaciones
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TeamResponse: Equipo creado
    """
    team = Team(**team_data.model_dump())
    db.add(team)
    await db.commit()
    await db.refresh(team)

    return TeamResponse.model_validate(team)


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Actualizar equipo",
    description="Modifica nombre, miembros o aplicaciones de un equipo (requiere rol ADMIN)"
)
async def update_team(
    team_id: UUID,
    team_update: TeamUpdate,
    current_user = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> TeamResponse:
    """
    Actualiza solo los campos enviados (actualización parcial).

    El frontend lo usa tanto para editar el equipo como para asignarle o
    quitarle proyectos (manda únicamente `application_ids`).

    Args:
        team_id (UUID): ID del equipo a actualizar
        team_update (TeamUpdate): Campos a modificar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Returns:
        TeamResponse: Equipo actualizado

    Raises:
        HTTPException: Si el equipo no existe (404)
    """
    team = await _get_team_or_404(team_id, db)

    for field, value in team_update.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)

    return TeamResponse.model_validate(team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar equipo",
    description="Elimina un equipo del sistema (requiere rol ADMIN)"
)
async def delete_team(
    team_id: UUID,
    current_user = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Elimina un equipo de forma permanente.

    Args:
        team_id (UUID): ID del equipo a eliminar
        current_user (User): Usuario autenticado con rol ADMIN
        db (AsyncSession): Sesión asíncrona de base de datos

    Raises:
        HTTPException: Si el equipo no existe (404)
    """
    team = await _get_team_or_404(team_id, db)

    await db.delete(team)
    await db.commit()
