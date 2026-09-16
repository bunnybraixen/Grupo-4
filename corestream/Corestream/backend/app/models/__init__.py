"""
Módulo de Modelos de CoreStream.

Este paquete contiene todas las definiciones de modelos SQLAlchemy para CoreStream,
una plataforma de gestión de proyectos con soporte para jerarquía de tareas,
seguimiento de tiempo, análisis y flujo de trabajo colaborativo.

Modelos disponibles:
    - User: Usuarios del sistema con roles (Admin, Group Leader, Developer)
    - Application: Nivel superior de organización de proyectos
    - Epic: Agrupa tickets relacionados dentro de una aplicación
    - Ticket: Unidades de trabajo individual con seguimiento de estado y tiempo
    - Subtask: Tareas más pequeñas dentro de un ticket
    - TicketEvent: Registro de auditoría y eventos para análisis
    - Notification: Notificaciones para mantener usuarios informados
    - Document: Archivos adjuntos a épicos o tickets

Jerarquía:
    Application
        └─ Epic
            └─ Ticket
                ├─ Subtask
                └─ TicketEvent (auditoría)

Características:
    - Máquina de estados de tickets (TODO → IN_PROGRESS → BLOCKED → REDIRECTED → DONE)
    - Niveles de prioridad (LOW, MEDIUM, HIGH, URGENT)
    - Seguimiento de tiempo (time_spent_seconds, blocked_time_seconds)
    - Sistema de roles y permisos basado en usuario
    - Análisis a través de eventos de auditoría
    - Soporte para drag-and-drop mediante order_index
    - Índices optimizados para consultas frecuentes
"""

# Importar la base declarativa
from .base import Base, BaseEntity

# Importar modelos en orden de dependencias
from .user import User, UserRole
from .application import Application
from .epic import Epic
from .ticket import Ticket, TicketStatus, TicketPriority
from .subtask import Subtask
from .ticket_event import TicketEvent, TicketEventType
from .notification import Notification, NotificationType
from .document import Document, DocumentType

# Exportar todas las clases públicas
__all__ = [
    # Base
    "Base",
    "BaseEntity",
    
    # User
    "User",
    "UserRole",
    
    # Application
    "Application",
    
    # Epic
    "Epic",
    
    # Ticket
    "Ticket",
    "TicketStatus",
    "TicketPriority",
    
    # Subtask
    "Subtask",
    
    # TicketEvent
    "TicketEvent",
    "TicketEventType",
    
    # Notification
    "Notification",
    "NotificationType",
    
    # Document
    "Document",
    "DocumentType",
]
