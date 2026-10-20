from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, BaseEntity

# El enum de roles real es app.models.user.UserRole (columna users.role).


class Role(Base, BaseEntity):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Nota: `User.role` es una columna ENUM, no una FK a `roles`, así que aquí
    # NO puede existir una relationship inversa (rompe la configuración del
    # mapper: NoForeignKeysError). La tabla `roles` queda como datos de apoyo.
 