from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User

from .base import Base, BaseEntity


class IncidentSeverity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class IncidentStatus(str, Enum):
    REPORTED = "REPORTED"
    INVESTIGATING = "INVESTIGATING"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"

class AffectedEnvironment(str, Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    DEV = "DEV"

class Incident(Base, BaseEntity):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[IncidentStatus] = mapped_column(
        SQLEnum(IncidentStatus, name="incident_status_enum"),
        default=IncidentStatus.REPORTED,
        nullable=False,
        index=True,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        SQLEnum(IncidentSeverity, name="incident_severity_enum"),
        default=IncidentSeverity.P3,
        nullable=False,
        index=True,
    )
    affected_environment: Mapped[AffectedEnvironment] = mapped_column(
        SQLEnum(AffectedEnvironment, name="incident_environment_enum"),
        default=AffectedEnvironment.PRODUCTION,
        nullable=False,
        index=True,
    )
    
    estimated_resolution_time_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mitigation_state: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    application_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_to_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    application: Mapped["Application | None"] = relationship(lazy="raise_on_sql", foreign_keys=[application_id])
    created_by: Mapped["User | None"] = relationship(lazy="raise_on_sql", foreign_keys=[created_by_id])
    assigned_to: Mapped["User | None"] = relationship(lazy="raise_on_sql", foreign_keys=[assigned_to_id])
