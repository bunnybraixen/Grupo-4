"""
Invitaciones de acceso — sustituyen al registro público (plan fase 3.7).

Un ADMIN genera una invitación con un rol y un correo destino; el token se
entrega por enlace (se copia y se envía por fuera de la aplicación, no hay
envío de correo). El invitado lo usa una sola vez para crear su propia cuenta
con la contraseña que él elija.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User

from .base import Base, BaseEntity


class Invitation(Base, BaseEntity):
    __tablename__ = "invitations"

    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Se guarda el hash del token, nunca el token en claro — el mismo
    # principio que una contraseña: si la base de datos se filtra, el token
    # no debe ser recuperable. A diferencia de una contraseña, el token tiene
    # alta entropía (aleatorio, 32 bytes) así que un hash rápido (sha256)
    # basta; no hace falta bcrypt.
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    # DEVELOPER, TEAM_LEADER o ADMIN — validado en el esquema, no aquí, por
    # el mismo motivo que Role.name tampoco es un enum de Postgres: mantiene
    # los roles como datos en vez de requerir una migración para añadir uno.
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_by: Mapped["User | None"] = relationship(
        lazy="raise_on_sql", foreign_keys=[created_by_id]
    )

    @property
    def is_expired(self) -> bool:
        from datetime import timezone

        return datetime.now(timezone.utc) > self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None
