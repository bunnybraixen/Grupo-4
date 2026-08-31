# Archivo de configuración centralizado para la aplicación FastAPI
# Utiliza pydantic-settings para cargar variables desde .env y valores por defecto

import secrets
from functools import lru_cache
from typing import Optional

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
    DATABASE_URL: str = "postgresql+asyncpg://corestream:corestream@localhost:5432/corestream"
    
    # Configuración de Redis
    # URL para conectarse al servidor Redis para caché y sistema de notificaciones
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Configuración de Autenticación y Seguridad
    # Clave secreta para firmar y verificar tokens JWT
    # Se genera aleatoriamente si no se proporciona en .env para mayor seguridad
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # Algoritmo criptográfico utilizado para firmar tokens JWT
    # HS256 (HMAC SHA-256) es el estándar recomendado
    ALGORITHM: str = "HS256"
    
    # Tiempo de expiración del token de acceso en minutos (corta duración para seguridad)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Tiempo de expiración del token de refresco en días (más largo para facilitar re-autenticación)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Configuración de CORS
    # Lista de orígenes (dominios) permitidos para solicitudes CORS desde JavaScript
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    
    # Configuración de la Aplicación
    # Nombre de la aplicación utilizado en documentación OpenAPI y metadatos
    APP_NAME: str = "CoreStream API"
    
    # Modo debug - activa información detallada de errores y recarga automática
    # IMPORTANTE: Desactivar en producción por razones de seguridad
    DEBUG: bool = True
    
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
