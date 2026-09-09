"""
Router de Invitaciones (plan 3.7).

Sustituye al registro público, que dejaba crear una cuenta activa a
cualquiera con solo un correo y una contraseña — inaceptable para un SaaS
interno bajo un dominio público. Un ADMIN genera un enlace de invitación con
un rol y un correo destino; el invitado lo usa una sola vez para crear su
cuenta con la contraseña que él elija.

No hay envío de correo: el enlace se copia desde la UI de administración y
se entrega por fuera de la aplicación (Slack, correo manual, lo que sea).
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.models import Invitation, Role, User, UserRole
from app.schemas import InvitationAccept, InvitationCreate, InvitationInfo, InvitationResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/invitations", tags=["Invitaciones"])

INVITATION_TTL_DAYS = 7


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.post(
    "/",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear invitación",
    description="Genera un enlace de invitación de un solo uso. Solo ADMIN.",
)
async def create_invitation(
    data: InvitationCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
) -> InvitationResponse:
    email = data.email.lower().strip()

    existing_user = await db.execute(select(User).where(User.email == email))
    if existing_user.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo",
        )

    # Una invitación pendiente y no caducada por correo, no varias acumulándose.
    pending = await db.execute(
        select(Invitation).where(
            Invitation.email == email,
            Invitation.used_at.is_(None),
        )
    )
    for inv in pending.scalars().all():
        if not inv.is_expired:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya hay una invitación pendiente para ese correo",
            )

    raw_token = secrets.token_urlsafe(32)
    invitation = Invitation(
        email=email,
        token_hash=_hash_token(raw_token),
        role=data.role,
        expires_at=datetime.now(timezone.utc) + timedelta(days=INVITATION_TTL_DAYS),
        created_by_id=current_user.id,
    )
    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        token=raw_token,
        expires_at=invitation.expires_at,
    )


@router.get(
    "/{token}",
    response_model=InvitationInfo,
    summary="Consultar una invitación",
    description="Sin autenticar: el invitado la usa para ver a qué se está uniendo antes de aceptar.",
)
async def get_invitation(token: str, db: AsyncSession = Depends(get_db)) -> InvitationInfo:
    invitation = await _get_invitation_or_404(token, db)
    return InvitationInfo(
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        is_expired=invitation.is_expired,
        is_used=invitation.is_used,
    )


@router.post(
    "/{token}/accept",
    status_code=status.HTTP_201_CREATED,
    summary="Aceptar una invitación",
    description="Sin autenticar: crea la cuenta del invitado con la contraseña que él elija.",
)
async def accept_invitation(
    token: str,
    data: InvitationAccept,
    db: AsyncSession = Depends(get_db),
) -> dict:
    invitation = await _get_invitation_or_404(token, db)

    if invitation.is_used:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta invitación ya fue usada")
    if invitation.is_expired:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Esta invitación ha caducado")

    existing_user = await db.execute(select(User).where(User.email == invitation.email))
    if existing_user.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo",
        )

    role_result = await db.execute(select(Role).where(Role.name == invitation.role))
    role = role_result.scalars().first()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"El rol '{invitation.role}' no existe en el sistema",
        )

    new_user = User(
        email=invitation.email,
        full_name=data.full_name.strip(),
        hashed_password=AuthService.hash_password(data.password),
        role_id=role.id,
        is_active=True,
    )
    db.add(new_user)

    invitation.used_at = datetime.now(timezone.utc)

    await db.commit()

    return {"message": "Cuenta creada correctamente. Ya puedes iniciar sesión."}


async def _get_invitation_or_404(token: str, db: AsyncSession) -> Invitation:
    result = await db.execute(select(Invitation).where(Invitation.token_hash == _hash_token(token)))
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitación no encontrada")
    return invitation
