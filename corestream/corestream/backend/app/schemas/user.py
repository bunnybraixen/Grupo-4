# Esquemas de validación para operaciones relacionadas con usuarios
# Incluye modelos para registro, login, autenticación y respuestas de usuario

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


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
    full_name: str
    specialty: Optional[str] = None


class UserCreate(UserBase):
    """
    Esquema para crear un nuevo usuario en el sistema.
    Extiende UserBase con validación de contraseña fuerte.
    
    Atributos:
        password: Contraseña que debe tener mínimo 8 caracteres
    """
    password: str

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
    full_name: Optional[str] = None
    specialty: Optional[str] = None
    avatar_url: Optional[str] = None


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
    Contiene los tokens JWT necesarios para acceder a recursos protegidos.
    
    Atributos:
        access_token: Token JWT para acceder a recursos protegidos (corta duración)
        refresh_token: Token para renovar el access_token sin requerer login
        token_type: Tipo de token (siempre "bearer" para JWT)
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """
    Esquema del contenido decodificado de un JWT.
    Contiene información extraída del token JWT para validación.
    
    Atributos:
        sub: Identificador del usuario (subject claim)
        role: Rol del usuario extraído del token
        exp: Timestamp Unix de expiración del token
    """
    sub: str
    role: str
    exp: int
