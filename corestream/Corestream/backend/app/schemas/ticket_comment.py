from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.schemas.user import UserResponse


class TicketCommentCreate(BaseModel):

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Contenido del comentario",
    )

    @field_validator("content")
    @classmethod
    def validate_comment_content(cls, v: str) -> str:

        if not v or v.isspace():
            raise ValueError("El comentario no puede estar vacío")

        return v.strip()


class TicketCommentUpdate(BaseModel):

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Nuevo contenido del comentario",
    )

    @field_validator("content")
    @classmethod
    def validate_comment_content(cls, v: str) -> str:

        if not v or v.isspace():
            raise ValueError("El comentario no puede estar vacío")

        return v.strip()

class TicketCommentResponse(BaseModel):


    id: UUID
    ticket_id: UUID
    user: UserResponse
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }