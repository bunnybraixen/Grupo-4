from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.incident import Incident
from app.models.role import UserRole
from app.models.user import User
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    IncidentUpdate,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Crea un nuevo incidente.
    """
    incident = Incident(
        **incident_in.model_dump(exclude_unset=True),
        created_by_id=current_user.id
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    
    return incident

@router.get("/", response_model=List[IncidentResponse])
async def get_incidents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene todos los incidentes.
    """
    query = select(Incident).order_by(Incident.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene un incidente por su ID.
    """
    query = select(Incident).filter(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
        
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_in: IncidentUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db),
):
    """
    Actualiza los detalles de un incidente.
    """
    query = select(Incident).filter(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
        
    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
        
    await db.commit()
    await db.refresh(incident)
    return incident

@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: UUID,
    status_in: IncidentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Actualiza el estado de un incidente.
    """
    query = select(Incident).filter(Incident.id == incident_id)
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
        
    incident.status = status_in.status
    await db.commit()
    await db.refresh(incident)
    return incident

