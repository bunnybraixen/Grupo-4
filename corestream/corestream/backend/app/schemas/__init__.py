# Archivo de importación central para todos los esquemas de Pydantic
# Este módulo exporta todos los modelos de validación de datos utilizados en la API

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
    TokenPayload,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from app.schemas.epic import (
    EpicCreate,
    EpicUpdate,
    EpicReorder,
    EpicResponse,
)
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketMoveEpic,
    TicketComplete,
    TicketQuestion,
    TicketRedirect,
    TicketResponse,
)
from app.schemas.subtask import (
    SubtaskCreate,
    SubtaskUpdate,
    SubtaskResponse,
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationMarkRead,
)
from app.schemas.analytics import (
    UserPerformance,
    HeatmapEntry,
    BurndownPoint,
    BurndownData,
    AnalyticsSummary,
)

__all__ = [
    # Esquemas de Usuario
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    "TokenPayload",
    # Esquemas de Aplicación
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    # Esquemas de Épica
    "EpicCreate",
    "EpicUpdate",
    "EpicReorder",
    "EpicResponse",
    # Esquemas de Ticket
    "TicketCreate",
    "TicketUpdate",
    "TicketMoveEpic",
    "TicketComplete",
    "TicketQuestion",
    "TicketRedirect",
    "TicketResponse",
    # Esquemas de Subtarea
    "SubtaskCreate",
    "SubtaskUpdate",
    "SubtaskResponse",
    # Esquemas de Notificación
    "NotificationResponse",
    "NotificationMarkRead",
    # Esquemas de Analítica
    "UserPerformance",
    "HeatmapEntry",
    "BurndownPoint",
    "BurndownData",
    "AnalyticsSummary",
]
