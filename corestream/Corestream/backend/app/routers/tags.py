from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import Tag, User
from app.schemas.ticket import TagCreate, TagResponse
from app.services.ticket_permissions import require_admin_or_leader

router = APIRouter(prefix="/tags", tags=["Etiquetas"])


@router.get("/", response_model=list[TagResponse])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TagResponse]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return [TagResponse.model_validate(tag) for tag in result.scalars().all()]


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    require_admin_or_leader(current_user)
    existing = await db.execute(select(Tag).where(Tag.name.ilike(data.name)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ya existe una etiqueta con ese nombre")
    tag = Tag(name=data.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    require_admin_or_leader(current_user)
    tag = await db.get(Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Etiqueta no encontrada")
    await db.delete(tag)
    # Sin el commit la fila seguía en la base de datos: el frontend la quitaba
    # de la lista local y "reaparecía" al recargar/refrescar los tickets.
    await db.commit()
    await db.commit()