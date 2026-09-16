"""
Servicio de autenticación y gestión de usuarios para CoreStream.

Este módulo proporciona funciones para autenticar usuarios, registrar nuevos usuarios,
y gestionar roles de usuarios dentro de la plataforma de gestión de proyectos CoreStream.
Utiliza SQLAlchemy AsyncSession para operaciones asincrónicas de base de datos y
proporciona manejo robusto de errores y validaciones.
"""

import base64

# Pre-hash con SHA-256
import hashlib
import logging
import re
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Importar utilidades de tokens del middleware
from app.middleware.auth import create_access_token as mw_create_access_token
from app.middleware.auth import create_refresh_token as mw_create_refresh_token
from app.middleware.auth import verify_token

# Importar modelos desde el paquete de modelos
from app.models import Role, User, UserRole
from app.schemas import TokenPayload

# Configuración del contexto de encriptación de contraseñas
# Se utiliza bcrypt como algoritmo de hashing para máxima seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("corestream.auth")


class AuthService:
    """
    Servicio de autenticación que encapsula toda la lógica relacionada con
    usuarios, autenticación y gestión de roles.
    
    Métodos principales:
    - authenticate_user: Valida credenciales de usuario
    - create_user: Registra un nuevo usuario en el sistema (antes register_user)
    - get_user_by_email: Busca usuario por dirección de correo
    - get_user_by_id: Busca usuario por identificador único
    - update_user_role: Actualiza el rol de un usuario
    """

    @staticmethod
    def _prepare_password(password: str) -> str:
        '''
        Pre-procesa la contraseña con SHA-256 antes de aplicar bcrypt.

        Args:
            password (str): Contraseña en texto plano a pre-procesar

        Returns:
            str: Contraseña codificada en base64 lista para ser hasheada con bcrypt

        Detalle técnico:
            - Aplica SHA-256 para obtener un digest de longitud fija (32 bytes)
            - Codifica el resultado en base64 para producir texto ASCII seguro (44 bytes)
            - Evita el límite de 72 bytes de bcrypt 4.x sin truncar la contraseña original
            - El resultado siempre tiene longitud fija independientemente del input
        '''
        digest = hashlib.sha256(password.encode()).digest()
        return base64.b64encode(digest).decode()

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña utilizando bcrypt.
        
        Args:
            password (str): Contraseña en texto plano a encriptar
              
        Returns:
            str: Contraseña hasheada y salteada de forma segura
            
        Detalle técnico:
            - Pre-procesa la contraseña con SHA-256 para evitar límite de 72 bytes de bcrypt
            - Utiliza bcrypt como algoritmo de hashing final para máxima seguridad
            - El salt se genera automáticamente en el hash
            - El hash es determinístico pero cada ejecución produce salt diferente
        """
        prepared = AuthService._prepare_password(password)
        return pwd_context.hash(prepared)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica que una contraseña en texto plano coincida con su hash.
    
        Args:
            plain_password (str): Contraseña en texto plano proporcionada por usuario
            hashed_password (str): Hash de la contraseña almacenado en la base de datos
        
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        
        Detalle técnico:
            - Aplica el mismo pre-procesamiento SHA-256 que hash_password antes de comparar
            - Usa la función verify de passlib que es resistente a timing attacks
            - Verifica el hash sin exponerse a ataques de fuerza bruta
        """
        prepared = AuthService._prepare_password(plain_password)
        return pwd_context.verify(prepared, hashed_password)

    @staticmethod
    def _validate_email(email: str) -> bool:
        """Valida que el correo electrónico tenga un formato válido."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _validate_password(password: str) -> tuple:
        """Valida que la contraseña cumpla con requisitos de seguridad mínimos."""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una mayúscula"
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una minúscula"
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un dígito"
        if not any(c in "!@#$%^&*()" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial"
        return True, ""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[dict]:
        """Autentica un usuario verificando sus credenciales contra la base de datos."""
        email = email.lower().strip()
        
        try:
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            user = result.scalars().first()
            
            if not user or not user.is_active:
                return None
            
            if not AuthService.verify_password(password, user.hashed_password):
                return None

            role_str = user.role.name if user.role else "DEVELOPER"

            return {
                'id': str(user.id),
                'email': user.email,
                'name': user.full_name,
                'role': role_str,
                'active': user.is_active
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error durante la autenticación"
            )

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data
    ) -> User:
        """Registra un nuevo usuario en el sistema."""
        try:
            email = user_data.email.lower().strip()
            password = user_data.password
            name = user_data.full_name.strip()
            
            if not AuthService._validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El formato del correo electrónico no es válido"
                )
            
            is_valid, error_msg = AuthService._validate_password(password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            stmt = select(User).where(User.email == email)
            result = await db.execute(stmt)
            existing_user = result.scalars().first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado"
                )
            
            getattr(user_data, 'specialty', 'Developer')

            # Prevenir Mass Assignment: Forzar siempre el rol a DEVELOPER en el registro público
            requested_role_name = 'DEVELOPER'
            role_stmt = select(Role).where(Role.name == requested_role_name)
            role_result = await db.execute(role_stmt)
            developer_role = role_result.scalars().first()

            if developer_role is None:
                # Bootstrap defensivo: si el rol solicitado no existe, cae a DEVELOPER
                role_stmt = select(Role).where(Role.name == UserRole.DEVELOPER.value)
                role_result = await db.execute(role_stmt)
                developer_role = role_result.scalars().first()

            if developer_role is None:
                developer_role = Role(
                    name=UserRole.DEVELOPER.value,
                    description="Rol base de desarrollo"
                )
                db.add(developer_role)
                await db.flush()

            new_user = User(
                email=email,
                hashed_password=AuthService.hash_password(password),
                full_name=name,
                specialty=user_data.specialty,
                role_id=developer_role.id,
                is_active=True
            )
            
            db.add(new_user)
            # El db.commit() y db.refresh() se delegan al router
            return new_user
            
        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            logger.exception("Error al registrar nuevo usuario")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al registrar nuevo usuario"
            )

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ) -> Optional[dict]:
        """Busca un usuario por su dirección de correo electrónico."""
        email = email.lower().strip()
        
        try:
            stmt = select(User).where(
                (User.email == email) & (User.is_active)
            )
            result = await db.execute(stmt)
            user = result.scalars().first()
            
            if not user:
                return None
            
            return {
                'id': str(user.id),
                'email': user.email,
                'name': user.full_name,
                'role': user.role.name if user.role else "DEVELOPER",
                'active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al buscar usuario por email"
            )

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: str
    ) -> Optional[dict]:
        """Busca un usuario por su identificador único (UUID)."""
        try:
            stmt = select(User).where(
                (User.id == UUID(user_id)) & (User.is_active)
            )
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                return None

            return {
                'id': str(user.id),
                'email': user.email,
                'name': user.full_name,
                'role': user.role.name if user.role else "DEVELOPER",
                'active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario inválido"
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al buscar usuario por ID"
            )

    @staticmethod
    async def update_user_role(
        db: AsyncSession,
        user_id: str,
        new_role: str
    ) -> dict:
        """Actualiza el rol de un usuario en el sistema."""
        valid_roles = ['DEVELOPER', 'TEAM_LEADER', 'ADMIN']

        try:
            if new_role not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol inválido. Roles válidos: {', '.join(valid_roles)}"
                )

            stmt = select(User).where(User.id == UUID(user_id))
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            role_stmt = select(Role).where(Role.name == new_role)
            role_result = await db.execute(role_stmt)
            role_obj = role_result.scalars().first()

            if not role_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol '{new_role}' no encontrado en BD"
                )

            user.role_id = role_obj.id
            await db.commit()
            await db.refresh(user)

            return {
                'id': str(user.id),
                'email': user.email,
                'name': user.full_name,
                'role': new_role,
                'active': user.is_active,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar rol del usuario"
            )
        
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """Verifica la clave antigua y actualiza por la nueva."""
        stmt = select(User).where(User.id == UUID(user_id))
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        # 1. Verificar clave antigua
        if not user or not AuthService.verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
            
        # 2. Validar la nueva clave (mayúsculas, números, etc.)
        is_valid, error_msg = AuthService._validate_password(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
            
        # 3. Hashear y guardar
        user.hashed_password = AuthService.hash_password(new_password)
        # Un cambio de contraseña exitoso cierra el ciclo abierto por un
        # reseteo de admin (plan 3.8): ya no hace falta forzar el cambio.
        user.must_change_password = False
        await db.commit()
        return True

    @staticmethod
    def create_access_token(user: User, role_name: str | None = None) -> str:
        """
        Crea un token de acceso JWT para la sesión del usuario.
        
        Args:
            user (User): Objeto del modelo User
            
        Returns:
            str: Token de acceso codificado
            
        Detalle técnico:
            - Inyecta el subject (sub) y el rol del usuario para autorización
        """
        token_role = role_name or UserRole.DEVELOPER.value
        return mw_create_access_token(
            data={"sub": str(user.id), "role": token_role}
        )

    @staticmethod
    def create_refresh_token(user: User, role_name: str | None = None) -> str:
        """
        Crea un token de refresco JWT para renovar sesiones.

        role_name opcional, igual que create_access_token: si el caller ya
        conoce el rol (p. ej. porque su query no cargó la relación
        User.role con selectinload), evita un lazy-load que con
        lazy="raise_on_sql" revienta con InvalidRequestError en vez de
        acceder a la relación en silencio.
        """
        role_str = role_name or (user.role.name if user.role else "DEVELOPER")

        return mw_create_refresh_token(
            data={"sub": str(user.id), "role": role_str}
        )

    @staticmethod
    async def verify_refresh_token(token: str) -> Optional[TokenPayload]:
        """
        Verifica la validez de un token de refresco y devuelve su payload
        completo (no solo el sub): el router necesita el jti para revocar el
        token consumido al rotarlo, y is_jti_revoked ya lo comprueba aquí.
        """
        try:
            return await verify_token(token, expected_type="refresh")
        except Exception:
            return None


# ---------------------------------------------------------------------
# Wrappers a nivel módulo para compatibilidad con imports existentes:
# from app.services import auth_service  -> auth_service.create_user(...)
# ---------------------------------------------------------------------
def hash_password(password: str) -> str:
    return AuthService.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return AuthService.verify_password(plain_password, hashed_password)


async def create_user(db: AsyncSession, user_data) -> User:
    return await AuthService.create_user(db, user_data)


def create_access_token(user: User, role_name: str | None = None) -> str:
    return AuthService.create_access_token(user, role_name)


def create_refresh_token(user: User) -> str:
    return AuthService.create_refresh_token(user)


async def verify_refresh_token(token: str) -> Optional[str]:
    return await AuthService.verify_refresh_token(token)

auth_service = AuthService()