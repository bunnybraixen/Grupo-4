from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.meeting import AttendanceStatus, MeetingType


class MeetingAttendanceBase(BaseModel):
    user_id: UUID
    status: AttendanceStatus = Field(default=AttendanceStatus.PRESENT)
    notes: Optional[str] = Field(None, max_length=5_000)

class MeetingAttendanceCreate(MeetingAttendanceBase):
    pass

class MeetingAttendanceResponse(MeetingAttendanceBase):
    id: UUID
    meeting_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    meeting_type: MeetingType = Field(default=MeetingType.OTHER)
    scheduled_at: datetime
    summary_markdown: Optional[str] = Field(None, max_length=50_000)
    application_id: Optional[UUID] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    meeting_type: Optional[MeetingType] = None
    scheduled_at: Optional[datetime] = None
    summary_markdown: Optional[str] = Field(None, max_length=50_000)
    application_id: Optional[UUID] = None

class MeetingResponse(MeetingBase):
    id: UUID
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    attendances: List[MeetingAttendanceResponse] = []

    model_config = ConfigDict(from_attributes=True)
