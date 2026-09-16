# Esquemas de validación para operaciones relacionadas con usuarios
# Incluye modelos para registro, login, autenticación y respuestas de usuario

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """
    Esquema base con información común de usuario.
    Contiene los campos esenciales compartidos entre múltiples esquemas.
    
    Atributos:
        email: Dirección de correo electrónico única del usuario
        full_name: Nombre completo del usuario
        specialty: Especialidad técnica o área de expertise (opcional)
    """
    email: EmailStr
    full_name: str = Field(..., max_length=255)
    specialty: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """
    Esquema para crear un nuevo usuario en el sistema.
    Extiende UserBase con validación de contraseña fuerte.

    Atributos:
        password: Contraseña que debe tener mínimo 8 caracteres
        role: Rol inicial del usuario (DEVELOPER o TEAM_LEADER); por defecto DEVELOPER
    """
    password: str = Field(..., max_length=128)
    role: Optional[str] = "DEVELOPER"

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """
        Valida que la contraseña tenga una longitud mínima de 8 caracteres.
        
        Args:
            v: Contraseña a validar
            
        Returns:
            La contraseña validada
            
        Raises:
            ValueError: Si la contraseña tiene menos de 8 caracteres
        """
        if len(v) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        return v


class UserUpdate(BaseModel):
    """
    Esquema para actualizar datos de un usuario existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Atributos:
        full_name: Nuevo nombre completo (opcional)
        specialty: Nueva especialidad (opcional)
        avatar_url: URL de la imagen de perfil (opcional)
    """
    full_name: Optional[str] = Field(None, max_length=255)
    specialty: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=2_000)
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """
    Esquema de respuesta al consultar datos de un usuario.
    Incluye información de administración y fechas de auditoría.
    
    Atributos:
        id: Identificador único en formato UUID
        role: Rol del usuario en el sistema (admin, manager, user, etc.)
        avatar_url: URL de la imagen de perfil del usuario
        is_active: Indica si el usuario está activo en el sistema
        created_at: Fecha y hora de creación del usuario
    """
    id: UUID
    role: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    preferences: Optional[dict] = None
    must_change_password: bool = False

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v: Any) -> str:
        """Extrae el nombre del rol si viene como un objeto de SQLAlchemy"""
        if hasattr(v, "name"):
            return v.name
        return str(v)

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """
    Esquema para validar credenciales durante el login.
    Utilizado en el endpoint de autenticación.
    
    Atributos:
        email: Correo electrónico del usuario
        password: Contraseña del usuario
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Esquema de respuesta después de una autenticación exitosa.

    El refresh_token YA NO viaja en este cuerpo (plan 3.2): el backend lo
    entrega como cookie HttpOnly en Set-Cookie, así que nunca es legible desde
    JavaScript. El access_token sí viaja aquí porque el frontend lo mantiene
    en memoria (no en localStorage) para usarlo como Bearer en cada petición.

    Atributos:
        access_token: Token JWT para acceder a recursos protegidos (corta duración)
        token_type: Tipo de token (siempre "bearer" para JWT)
        expires_in: Segundos de vida del access_token
        must_change_password: Si es True, el frontend debe forzar el cambio
            de contraseña antes de dejar navegar (plan 3.8)
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    must_change_password: bool = False


class TokenPayload(BaseModel):
    """
    Esquema del contenido decodificado de un JWT.

    Atributos:
        sub: Identificador del usuario (subject claim)
        role: Rol del usuario extraído del token
        exp: Timestamp Unix de expiración del token
        type: "access" o "refresh" — evita que un token sirva para el
            propósito del otro (plan 3.1: antes ambos compartían payload y
            clave, así que un refresh token de 7 días colaba como Bearer)
        jti: identificador único del token, usado para poder revocarlo
            individualmente en logout (plan 3.3)
    """
    sub: str
    role: str
    exp: int
    type: str
    jti: str


class RefreshRequest(BaseModel):
    """
    Ya no se usa para /auth/refresh (el refresh token viaja por cookie, no
    por cuerpo). Se mantiene por si algún cliente no-navegador (CLI, tests)
    necesita pasar el token explícitamente; el router acepta ambas formas.
    """
    refresh_token: Optional[str] = None


class LogoutRequest(BaseModel):
    """Cuerpo opcional de /auth/logout, para revocar un refresh_token explícito."""
    refresh_token: Optional[str] = None

class PasswordChange(BaseModel):
    """
    Esquema para validar la petición de cambio de contraseña.
    """
    old_password: str = Field(..., max_length=128)
    new_password: str = Field(..., max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La nueva contraseña debe tener mínimo 8 caracteres")
        return v


class AdminPasswordResetResponse(BaseModel):
    """
    Respuesta al resetear la contraseña de otro usuario (plan 3.8).

    La contraseña temporal se devuelve UNA sola vez, en esta respuesta; no se
    puede volver a consultar. El usuario deberá cambiarla en su próximo login
    (must_change_password queda en True).
    """
    user_id: UUID
    temporary_password: str


# ---------------------------------------------------------------------------
# Invitaciones (plan 3.7) — sustituyen al registro público
# ---------------------------------------------------------------------------

class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "DEVELOPER"

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"ADMIN", "TEAM_LEADER", "DEVELOPER"}
        if v not in valid:
            raise ValueError(f"Rol inválido. Roles válidos: {', '.join(sorted(valid))}")
        return v


class InvitationResponse(BaseModel):
    """
    Se devuelve una sola vez, justo al crear la invitación: es el único
    momento en que el token en claro existe fuera de la base de datos (donde
    solo se guarda su hash). El admin copia el enlace y lo entrega por fuera
    de la aplicación.
    """
    id: UUID
    email: str
    role: str
    token: str
    expires_at: datetime


class InvitationInfo(BaseModel):
    """Lo que ve el invitado antes de aceptar: sin datos sensibles."""
    email: str
    role: str
    expires_at: datetime
    is_expired: bool
    is_used: bool


class InvitationAccept(BaseModel):
    full_name: str = Field(..., max_length=255)
    password: str = Field(..., max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres")
        return v