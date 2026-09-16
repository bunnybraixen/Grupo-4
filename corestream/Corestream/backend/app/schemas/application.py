# Esquemas de validación para operaciones relacionadas con aplicaciones
# Una aplicación es un contenedor que agrupa épicas y tickets relacionados

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class ApplicationCreate(BaseModel):
    """
    Esquema para crear una nueva aplicación en el sistema.
    Una aplicación sirve como contenedor principal para organizar épicas y tickets.
    
    Atributos:
        name: Nombre único de la aplicación (requerido)
        description: Descripción detallada de la aplicación (opcional)
        color: Código hexadecimal de color para la interfaz (opcional)
        icon: Identificador o URL del ícono de la aplicación (opcional)
    """
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """
        Valida que el nombre de la aplicación no esté vacío.
        
        Args:
            v: Nombre a validar
            
        Returns:
            El nombre validado
            
        Raises:
            ValueError: Si el nombre está vacío o solo contiene espacios
        """
        if not v or not v.strip():
            raise ValueError("El nombre de la aplicación no puede estar vacío")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que el color sea un código hexadecimal válido (ej: #FF5733).
        
        Args:
            v: Código de color a validar
            
        Returns:
            El color validado o None si no se proporcionó
            
        Raises:
            ValueError: Si el color no es un código hexadecimal válido
        """
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("El color debe ser un código hexadecimal válido (ej: #FF5733)")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("El color debe ser un código hexadecimal válido (ej: #FF5733)")
        return v


class ApplicationUpdate(BaseModel):
    """
    Esquema para actualizar datos de una aplicación existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Atributos:
        name: Nuevo nombre de la aplicación (opcional)
        description: Nueva descripción (opcional)
        color: Nuevo código de color (opcional)
        icon: Nuevo ícono (opcional)
    """
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que el nombre, si se proporciona, no esté vacío.
        
        Args:
            v: Nombre a validar
            
        Returns:
            El nombre validado o None
            
        Raises:
            ValueError: Si el nombre está vacío
        """
        if v is not None and not v.strip():
            raise ValueError("El nombre de la aplicación no puede estar vacío")
        return v.strip() if v else v

    @field_validator("color")
    @classmethod
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        """
        Valida que el color sea un código hexadecimal válido si se proporciona.
        
        Args:
            v: Código de color a validar
            
        Returns:
            El color validado o None
            
        Raises:
            ValueError: Si el color no es un código hexadecimal válido
        """
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("El color debe ser un código hexadecimal válido (ej: #FF5733)")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("El color debe ser un código hexadecimal válido (ej: #FF5733)")
        return v


class ApplicationResponse(BaseModel):
    """
    Esquema de respuesta al consultar datos de una aplicación.
    Incluye metadatos sobre la aplicación y estadísticas de épicas y tickets.
    
    Atributos:
        id: Identificador único en formato UUID
        name: Nombre de la aplicación
        description: Descripción de la aplicación
        color: Código de color para la interfaz
        icon: Ícono de la aplicación
        owner_id: UUID del usuario propietario de la aplicación
        is_active: Indica si la aplicación está activa
        created_at: Fecha y hora de creación
        epic_count: Total de épicas en la aplicación
        pending_count: Total de tickets pendientes en la aplicación
        delayed_count: Total de tickets retrasados en la aplicación
    """
    id: UUID
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    owner_id: UUID
    is_active: bool
    created_at: datetime
    epic_count: int
    pending_count: int
    delayed_count: int

    model_config = {"from_attributes": True}
