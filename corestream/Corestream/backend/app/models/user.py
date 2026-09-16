"""
Modelo de Usuario para CoreStream.
Define la estructura y comportamiento de los usuarios del sistema,
incluyendo autenticación, roles, permisos y relaciones con otras entidades.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID as PyUUID
from sqlalchemy import String, Boolean, Integer, ForeignKey, Table, Column, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import Base, BaseEntity


class UserRole(str, Enum):
    """
    Enumeración de roles de usuario disponibles en CoreStream.
    
    Roles:
        ADMIN: Administrador del sistema con acceso total a todas las funcionalidades
        GROUP_LEADER: Líder de grupo con permisos de supervisión y gestión de equipo
        DEVELOPER: Desarrollador con permisos limitados a tareas asignadas
    """
    ADMIN = "ADMIN"
    GROUP_LEADER = "GROUP_LEADER"
    DEVELOPER = "DEVELOPER"


class User(Base, BaseEntity):
    """
    Entidad que representa un usuario del sistema CoreStream.
    
    Atributos principales:
        email: Correo electrónico único del usuario utilizado para autenticación
        hashed_password: Contraseña hasheada y salteada por razones de seguridad
        full_name: Nombre completo del usuario para visualización
        avatar_url: URL de la imagen de perfil del usuario
        role: Rol asignado al usuario que determina permisos y funcionalidades
        specialty: Campo especialidad que describe el área de expertise del usuario
        is_active: Indicador booleano si el usuario está activo en el sistema
    
    Relaciones:
        assigned_tickets: Tickets asignados al usuario
        created_tickets: Tickets creados por el usuario
        events: Eventos en los que participa o es mencionado
        notifications: Notificaciones dirigidas al usuario
    
    Índices:
        email: Índice único para búsquedas rápidas de autenticación
        role: Índice para consultas por rol de usuario
        is_active: Índice para filtrado de usuarios activos
    """
    
    __tablename__ = "users"
    
    # Campo de correo electrónico con restricción de unicidad
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Correo electrónico único del usuario utilizado como identificador de sesión"
    )
    
    # Contraseña hasheada con algoritmo seguro (bcrypt o similar)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Contraseña del usuario hasheada con algoritmo seguro (bcrypt/argon2)"
    )
    
    # Nombre completo del usuario para visualización en la interfaz
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Nombre completo del usuario que se muestra en la interfaz"
    )
    
    # URL del avatar del usuario
    avatar_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        doc="URL de la imagen de perfil/avatar del usuario"
    )
    
    # Rol del usuario que determina permisos y acceso
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role_enum"),
        default=UserRole.DEVELOPER,
        nullable=False,
        index=True,
        doc="Rol asignado al usuario: ADMIN, GROUP_LEADER o DEVELOPER"
    )
    
    # Especialidad o área de expertise del usuario
    specialty: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Especialidad o área de expertise técnica del usuario"
    )
    
    # Indicador de estado activo/inactivo del usuario
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Indicador si el usuario está activo en el sistema y puede iniciar sesión"
    )
    
    # Relaciones hacia otras entidades
    
    assigned_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.assignee_id",
        back_populates="assignee",
        doc="Lista de tickets asignados a este usuario"
    )
    
    created_tickets = relationship(
        "Ticket",
        foreign_keys="Ticket.created_by_id",
        back_populates="created_by",
        doc="Lista de tickets creados por este usuario"
    )
    
    owned_applications = relationship(
        "Application",
        back_populates="owner",
        doc="Lista de aplicaciones creadas/propietarias de este usuario"
    )
    
    events = relationship(
        "TicketEvent",
        back_populates="user",
        foreign_keys="TicketEvent.user_id",
        doc="Lista de eventos registrados para este usuario"
    )
    
    notifications = relationship(
        "Notification",
        back_populates="user",
        doc="Lista de notificaciones dirigidas a este usuario"
    )
    
    uploaded_documents = relationship(
        "Document",
        back_populates="uploaded_by",
        doc="Lista de documentos subidos por este usuario"
    )
    
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_role', 'role'),
        Index('ix_users_is_active', 'is_active'),
    )
