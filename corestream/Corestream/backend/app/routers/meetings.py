from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.middleware.auth import get_current_user, require_role
from app.models.meeting import Meeting, MeetingAttendance
from app.models.role import UserRole
from app.models.user import User
from app.schemas.meeting import (
    MeetingAttendanceCreate,
    MeetingAttendanceResponse,
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
)

router = APIRouter(prefix="/meetings", tags=["meetings"])

@router.post("/", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meeting_in: MeetingCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db),
):
    """
    Programa una nueva reunión. Solo Administradores o Líderes de Equipo.
    """
    meeting = Meeting(
        **meeting_in.model_dump(exclude_unset=True),
        created_by_id=current_user.id
    )
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting, ["attendances"])
    return meeting

@router.get("/", response_model=List[MeetingResponse])
async def get_meetings(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene todas las reuniones programadas.
    """
    query = select(Meeting).options(selectinload(Meeting.attendances)).order_by(Meeting.scheduled_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una reunión por su ID.
    """
    query = select(Meeting).options(selectinload(Meeting.attendances)).filter(Meeting.id == meeting_id)
    result = await db.execute(query)
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reunión no encontrada")
        
    return meeting

@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: UUID,
    meeting_in: MeetingUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db),
):
    """
    Actualiza los detalles de una reunión.
    """
    query = select(Meeting).options(selectinload(Meeting.attendances)).filter(Meeting.id == meeting_id)
    result = await db.execute(query)
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reunión no encontrada")
        
    update_data = meeting_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
        
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.post("/{meeting_id}/attendance", response_model=MeetingAttendanceResponse, status_code=status.HTTP_201_CREATED)
async def record_attendance(
    meeting_id: UUID,
    attendance_in: MeetingAttendanceCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.TEAM_LEADER])),
    db: AsyncSession = Depends(get_db),
):
    """
    Registra la asistencia de un participante a la reunión.
    """
    # Verificar que la reunión exista
    query = select(Meeting).filter(Meeting.id == meeting_id)
    result = await db.execute(query)
    meeting = result.scalar_one_or_none()
    
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reunión no encontrada")
        
    # Crear o actualizar registro de asistencia
    attendance_query = select(MeetingAttendance).filter(
        MeetingAttendance.meeting_id == meeting_id,
        MeetingAttendance.user_id == attendance_in.user_id
    )
    result = await db.execute(attendance_query)
    attendance = result.scalar_one_or_none()
    
    if attendance:
        attendance.status = attendance_in.status
        if attendance_in.notes is not None:
            attendance.notes = attendance_in.notes
    else:
        attendance = MeetingAttendance(
            meeting_id=meeting_id,
            **attendance_in.model_dump(exclude_unset=True)
        )
        db.add(attendance)
        
    await db.commit()
    await db.refresh(attendance)
    return attendance
