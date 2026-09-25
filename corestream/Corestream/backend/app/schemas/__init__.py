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

# Alias usado por app/routers/auth.py (mismo esquema que UserCreate)
UserRegister = UserCreate
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
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationMarkRead,
)
from app.schemas.document import (
    DocumentResponse,
)
from app.schemas.ticket_redirection import (
    TicketEventResponse,
    TicketRedirectionRequest,
    TicketRedirectionResponse,
    TeamMemberResponse,
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
    "UserRegister",
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
    # Esquemas de Equipo
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    # Esquemas de Notificación
    "NotificationResponse",
    "NotificationMarkRead",
    # Esquemas de Documentos
    "DocumentResponse",
    # Esquemas de Redirección / Eventos de Ticket
    "TicketEventResponse",
    "TicketRedirectionRequest",
    "TicketRedirectionResponse",
    "TeamMemberResponse",
    # Esquemas de Analítica
    "UserPerformance",
    "HeatmapEntry",
    "BurndownPoint",
    "BurndownData",
    "AnalyticsSummary",
]
