from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import AffectedEnvironment, IncidentSeverity, IncidentStatus


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    severity: IncidentSeverity = Field(default=IncidentSeverity.P3)
    affected_environment: AffectedEnvironment = Field(default=AffectedEnvironment.PRODUCTION)
    estimated_resolution_time_seconds: int = Field(default=0, ge=0)
    mitigation_state: Optional[str] = Field(None, max_length=10_000)
    application_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10_000)
    severity: Optional[IncidentSeverity] = None
    affected_environment: Optional[AffectedEnvironment] = None
    estimated_resolution_time_seconds: Optional[int] = Field(None, ge=0)
    mitigation_state: Optional[str] = Field(None, max_length=10_000)
    application_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None

class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class IncidentResponse(IncidentBase):
    id: UUID
    status: IncidentStatus
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
