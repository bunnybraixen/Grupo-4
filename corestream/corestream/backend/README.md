# CoreStream Backend API

Backend de la aplicación CoreStream construida con FastAPI, PostgreSQL y Redis.

## Descripción General

CoreStream es una plataforma de gestión de trabajo que permite a los equipos:
- Organizar trabajo en **Aplicaciones**, **Épicas** y **Tickets**
- Asignar tareas y hacer seguimiento del progreso
- Comunicarse mediante preguntas y redirecciones
- Visualizar analítica de desempeño del equipo
- Recibir notificaciones en tiempo real vía WebSocket

## Arquitectura

```
app/
├── __init__.py              # Inicialización del paquete
├── main.py                  # Aplicación FastAPI principal
├── config.py                # Configuración y variables de entorno
├── database.py              # Configuración de SQLAlchemy
├── redis_client.py          # Cliente Redis asincrónico
├── schemas/                 # Esquemas de validación Pydantic
│   ├── __init__.py
│   ├── user.py             # Esquemas de usuario y autenticación
│   ├── application.py       # Esquemas de aplicaciones
│   ├── epic.py             # Esquemas de épicas
│   ├── ticket.py           # Esquemas de tickets
│   ├── subtask.py          # Esquemas de subtareas
│   ├── notification.py     # Esquemas de notificaciones
│   └── analytics.py        # Esquemas de analítica
├── middleware/              # Funciones de autenticación y autorización
│   ├── __init__.py
│   └── auth.py             # Middleware JWT, hash de contraseñas, roles
├── routers/                 # Controladores de endpoints (crear según sea necesario)
│   ├── __init__.py
│   ├── auth.py             # Endpoints: login, registro, refresh token
│   ├── users.py            # Endpoints: CRUD de usuarios
│   ├── applications.py      # Endpoints: CRUD de aplicaciones
│   ├── epics.py            # Endpoints: CRUD de épicas
│   ├── tickets.py          # Endpoints: CRUD de tickets, completar, redirigir
│   ├── subtasks.py         # Endpoints: CRUD de subtareas
│   ├── analytics.py        # Endpoints: métricas y analítica
│   ├── documents.py        # Endpoints: gestión de documentos
│   └── notifications.py    # Endpoints: consultar notificaciones
├── models/                  # Modelos ORM SQLAlchemy (crear según sea necesario)
│   ├── __init__.py
│   ├── user.py
│   ├── application.py
│   ├── epic.py
│   ├── ticket.py
│   ├── subtask.py
│   └── notification.py
└── utils/                   # Utilidades y funciones comunes (crear según sea necesario)
    ├── __init__.py
    └── helpers.py
```

## Requisitos Previos

- Python 3.10+
- PostgreSQL 13+
- Redis 6+
- pip o poetry para gestión de dependencias

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-repositorio>
cd corestream/corestream/backend
```

### 2. Crear entorno virtual

```bash
# Con venv
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# O con conda
conda create -n corestream python=3.10
conda activate corestream
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores locales
# Asegurar que PostgreSQL y Redis estén corriendo
```

## Configuración

### Variables de Entorno (.env)

```env
# Base de Datos
DATABASE_URL=postgresql+asyncpg://corestream:corestream@localhost:5432/corestream

# Redis
REDIS_URL=redis://localhost:6379/0

# Seguridad
SECRET_KEY=generar-una-clave-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173

# Aplicación
APP_NAME=CoreStream API
DEBUG=True
```

## Ejecución

### Desarrollo

```bash
# Con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O ejecutar main.py
python app/main.py
```

La API estará disponible en:
- **API**: http://localhost:8000/api
- **Documentación Swagger**: http://localhost:8000/api/docs
- **Documentación ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

### Producción

```bash
# Con múltiples workers
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

## Estructura de Endpoints

### Autenticación (`/api/auth`)
- `POST /login` - Iniciar sesión con email y contraseña
- `POST /register` - Registrar nuevo usuario
- `POST /refresh` - Obtener nuevo access token usando refresh token
- `POST /logout` - Cerrar sesión

### Usuarios (`/api/users`)
- `GET /` - Listar todos los usuarios
- `GET /{user_id}` - Obtener detalles de usuario
- `PUT /{user_id}` - Actualizar perfil de usuario
- `DELETE /{user_id}` - Eliminar usuario (solo admin)
- `GET /performance` - Obtener métricas de desempeño

### Aplicaciones (`/api/applications`)
- `GET /` - Listar aplicaciones del usuario
- `POST /` - Crear nueva aplicación
- `GET /{app_id}` - Obtener detalles de aplicación
- `PUT /{app_id}` - Actualizar aplicación
- `DELETE /{app_id}` - Eliminar aplicación
- `GET /{app_id}/stats` - Obtener estadísticas

### Épicas (`/api/epics`)
- `GET /` - Listar épicas
- `POST /` - Crear épica
- `GET /{epic_id}` - Obtener épica
- `PUT /{epic_id}` - Actualizar épica
- `DELETE /{epic_id}` - Eliminar épica
- `POST /{epic_id}/reorder` - Reordenar épicas
- `GET /{epic_id}/burndown` - Obtener gráfico de deuda

### Tickets (`/api/tickets`)
- `GET /` - Listar tickets
- `POST /` - Crear ticket
- `GET /{ticket_id}` - Obtener ticket
- `PUT /{ticket_id}` - Actualizar ticket
- `DELETE /{ticket_id}` - Eliminar ticket
- `POST /{ticket_id}/complete` - Marcar como completado
- `POST /{ticket_id}/move-epic` - Mover a otra épica
- `POST /{ticket_id}/question` - Agregar pregunta
- `POST /{ticket_id}/redirect` - Redirigir a otro usuario

### Subtareas (`/api/subtasks`)
- `GET /` - Listar subtareas
- `POST /` - Crear subtarea
- `GET /{subtask_id}` - Obtener subtarea
- `PUT /{subtask_id}` - Actualizar subtarea
- `DELETE /{subtask_id}` - Eliminar subtarea

### Analítica (`/api/analytics`)
- `GET /summary` - Resumen general de analítica
- `GET /users/performance` - Desempeño de usuarios
- `GET /heatmap` - Mapa de calor de actividad
- `GET /epics/{epic_id}/burndown` - Gráfico de deuda de épica

### Notificaciones (`/api/notifications`)
- `GET /` - Listar notificaciones del usuario
- `PUT /mark-read` - Marcar notificaciones como leídas
- `WS /ws/notifications/{user_id}` - WebSocket para notificaciones en tiempo real

## Esquemas Pydantic

### Validación de Datos

Todos los esquemas utilizan Pydantic v2 con validadores personalizados:

```python
# Usuario
UserCreate: email, full_name, specialty (opt), password (min 8 chars)
UserResponse: id, email, full_name, role, avatar_url, is_active, created_at

# Aplicación
ApplicationCreate: name, description (opt), color (hex format), icon (opt)
ApplicationResponse: id, name, owner_id, epic_count, pending_count, delayed_count

# Épica
EpicCreate: title, description (opt), application_id, due_date (opt)
EpicResponse: id, title, order_index, progress, total_tickets, completed_tickets

# Ticket
TicketCreate: title, description (opt), epic_id, assignee_id (opt), priority, due_date
TicketResponse: id, title, priority, status, assignee, epic_title, app_name, subtasks

# Subtarea
SubtaskCreate: title, ticket_id
SubtaskResponse: id, title, is_completed, order_index, completed_at (opt)

# Notificación
NotificationResponse: id, user_id, title, message, type, is_read, ticket_id, created_at
```

## Autenticación y Autorización

### JWT (JSON Web Tokens)

La API utiliza JWT para autenticación:

```
Header: Authorization: Bearer <token>
```

Tokens contienen:
- `sub` (subject): ID del usuario
- `role` (role): Rol del usuario (user, manager, admin)
- `exp` (expiration): Hora de expiración

### Roles

- **user**: Usuario regular (crear tickets, completar tareas)
- **manager**: Gestor de equipo (crear aplicaciones, épicas)
- **admin**: Administrador (gestionar usuarios, configuración)

### Ejemplo de Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Respuesta:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Base de Datos

### Configuración

PostgreSQL con driver async (asyncpg):

```
postgresql+asyncpg://usuario:contraseña@localhost:5432/corestream
```

### Migraciones (Alembic)

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

## Redis

Redis se utiliza para:
1. **Caché**: Almacenar datos frecuentes
2. **Pub/Sub**: Notificaciones en tiempo real vía WebSocket
3. **Sessions**: Almacenar sesiones de usuario

### Conexión

```python
from app.redis_client import get_redis, publish_message

# Obtener cliente
redis = await get_redis()

# Publicar notificación
await publish_message(
    f"notifications:{user_id}",
    {"type": "TICKET_ASSIGNED", "ticket_id": "123"}
)

# Suscribirse a canal
pubsub = await subscribe_channel(f"notifications:{user_id}")
```

## WebSocket - Notificaciones en Tiempo Real

### Cliente JavaScript

```javascript
// Conectar a WebSocket
const token = localStorage.getItem('access_token');
const ws = new WebSocket(
    `ws://localhost:8000/api/ws/notifications/${userId}?token=${token}`
);

// Escuchar notificaciones
ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    console.log('Notificación:', notification);
    
    if (notification.type === 'TICKET_ASSIGNED') {
        // Mostrar notificación de ticket asignado
    }
};

ws.onerror = (error) => {
    console.error('Error WebSocket:', error);
};

ws.onclose = () => {
    console.log('Desconectado de notificaciones');
};
```

## Testing

```bash
# Ejecutar tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
```

## Desarrollo

### Crear nuevo endpoint

1. **Crear modelo en** `app/models/mi_modelo.py`:

```python
from sqlalchemy import Column, String, UUID
from app.database import Base

class MiModelo(Base):
    __tablename__ = "mi_modelos"
    id = Column(UUID, primary_key=True)
    nombre = Column(String, nullable=False)
```

2. **Crear esquema en** `app/schemas/mi_esquema.py`:

```python
from pydantic import BaseModel

class MiEsquemaResponse(BaseModel):
    id: UUID
    nombre: str
    
    model_config = {"from_attributes": True}
```

3. **Crear router en** `app/routers/mi_router.py`:

```python
from fastapi import APIRouter
from app.middleware import get_current_user

router = APIRouter(prefix="/api/mi-recurso", tags=["mi-recurso"])

@router.get("/")
async def listar(current_user = Depends(get_current_user)):
    # Implementar lógica
    pass

@router.post("/")
async def crear(data: MiEsquemaCreate, db = Depends(get_db)):
    # Implementar lógica
    pass
```

4. **Incluir router en** `app/main.py`:

```python
from app.routers import mi_router
app.include_router(mi_router.router)
```

## Mejores Prácticas

### Código

- Todos los comentarios en español, muy detallados
- Usar type hints en todas las funciones
- Validar entrada con Pydantic
- Usar async/await para operaciones I/O
- Nombres descriptivos en variables y funciones

### Seguridad

- Nunca almacenar contraseñas en texto plano
- Usar HTTPS en producción
- Rotar SECRET_KEY periódicamente
- Validar y sanitizar entrada de usuario
- Implementar rate limiting
- Usar CORS restrictivo en producción

### Rendimiento

- Usar índices en base de datos
- Implementar paginación
- Cachear datos frecuentes
- Usar conexiones asincrónicas
- Usar batch operations cuando sea posible

### Testing

- Tests unitarios para funciones críticas
- Tests de integración para endpoints
- Coverage mínimo de 80%
- Tests de seguridad

## Troubleshooting

### Error de conexión a PostgreSQL

```
asyncpg.exceptions.PostgresError: could not connect to the server
```

Solución: Verificar que PostgreSQL está corriendo y los credenciales son correctos.

### Error de conexión a Redis

```
aioredis.exceptions.ConnectionError: [Errno 111] Connection refused
```

Solución: Verificar que Redis está corriendo en localhost:6379.

### Error de token JWT expirado

```
HTTPException: No se pudo validar el token
```

Solución: Usar el endpoint `/api/auth/refresh` con el refresh token.

## Contribución

1. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer cambios y commits: `git commit -am 'Agregar nueva funcionalidad'`
3. Subir rama: `git push origin feature/nueva-funcionalidad`
4. Crear Pull Request

## Licencia

Propietaria - CoreStream

## Autores

Equipo de CoreStream

## Contacto

Para preguntas o reportes de bugs: support@corestream.com
