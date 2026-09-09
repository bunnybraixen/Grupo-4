"""
Router para la redirección de tickets (CS-020).

Proporciona endpoints para:
- Redirigir tickets entre usuarios
- Obtener lista de miembros del equipo disponibles
- Gestionar la lógica de traspaso de responsabilidad
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User
from app.schemas import TeamMemberResponse, TicketRedirectionRequest, TicketRedirectionResponse
from app.services.ticket_redirection import TicketRedirectionService

router = APIRouter(prefix="/api/tickets", tags=["Ticket Redirection"])


@router.post("/{ticket_id}/redirect", response_model=TicketRedirectionResponse)
async def redirect_ticket(
    ticket_id: UUID,
    redirection_data: TicketRedirectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Redirige un ticket a otro usuario con justificación obligatoria.
    
    Este endpoint implementa la lógica completa de CS-020:
    - Valida que el usuario actual es el asignado
    - Requiere justificación obligatoria
    - Actualiza la asignación del ticket
    - Cambia el estado a TODO si estaba IN_PROGRESS
    - Crea eventos de trazabilidad
    - Envía notificaciones push en tiempo real
    
    Args:
        ticket_id: ID del ticket a redirigir
        redirection_data: Datos de la redirección (nuevo asignado y justificación)
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        TicketRedirectionResponse: Detalles de la redirección realizada
        
    Raises:
        HTTPException: Si hay errores de validación o permisos
    """
    try:
        service = TicketRedirectionService(db)
        
        # Validar que el usuario actual es el asignado
        result = await db.execute(
            select(User).where(User.id == redirection_data.to_user_id)
        )
        new_assignee = result.scalar_one_or_none()
        
        if not new_assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario destino no encontrado"
            )
        
        # Ejecutar la redirección
        redirected_ticket = await service.redirect_ticket(
            ticket_id=ticket_id,
            from_user_id=current_user.id,
            to_user_id=redirection_data.to_user_id,
            justification=redirection_data.justification
        )
        
        return TicketRedirectionResponse(
            ticket_id=redirected_ticket.id,
            from_user_id=current_user.id,
            to_user_id=redirection_data.to_user_id,
            justification=redirection_data.justification,
            new_status=redirected_ticket.status.value if hasattr(redirected_ticket.status, 'value') else str(redirected_ticket.status),
            redirected_at=redirected_ticket.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la redirección del ticket: {str(e)}"
        )


@router.get("/team-members", response_model=List[TeamMemberResponse])
async def get_team_members(
    epic_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene la lista de miembros del equipo disponibles para redirección.
    
    Args:
        epic_id: ID de la épica (opcional, para filtrar miembros relevantes)
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        List[TeamMemberResponse]: Lista de usuarios disponibles para redirección
    """
    try:
        service = TicketRedirectionService(db)
        team_members = await service.get_team_members(epic_id)
        
        return [
            TeamMemberResponse(
                id=member.id,
                full_name=member.full_name,
                email=member.email,
                role=member.role.name if member.role else "DEVELOPER"
            )
            for member in team_members
            if member.id != current_user.id  # Excluir al usuario actual
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo miembros del equipo: {str(e)}"
        )
