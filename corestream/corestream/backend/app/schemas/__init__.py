# Archivo de importación central para todos los esquemas de Pydantic
# Este módulo exporta todos los modelos de validación de datos utilizados en la API

from app.schemas.analytics import (
    AnalyticsSummary,
    BurndownData,
    BurndownPoint,
    HeatmapEntry,
    UserPerformance,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.schemas.document import (
    DocumentResponse,
)
from app.schemas.epic import (
    EpicCreate,
    EpicReorder,
    EpicResponse,
    EpicUpdate,
)
from app.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
    IncidentStatusUpdate,
    IncidentUpdate,
)
from app.schemas.meeting import (
    MeetingAttendanceCreate,
    MeetingAttendanceResponse,
    MeetingCreate,
    MeetingResponse,
    MeetingUpdate,
)
from app.schemas.notification import (
    NotificationMarkRead,
    NotificationResponse,
)
from app.schemas.subtask import (
    SubtaskCreate,
    SubtaskResponse,
    SubtaskUpdate,
)
from app.schemas.ticket import (
    TicketComplete,
    TicketCreate,
    TicketMoveEpic,
    TicketQuestion,
    TicketRedirect,
    TicketResponse,
    TicketUpdate,
)
from app.schemas.ticket_redirection import (
    TeamMemberResponse,
    TicketAssignedNotification,
    TicketEventResponse,
    TicketRedirectionRequest,
    TicketRedirectionResponse,
    TicketStatusChangedNotification,
    TimerSyncNotification,
    WebSocketNotification,
)
from app.schemas.user import (
    AdminPasswordResetResponse,
    InvitationAccept,
    InvitationCreate,
    InvitationInfo,
    InvitationResponse,
    LogoutRequest,
    RefreshRequest,
    TokenPayload,
    TokenResponse,
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
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
    "RefreshRequest",
    "LogoutRequest",
    "AdminPasswordResetResponse",
    "InvitationCreate",
    "InvitationResponse",
    "InvitationInfo",
    "InvitationAccept",
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
    # Esquemas de Documentos
    "DocumentResponse",
    # Esquemas de Redirección de Tickets
    "TicketRedirectionRequest",
    "TicketRedirectionResponse",
    "TeamMemberResponse",
    "TicketEventResponse",
    "WebSocketNotification",
    "TicketAssignedNotification",
    "TicketStatusChangedNotification",
    "TimerSyncNotification",
    # Esquemas de Incidentes
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentStatusUpdate",
    "IncidentResponse",
    # Esquemas de Reuniones
    "MeetingAttendanceCreate",
    "MeetingAttendanceResponse",
    "MeetingCreate",
    "MeetingUpdate",
    "MeetingResponse",
]
