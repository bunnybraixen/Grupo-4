# Archivo de configuración centralizado para la aplicación FastAPI
# Utiliza pydantic-settings para cargar variables desde .env y valores por defecto

from functools import lru_cache
from typing import Union

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Clase de configuración que carga y valida variables de entorno.
    Proporciona valores por defecto seguros y permite sobrescribir desde .env.
    
    Atributos de base de datos:
        DATABASE_URL: URL de conexión a PostgreSQL con soporte async (asyncpg)
        
    Atributos de caché:
        REDIS_URL: URL de conexión al servidor Redis para caché y pubsub
        
    Atributos de autenticación:
        SECRET_KEY: Clave secreta para firmar tokens JWT (generada aleatoriamente si no se proporciona)
        ALGORITHM: Algoritmo criptográfico para tokens JWT (HS256)
        ACCESS_TOKEN_EXPIRE_MINUTES: Tiempo de expiración del token de acceso en minutos
        REFRESH_TOKEN_EXPIRE_DAYS: Tiempo de expiración del token de refresco en días
        
    Atributos de CORS:
        CORS_ORIGINS: Lista de orígenes permitidos para solicitudes CORS desde el frontend
        
    Atributos de la aplicación:
        APP_NAME: Nombre de la aplicación para documentación y metadatos
        DEBUG: Modo debug para desarrollo (desactivar en producción)
        
    Atributos de configuración de Pydantic:
        env_file: Ruta del archivo .env para cargar variables de entorno
    """
    
    # Configuración de Base de Datos
    # URL para conectarse a PostgreSQL con soporte para operaciones asincrónicas
    # Railway genera postgresql:// — el validator lo convierte a postgresql+asyncpg://
    DATABASE_URL: str = "postgresql+asyncpg://corestream:corestream@localhost:5432/corestream"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Opciones del pool de conexiones (solo aplican a PostgreSQL)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Recicla conexiones más viejas que este umbral (segundos). Evita que un
    # proxy o el propio PostgreSQL cierre por su cuenta una conexión que el
    # pool sigue considerando válida.
    DB_POOL_RECYCLE: int = 1800

    # Volcado de cada sentencia SQL al log.
    # Deliberadamente independiente de DEBUG: antes era echo=DEBUG, y eso hacía
    # que cualquier entorno con DEBUG=True escribiera todas las consultas al
    # log por duplicado, llenando el disco y filtrando datos de negocio.
    SQL_ECHO: bool = False

    # Configuración de Redis
    # URL para conectarse al servidor Redis para caché y sistema de notificaciones
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Configuración de Autenticación y Seguridad
    # Clave secreta para firmar y verificar tokens JWT
    # En producción debe ser sobreescrita desde el archivo .env
    SECRET_KEY: str = "insecure-default-key-change-in-prod"
    
    # Algoritmo criptográfico utilizado para firmar tokens JWT
    # HS256 (HMAC SHA-256) es el estándar recomendado
    ALGORITHM: str = "HS256"
    
    # Tiempo de expiración del token de acceso en minutos (corta duración para seguridad)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Tiempo de expiración del token de refresco en días (más largo para facilitar re-autenticación)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configuración de CORS
    # Acepta lista CSV, JSON array, o "*" para todos los orígenes.
    # En Railway: ALLOWED_ORIGINS=https://dominio-produccion.com,http://localhost:5173
    ALLOWED_ORIGINS: Union[list[str], str] = ["http://localhost:5173"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, list]) -> list[str]:
        if isinstance(v, list):
            return v
        # Soporta "*", CSV, o JSON array como string
        stripped = v.strip()
        if stripped.startswith("["):
            import json
            return json.loads(stripped)
        return [origin.strip() for origin in stripped.split(",") if origin.strip()]

    # Entorno de ejecución
    ENVIRONMENT: str = "development"

    # Configuración de la Aplicación
    # Nombre de la aplicación utilizado en documentación OpenAPI y metadatos
    APP_NAME: str = "CoreStream API"

    # Modo debug - activa información detallada de errores y recarga automática
    # IMPORTANTE: Desactivar en producción por razones de seguridad
    DEBUG: bool = True

    # Nivel de log para la aplicación
    LOG_LEVEL: str = "info"

    # Configuración de Azure Cognitive Services Translator
    # La empresa debe proveer estos valores al desplegar en producción
    AZURE_TRANSLATOR_KEY: str = ""
    AZURE_TRANSLATOR_REGION: str = "eastus"
    AZURE_TRANSLATOR_ENDPOINT: str = "https://api.cognitive.microsofttranslator.com"

    # Raíz de almacenamiento de archivos subidos por los usuarios. Tanto
    # routers/documents.py (subcarpeta "documents") como
    # services/file_service.py (subcarpeta "uploads") cuelgan de esta misma
    # raíz (plan fase 7.2) — en Docker debe ser un volumen persistente.
    UPLOAD_DIR: str = "/app/storage"
    
    # Configuración de Pydantic Settings
    class Config:
        """
        Configuración de Pydantic Settings para cargar variables de entorno.
        
        env_file: Especifica el archivo .env a cargar
        env_file_encoding: Codificación del archivo .env
        case_sensitive: Las variables de entorno son sensibles a mayúsculas
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """
        Aborta el arranque si ENVIRONMENT=production trae configuración
        insegura (plan 3.4). Deliberadamente un model_validator(mode="after"),
        no field_validators individuales: con field_validator, el orden de
        declaración de los campos en la clase determina qué hay disponible en
        info.data, y ENVIRONMENT está declarado DESPUÉS de SECRET_KEY — un
        field_validator sobre SECRET_KEY nunca vería el ENVIRONMENT real. Aquí,
        al validar después de poblar todo el modelo, ese problema no existe.

        Antes, backend/.env traía literalmente
        SECRET_KEY=tu-clave-secreta-muy-segura-cambiar-en-produccion y nada
        impedía arrancar así contra el dominio público: con una clave
        conocida, cualquiera puede forjar un JWT con rol ADMIN.
        """
        if self.ENVIRONMENT != "production":
            return self

        placeholders = {
            "tu-clave-secreta-muy-segura-cambiar-en-produccion",
            "insecure-default-key-change-in-prod",
            "cambiar-esta-clave-por-una-generada",
            "",
        }
        # `openssl rand -hex 32` (lo que .env.example pide) produce 64
        # caracteres. El umbral queda bien por debajo de eso a propósito
        # (para no rechazar otros generadores válidos de menos entropía),
        # pero por encima de cualquier placeholder legible tecleado a mano
        # — la lista explícita de arriba ya cubre los conocidos, esto es
        # la red de seguridad para el próximo placeholder que alguien añada
        # y se olvide de registrar aquí.
        if self.SECRET_KEY in placeholders or len(self.SECRET_KEY) < 40:
            raise ValueError(
                "SECRET_KEY inválida para producción: falta, es un placeholder, o "
                "es demasiado corta. Generar una con: openssl rand -hex 32"
            )

        if self.DEBUG:
            raise ValueError("DEBUG no puede ser True con ENVIRONMENT=production")

        if "*" in self.ALLOWED_ORIGINS:
            raise ValueError(
                "ALLOWED_ORIGINS no puede ser '*' en producción — combinado con "
                "allow_credentials=True (cookies) es una combinación que los "
                "navegadores rechazan de todas formas, y expone la API a "
                "cualquier origen si algún día se relaja allow_credentials."
            )

        return self


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la instancia singleton de configuración con caché.
    
    Esta función utiliza el decorador lru_cache para garantizar que solo se crea
    una instancia de Settings durante toda la vida de la aplicación, mejorando
    el rendimiento y evitando lecturas redundantes de variables de entorno.
    
    Returns:
        Settings: Instancia única de la clase Settings con configuración validada
        
    Ejemplo:
        settings = get_settings()
        db_url = settings.DATABASE_URL
        token_expiry = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    """
    return Settings()
