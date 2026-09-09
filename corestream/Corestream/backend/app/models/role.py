from __future__ import annotations

from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseEntity
from .user import User


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEAM_LEADER = "TEAM_LEADER"
    DEVELOPER = "DEVELOPER"


class Role(Base, BaseEntity):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(lazy="raise_on_sql", back_populates="role")
 