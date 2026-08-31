# Estructura del Proyecto Backend - CoreStream

Este documento describe la estructura completa del backend y cómo está organizado.

## Árbol de Directorios

```
backend/
├── app/                                    # Paquete principal de la aplicación
│   ├── __init__.py                         # Metadatos del paquete
│   ├── main.py                             # Aplicación FastAPI principal
│   ├── config.py                           # Configuración y variables de entorno
│   ├── database.py                         # Configuración SQLAlchemy async
│   ├── redis_client.py                     # Cliente Redis asincrónico
│   │
│   ├── schemas/                            # Esquemas de validación Pydantic v2
│   │   ├── __init__.py                     # Exporta todos los esquemas
│   │   ├── user.py                         # Esquemas: UserBase, UserCreate, UserLogin, etc.
│   │   ├── application.py                  # Esquemas: ApplicationCreate, ApplicationResponse, etc.
│   │   ├── epic.py                         # Esquemas: EpicCreate, EpicResponse, etc.
│   │   ├── ticket.py                       # Esquemas: TicketCreate, TicketComplete, etc.
│   │   ├── subtask.py                      # Esquemas: SubtaskCreate, SubtaskResponse, etc.
│   │   ├── notification.py                 # Esquemas: NotificationResponse, etc.
│   │   └── analytics.py                    # Esquemas: UserPerformance, BurndownData, etc.
│   │
│   ├── middleware/                         # Autenticación, autorización y seguridad
│   │   ├── __init__.py                     # Exporta funciones de autenticación
│   │   └── auth.py                         # JWT, hash passwords, roles, verificación
│   │
│   ├── models/                             # Modelos ORM SQLAlchemy (A CREAR)
│   │   ├── __init__.py
│   │   ├── base.py                         # Clase base para todos los modelos
│   │   ├── user.py                         # Modelo User
│   │   ├── application.py                  # Modelo Application
│   │   ├── epic.py                         # Modelo Epic
│   │   ├── ticket.py                       # Modelo Ticket
│   │   ├── subtask.py                      # Modelo Subtask
│   │   └── notification.py                 # Modelo Notification
│   │
│   ├── routers/                            # Controladores de endpoints (A CREAR)
│   │   ├── __init__.py                     # Exporta todos los routers
│   │   ├── auth.py                         # Endpoints: login, register, refresh
│   │   ├── users.py                        # Endpoints: CRUD usuarios, performance
│   │   ├── applications.py                 # Endpoints: CRUD aplicaciones
│   │   ├── epics.py                        # Endpoints: CRUD épicas, reorder
│   │   ├── tickets.py                      # Endpoints: CRUD tickets, acciones
│   │   ├── subtasks.py                     # Endpoints: CRUD subtareas
│   │   ├── analytics.py                    # Endpoints: métricas, burndown, heatmap
│   │   ├── documents.py                    # Endpoints: gestión de documentos
│   │   └── notifications.py                # Endpoints: consultar notificaciones
│   │
│   ├── services/                           # Lógica de negocio (A CREAR)
│   │   ├── __init__.py
│   │   ├── user_service.py                 # Servicios de usuario
│   │   ├── application_service.py          # Servicios de aplicación
│   │   ├── epic_service.py                 # Servicios de épica
│   │   ├── ticket_service.py               # Servicios de ticket
│   │   ├── analytics_service.py            # Cálculos de analítica
│   │   └── notification_service.py         # Gestión de notificaciones
│   │
│   ├── utils/                              # Utilidades y helpers (A CREAR)
│   │   ├── __init__.py
│   │   ├── validators.py                   # Validadores personalizados
│   │   ├── helpers.py                      # Funciones auxiliares
│   │   ├── converters.py                   # Conversión entre modelos y esquemas
│   │   └── constants.py                    # Constantes de la aplicación
│   │
│   └── exceptions/                         # Excepciones personalizadas (A CREAR)
│       ├── __init__.py
│       ├── base.py                         # Clase base de excepciones
│       ├── user_exceptions.py              # Excepciones de usuario
│       └── ticket_exceptions.py            # Excepciones de ticket
│
├── migrations/                             # Migraciones de Alembic (A CREAR)
│   ├── versions/                           # Scripts de migración
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
│
├── tests/                                  # Suite de tests (A CREAR)
│   ├── __init__.py
│   ├── conftest.py                         # Fixtures de pytest
│   ├── test_auth.py                        # Tests de autenticación
│   ├── test_users.py                       # Tests de usuarios
│   ├── test_applications.py                # Tests de aplicaciones
│   ├── test_epics.py                       # Tests de épicas
│   ├── test_tickets.py                     # Tests de tickets
│   └── test_analytics.py                   # Tests de analítica
│
├── requirements.txt                        # Dependencias del proyecto
├── .env.example                            # Ejemplo de variables de entorno
├── .gitignore                              # Archivos a ignorar en Git
├── README.md                               # Este archivo
├── STRUCTURE.md                            # Descripción de estructura (este archivo)
├── pyproject.toml                          # Configuración de proyecto (opcional)
└── alembic.ini                             # Configuración de Alembic (opcional)
```

## Descripción Detallada de Componentes

### `/app/main.py`
- Instancia principal de FastAPI
- Configuración de CORS
- Registración de routers
- Eventos de startup/shutdown
- Endpoints de salud y raíz
- Endpoint WebSocket de notificaciones

### `/app/config.py`
- Clase `Settings` con pydantic-settings
- Carga de variables de entorno desde `.env`
- Valores por defecto seguros
- Caché con `@lru_cache()`

### `/app/database.py`
- Configuración de SQLAlchemy async
- Motor asincrónico con asyncpg
- Factory de sesiones AsyncSessionLocal
- Generador `get_db()` para inyección de dependencias
- Clase base `Base` para modelos ORM

### `/app/redis_client.py`
- Cliente Redis asincrónico
- Inicialización y cierre de conexión
- Publicación de mensajes en canales
- Suscripción a canales para WebSockets
- Funciones de caché (get, set, delete)

### `/app/schemas/`
- Esquemas Pydantic v2
- Validadores con `@field_validator`
- Modo ORM con `from_attributes=True`
- Documentación detallada en español

Esquemas principales:
- **user.py**: Autenticación y datos de usuario
- **application.py**: Contenedor principal de trabajo
- **epic.py**: Agrupación de tickets
- **ticket.py**: Tarea individual
- **subtask.py**: Paso dentro de un ticket
- **notification.py**: Alertas para usuarios
- **analytics.py**: Métricas y reportes

### `/app/middleware/auth.py`
- `hash_password()`: Hash seguro con bcrypt
- `verify_password()`: Verificación de contraseña
- `create_access_token()`: Genera JWT de acceso
- `create_refresh_token()`: Genera JWT de refresco
- `verify_token()`: Valida y decodifica JWT
- `get_current_user()`: Dependencia de autenticación
- `require_role()`: Factory para autorización

### `/app/models/` (A CREAR)
Modelos SQLAlchemy que mapean tablas:
- User: Usuarios del sistema
- Application: Aplicaciones/proyectos
- Epic: Épicas dentro de aplicaciones
- Ticket: Tareas dentro de épicas
- Subtask: Pasos dentro de tickets
- Notification: Notificaciones para usuarios
- Relaciones: ForeignKeys para conectar modelos

### `/app/routers/` (A CREAR)
Controladores FastAPI:
- `auth.py`: Login, registro, refresh token
- `users.py`: CRUD de usuarios, performance
- `applications.py`: CRUD de aplicaciones
- `epics.py`: CRUD de épicas, reorder, burndown
- `tickets.py`: CRUD de tickets, acciones, movimiento
- `subtasks.py`: CRUD de subtareas
- `analytics.py`: Métricas, heatmap, burndown
- `documents.py`: Gestión de archivos
- `notifications.py`: Consultar notificaciones

### `/app/services/` (A CREAR)
Lógica de negocio reutilizable:
- Operaciones de base de datos complejas
- Cálculos de analítica
- Integración con Redis
- Publicación de notificaciones
- Validación de reglas de negocio

### `/app/utils/` (A CREAR)
Funciones auxiliares:
- Validadores personalizados
- Helpers para conversión de datos
- Constantes de la aplicación
- Utilidades de formateo

### `/app/exceptions/` (A CREAR)
Excepciones personalizadas:
- Excepciones de usuario (UsuarioNoEncontrado, etc.)
- Excepciones de ticket (TicketNoDisponible, etc.)
- Manejo consistente de errores

### `/migrations/` (A CREAR CON ALEMBIC)
Scripts de migración de base de datos:
- Crear, modificar, eliminar tablas
- Crear índices
- Migrar datos
- Ejecutables con `alembic upgrade/downgrade`

### `/tests/` (A CREAR)
Suite de tests con pytest:
- Tests unitarios de servicios
- Tests de integración de endpoints
- Fixtures de base de datos
- Mocks de Redis

## Flujo de Datos

### Solicitud HTTP
```
Cliente HTTP
    ↓
FastAPI (main.py)
    ↓
Router (ej: routers/users.py)
    ↓
Validación Pydantic (schemas/user.py)
    ↓
Autenticación (middleware/auth.py)
    ↓
Autorización (require_role)
    ↓
Servicio de Negocio (services/user_service.py)
    ↓
Modelo ORM (models/user.py)
    ↓
Base de Datos PostgreSQL
```

### Publicación de Notificación
```
Evento en aplicación
    ↓
Servicio publica en Redis
    ↓
Canal: notifications:{user_id}
    ↓
WebSocket escucha
    ↓
JSON enviado a cliente
    ↓
JavaScript recibe notificación
```

## Convenciones de Código

### Nombres
- **Función**: `verb_noun` (ej: `create_user`, `publish_message`)
- **Variable**: `snake_case` (ej: `user_id`, `ticket_status`)
- **Clase**: `PascalCase` (ej: `UserCreate`, `TicketResponse`)
- **Constante**: `UPPER_SNAKE_CASE` (ej: `DEFAULT_TIMEOUT`)

### Comentarios
- Todos en español
- Muy detallados
- Explicar el "por qué" no solo el "qué"
- Docstrings en todas las funciones

### Type Hints
- Obligatorios en todas las funciones
- Usar `Optional[T]` para valores opcionales
- Usar `list[T]` para listas (Python 3.9+)
- Usar `dict[K, V]` para diccionarios

## Dependencias Principales

```
fastapi[standard]    # Framework web
uvicorn[standard]    # Servidor ASGI
sqlalchemy[asyncio]  # ORM async
asyncpg              # Driver PostgreSQL async
redis                # Cliente Redis
pydantic-settings    # Configuración
python-jose          # JWT
passlib              # Hashing de passwords
```

Ver `requirements.txt` para lista completa.

## Pasos Siguientes

1. **Crear modelos ORM** en `/app/models/`
   - Implementar tablas con SQLAlchemy
   - Definir relaciones
   - Crear índices

2. **Crear servicios** en `/app/services/`
   - Lógica de negocio
   - Operaciones de base de datos
   - Cálculos y transformaciones

3. **Crear routers** en `/app/routers/`
   - Endpoints REST
   - Validación de entrada
   - Llamar a servicios
   - Retornar esquemas Pydantic

4. **Crear migraciones** con Alembic
   - Scripts para crear tablas
   - Datos de ejemplo

5. **Crear tests** en `/tests/`
   - Tests unitarios
   - Tests de integración
   - Cobertura de código

6. **Desplegar**
   - Docker (Dockerfile + docker-compose)
   - CI/CD (GitHub Actions)
   - Servidor (AWS, DigitalOcean, etc.)

## Recursos Útiles

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [JWT.io](https://jwt.io/)
- [Redis Py](https://redis-py.readthedocs.io/)
