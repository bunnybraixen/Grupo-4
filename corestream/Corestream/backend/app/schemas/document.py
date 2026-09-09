from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UploaderResponse(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    email: str

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_size: int
    mime_type: str
    doc_type: str
    epic_id: Optional[UUID] = None
    ticket_id: Optional[UUID] = None
    uploaded_by_id: Optional[UUID] = None
    uploaded_by: Optional[UploaderResponse] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TranslateRequest(BaseModel):
    target_language: str = Field(..., max_length=10)  # código ISO 639-1: "en", "es", "fr", "de", "pt", "it", "zh", "ar"


class TranslateResponse(BaseModel):
    document_id: UUID
    original_filename: str
    target_language: str
    translated_text: str
