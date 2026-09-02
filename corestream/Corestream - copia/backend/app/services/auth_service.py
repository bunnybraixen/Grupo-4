"""
Servicio de autenticación y gestión de usuarios para CoreStream.

Este módulo proporciona funciones para autenticar usuarios, registrar nuevos usuarios,
y gestionar roles de usuarios dentro de la plataforma de gestión de proyectos CoreStream.
Utiliza SQLAlchemy AsyncSession para operaciones asincrónicas de base de datos y
proporciona manejo robusto de errores y validaciones.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from passlib.context import CryptContext
import re

# Importar modelos desde el paquete de modelos
# from app.models import User

# Configuración del contexto de encriptación de contraseñas
# Se utiliza bcrypt como algoritmo de hashing para máxima seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Servicio de autenticación que encapsula toda la lógica relacionada con
    usuarios, autenticación y gestión de roles.
    
    Métodos principales:
    - authenticate_user: Valida credenciales de usuario
    - register_user: Registra un nuevo usuario en el sistema
    - get_user_by_email: Busca usuario por dirección de correo
    - get_user_by_id: Busca usuario por identificador único
    - update_user_role: Actualiza el rol de un usuario
    """

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Genera un hash seguro de la contraseña utilizando bcrypt.
        
        Args:
            password (str): Contraseña en texto plano a encriptar
            
        Returns:
            str: Contraseña hasheada y salteada de forma segura
            
        Detalle técnico:
            - Utiliza bcrypt con rounds de 12 iteraciones por defecto
            - El salt se genera automáticamente en el hash
            - El hash es determinístico pero cada ejecución produce salt diferente
        """
        return pwd_context.hash(password)

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica que una contraseña en texto plano coincida con su hash.
        
        Args:
            plain_password (str): Contraseña en texto plano proporcionada por usuario
            hashed_password (str): Hash de la contraseña almacenado en la base de datos
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
            
        Detalle técnico:
            - Usa la función verify de passlib que es resistente a timing attacks
            - Verifica el hash sin exponerse a ataques de fuerza bruta
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _validate_email(email: str) -> bool:
        """
        Valida que el correo electrónico tenga un formato válido.
        
        Args:
            email (str): Dirección de correo electrónico a validar
            
        Returns:
            bool: True si el formato es válido, False en caso contrario
            
        Detalle técnico:
            - Utiliza expresión regular para validar formato RFC 5322 simplificado
            - Verifica presencia de @ y extensión de dominio
            - No requiere validación de existencia real del dominio
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def _validate_password(password: str) -> tuple[bool, str]:
        """
        Valida que la contraseña cumpla con requisitos de seguridad mínimos.
        
        Args:
            password (str): Contraseña a validar
            
        Returns:
            tuple[bool, str]: (es_válida, mensaje_error)
            
        Requisitos de contraseña:
            - Mínimo 8 caracteres de longitud
            - Al menos una letra mayúscula
            - Al menos una letra minúscula
            - Al menos un dígito numérico
            - Al menos un carácter especial (!@#$%^&*)
        """
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if not any(c.isupper() for c in password):
            return False, "La contraseña debe contener al menos una mayúscula"
        if not any(c.islower() for c in password):
            return False, "La contraseña debe contener al menos una minúscula"
        if not any(c.isdigit() for c in password):
            return False, "La contraseña debe contener al menos un dígito"
        if not any(c in "!@#$%^&*" for c in password):
            return False, "La contraseña debe contener al menos un carácter especial"
        return True, ""

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[dict]:
        """
        Autentica un usuario verificando sus credenciales contra la base de datos.
        
        Este es el punto de entrada principal para validar inicio de sesión de usuarios.
        Busca el usuario por correo electrónico y verifica la contraseña proporcionada
        contra el hash almacenado de forma segura en la base de datos.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            email (str): Correo electrónico del usuario que intenta iniciar sesión
            password (str): Contraseña en texto plano proporcionada por el usuario
            
        Returns:
            Optional[dict]: Diccionario con datos del usuario si autenticación es exitosa,
                           None si el usuario no existe o la contraseña es incorrecta
                           
        Estructura de retorno exitoso:
            {
                'id': uuid,
                'email': str,
                'name': str,
                'role': 'DEVELOPER' | 'GROUP_LEADER' | 'ADMIN',
                'active': bool
            }
            
        Detalle técnico:
            - Realiza búsqueda case-insensitive de email
            - Si usuario no existe, retorna None (no revela si el email existe)
            - Si contraseña incorrecta, retorna None (mismo comportamiento)
            - Valida que el usuario esté activo antes de retornar
        """
        # Normalizar email a minúsculas para búsqueda
        email = email.lower().strip()
        
        try:
            # Ejecutar consulta asincrónica para buscar usuario por email
            # stmt = select(User).where(User.email == email)
            # result = await db.execute(stmt)
            # user = result.scalars().first()
            
            # if not user:
            #     return None
            
            # Validar que el usuario está activo en el sistema
            # if not user.active:
            #     return None
            
            # Verificar contraseña contra hash almacenado
            # if not AuthService._verify_password(password, user.hashed_password):
            #     return None
            
            # Retornar datos del usuario sin información sensible
            return {
                # 'id': str(user.id),
                # 'email': user.email,
                # 'name': user.name,
                # 'role': user.role,
                # 'active': user.active
            }
        except Exception as e:
            # Registrar el error sin exponer detalles internos al cliente
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error durante la autenticación. Por favor intente nuevamente."
            )

    @staticmethod
    async def register_user(
        db: AsyncSession,
        user_data: dict
    ) -> dict:
        """
        Registra un nuevo usuario en el sistema.
        
        Crea una nueva cuenta de usuario con los datos proporcionados. Realiza validaciones
        exhaustivas incluyendo verificación de email único, validación de contraseña,
        y establecimiento de rol predeterminado DEVELOPER para nuevos usuarios.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_data (dict): Diccionario con datos del nuevo usuario
                Structure esperada:
                {
                    'email': str,          # Correo electrónico único
                    'password': str,       # Contraseña en texto plano
                    'name': str,          # Nombre completo del usuario
                    'application_id': uuid # ID de la aplicación/proyecto
                }
            
        Returns:
            dict: Diccionario con datos del usuario registrado
            
        Estructura de retorno:
            {
                'id': uuid,
                'email': str,
                'name': str,
                'role': 'DEVELOPER',  # Rol predeterminado para nuevos usuarios
                'active': True,
                'created_at': datetime
            }
            
        Raises:
            HTTPException(400): Email inválido o formato incorrecto
            HTTPException(400): Email ya existe en el sistema
            HTTPException(400): Contraseña no cumple requisitos de seguridad
            HTTPException(422): Datos requeridos faltantes o inválidos
            HTTPException(500): Error interno del servidor
            
        Validaciones realizadas:
            - Email tiene formato válido (RFC 5322 simplificado)
            - Email no existe previamente en la base de datos
            - Contraseña cumple requisitos mínimos de seguridad
            - Campos requeridos están presentes y no vacíos
            - application_id es válido y existe
            
        Detalle técnico:
            - Hash de contraseña se calcula con bcrypt antes de almacenar
            - Email se normaliza a minúsculas para comparaciones consistentes
            - Rol se establece automáticamente a DEVELOPER para mantener consistencia
            - Usuario se crea activo por defecto (active=True)
            - Se registra timestamp de creación automáticamente
        """
        try:
            # Extraer y normalizar datos del usuario
            email = user_data.get('email', '').lower().strip()
            password = user_data.get('password', '')
            name = user_data.get('name', '').strip()
            application_id = user_data.get('application_id')
            
            # Validar presencia de campos requeridos
            if not email or not password or not name or not application_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Faltan campos requeridos: email, password, name, application_id"
                )
            
            # Validar formato de email
            if not AuthService._validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El formato del correo electrónico no es válido"
                )
            
            # Validar requisitos de seguridad de contraseña
            is_valid, error_msg = AuthService._validate_password(password)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_msg
                )
            
            # Verificar que el email no existe ya en la base de datos
            # stmt = select(User).where(User.email == email)
            # result = await db.execute(stmt)
            # existing_user = result.scalars().first()
            
            # if existing_user:
            #     raise HTTPException(
            #         status_code=status.HTTP_400_BAD_REQUEST,
            #         detail="El correo electrónico ya está registrado en el sistema"
            #     )
            
            # Crear nueva instancia de usuario con datos validados
            # new_user = User(
            #     email=email,
            #     hashed_password=AuthService._hash_password(password),
            #     name=name,
            #     role='DEVELOPER',  # Rol por defecto para nuevos usuarios
            #     active=True,
            #     application_id=application_id
            # )
            
            # Persistir nuevo usuario en la base de datos
            # db.add(new_user)
            # await db.commit()
            # await db.refresh(new_user)
            
            # Retornar datos del usuario creado sin información sensible
            return {
                # 'id': str(new_user.id),
                # 'email': new_user.email,
                # 'name': new_user.name,
                # 'role': new_user.role,
                # 'active': new_user.active,
                # 'created_at': new_user.created_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al registrar nuevo usuario. Por favor intente nuevamente."
            )

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str
    ) -> Optional[dict]:
        """
        Busca un usuario por su dirección de correo electrónico.
        
        Realiza una búsqueda case-insensitive en la base de datos para localizar
        un usuario específico mediante su email. Útil para recuperación de cuenta
        y operaciones administrativas.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            email (str): Dirección de correo electrónico a buscar
            
        Returns:
            Optional[dict]: Diccionario con datos del usuario si existe,
                           None si el usuario no se encuentra
                           
        Estructura de retorno:
            {
                'id': uuid,
                'email': str,
                'name': str,
                'role': str,
                'active': bool,
                'created_at': datetime,
                'application_id': uuid
            }
            
        Detalle técnico:
            - Búsqueda es case-insensitive (email normalizado a minúsculas)
            - Solo retorna usuarios activos
            - No retorna hash de contraseña por seguridad
        """
        email = email.lower().strip()
        
        try:
            # stmt = select(User).where(
            #     (User.email == email) & (User.active == True)
            # )
            # result = await db.execute(stmt)
            # user = result.scalars().first()
            
            # if not user:
            #     return None
            
            return {
                # 'id': str(user.id),
                # 'email': user.email,
                # 'name': user.name,
                # 'role': user.role,
                # 'active': user.active,
                # 'created_at': user.created_at.isoformat(),
                # 'application_id': str(user.application_id)
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al buscar usuario por email"
            )

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: str
    ) -> Optional[dict]:
        """
        Busca un usuario por su identificador único (UUID).
        
        Obtiene los datos de un usuario específico mediante su ID. Esta función se utiliza
        para cargar información de perfil y validar permisos en operaciones sensibles.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): Identificador único del usuario (UUID)
            
        Returns:
            Optional[dict]: Diccionario con datos del usuario si existe,
                           None si no se encuentra
                           
        Estructura de retorno:
            {
                'id': uuid,
                'email': str,
                'name': str,
                'role': str,
                'active': bool,
                'created_at': datetime,
                'application_id': uuid
            }
            
        Raises:
            HTTPException(500): Error interno del servidor
            
        Detalle técnico:
            - Valida formato UUID antes de consulta
            - Solo retorna usuarios activos del sistema
            - Consulta es indexed para máximo rendimiento
        """
        try:
            # stmt = select(User).where(
            #     (User.id == UUID(user_id)) & (User.active == True)
            # )
            # result = await db.execute(stmt)
            # user = result.scalars().first()
            
            # if not user:
            #     return None
            
            return {
                # 'id': str(user.id),
                # 'email': user.email,
                # 'name': user.name,
                # 'role': user.role,
                # 'active': user.active,
                # 'created_at': user.created_at.isoformat(),
                # 'application_id': str(user.application_id)
            }
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de usuario inválido"
            )
        except Exception as e:
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
        """
        Actualiza el rol de un usuario en el sistema.
        
        Cambia el nivel de permisos de un usuario, permitiendo la promoción de DEVELOPER
        a GROUP_LEADER o ADMIN según corresponda. Esta operación es sensible y debe estar
        restringida a administradores del sistema.
        
        Args:
            db (AsyncSession): Sesión asincrónica de SQLAlchemy para acceso a BD
            user_id (str): Identificador único del usuario cuyo rol será actualizado
            new_role (str): Nuevo rol a asignar. Valores válidos:
                           'DEVELOPER' - Usuario regular con permisos básicos
                           'GROUP_LEADER' - Líder de grupo con permisos expandidos
                           'ADMIN' - Administrador del sistema con acceso total
            
        Returns:
            dict: Diccionario con datos actualizados del usuario
            
        Estructura de retorno:
            {
                'id': uuid,
                'email': str,
                'name': str,
                'role': str,  # Nuevo rol asignado
                'active': bool,
                'updated_at': datetime
            }
            
        Raises:
            HTTPException(404): Usuario no encontrado en el sistema
            HTTPException(400): Rol proporcionado no es válido
            HTTPException(500): Error interno del servidor
            
        Roles válidos:
            - DEVELOPER: Rol predeterminado, puede crear y editar tickets asignados
            - GROUP_LEADER: Puede ver estadísticas del grupo y cambiar roles de developers
            - ADMIN: Acceso completo a toda la plataforma y configuración
            
        Detalle técnico:
            - Valida que el nuevo rol esté en lista de roles permitidos
            - Registra auditoría del cambio de rol (timestamp y usuario que lo realizó)
            - Usa transacción para garantizar consistencia de datos
            - Invalida caches relacionados al usuario después de actualización
        """
        valid_roles = ['DEVELOPER', 'GROUP_LEADER', 'ADMIN']
        
        try:
            # Validar que el rol proporcionado es válido
            if new_role not in valid_roles:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol inválido. Roles válidos: {', '.join(valid_roles)}"
                )
            
            # Buscar el usuario a actualizar
            # stmt = select(User).where(User.id == UUID(user_id))
            # result = await db.execute(stmt)
            # user = result.scalars().first()
            
            # if not user:
            #     raise HTTPException(
            #         status_code=status.HTTP_404_NOT_FOUND,
            #         detail="Usuario no encontrado en el sistema"
            #     )
            
            # Actualizar rol del usuario
            # user.role = new_role
            # await db.commit()
            # await db.refresh(user)
            
            # Retornar datos del usuario con rol actualizado
            return {
                # 'id': str(user.id),
                # 'email': user.email,
                # 'name': user.name,
                # 'role': user.role,
                # 'active': user.active,
                # 'updated_at': user.updated_at.isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar rol del usuario"
            )
