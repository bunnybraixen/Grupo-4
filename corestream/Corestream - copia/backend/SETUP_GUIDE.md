# Guía de Configuración - CoreStream Backend

Este documento proporciona instrucciones paso a paso para configurar y ejecutar el backend de CoreStream.

## Archivos Creados

### Configuración Principal
- `app/config.py` - Configuración de aplicación con pydantic-settings
- `app/database.py` - Configuración de SQLAlchemy async y PostgreSQL
- `app/redis_client.py` - Cliente Redis asincrónico
- `app/main.py` - Aplicación FastAPI principal con middleware, routers y WebSocket
- `app/__init__.py` - Metadatos del paquete

### Esquemas Pydantic (Validación de Datos)
- `app/schemas/__init__.py` - Exporta todos los esquemas
- `app/schemas/user.py` - Esquemas: UserBase, UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse, TokenPayload
- `app/schemas/application.py` - Esquemas: ApplicationCreate, ApplicationUpdate, ApplicationResponse
- `app/schemas/epic.py` - Esquemas: EpicCreate, EpicUpdate, EpicReorder, EpicResponse
- `app/schemas/ticket.py` - Esquemas: TicketCreate, TicketUpdate, TicketMoveEpic, TicketComplete, TicketQuestion, TicketRedirect, TicketResponse
- `app/schemas/subtask.py` - Esquemas: SubtaskCreate, SubtaskUpdate, SubtaskResponse
- `app/schemas/notification.py` - Esquemas: NotificationResponse, NotificationMarkRead
- `app/schemas/analytics.py` - Esquemas: UserPerformance, HeatmapEntry, BurndownPoint, BurndownData, AnalyticsSummary

### Middleware y Autenticación
- `app/middleware/__init__.py` - Exporta funciones de autenticación
- `app/middleware/auth.py` - JWT, hash de contraseñas, verificación de tokens, roles

### Archivos de Configuración
- `requirements.txt` - Dependencias del proyecto
- `.env.example` - Ejemplo de variables de entorno
- `.gitignore` - Archivos a ignorar en Git (creado automáticamente)

### Documentación
- `README.md` - Documentación completa del proyecto
- `STRUCTURE.md` - Descripción detallada de la arquitectura
- `SETUP_GUIDE.md` - Este archivo (guía de configuración)

## Requisitos Previos

### Sistema Operativo
- Linux, macOS o Windows 10+ (con WSL2)

### Software Necesario
- Python 3.10 o superior
- PostgreSQL 13 o superior
- Redis 6 o superior
- pip (gestor de paquetes de Python)

### Instalación de Requisitos

#### En Linux (Ubuntu/Debian)
```bash
# Actualizar repositorios
sudo apt-get update

# Instalar PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Instalar Redis
sudo apt-get install redis-server

# Instalar Python
sudo apt-get install python3.10 python3-pip python3-venv
```

#### En macOS
```bash
# Con Homebrew
brew install postgresql redis python@3.10
```

#### En Windows
- Descargar e instalar PostgreSQL desde https://www.postgresql.org/download/windows/
- Descargar e instalar Redis desde https://github.com/microsoftarchive/redis/releases
- Descargar e instalar Python 3.10+ desde https://www.python.org/downloads/

## Pasos de Configuración

### 1. Preparar Base de Datos PostgreSQL

```bash
# Iniciar servicio PostgreSQL (si no está corriendo automáticamente)
# En Linux:
sudo systemctl start postgresql

# Conectarse a PostgreSQL
psql -U postgres

# En la consola psql, ejecutar:
CREATE DATABASE corestream;
CREATE USER corestream WITH PASSWORD 'corestream';
ALTER ROLE corestream SET client_encoding TO 'utf8';
ALTER ROLE corestream SET default_transaction_isolation TO 'read committed';
ALTER ROLE corestream SET default_transaction_deferrable TO on;
ALTER ROLE corestream SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE corestream TO corestream;
\q

# Verificar conexión
psql -U corestream -d corestream -h localhost
\q
```

### 2. Preparar Redis

```bash
# Iniciar servicio Redis (si no está corriendo automáticamente)
# En Linux:
sudo systemctl start redis-server

# Verificar que Redis está corriendo
redis-cli ping
# Debería responder: PONG
```

### 3. Clonar o Descargar Proyecto

```bash
# Si tienes acceso al repositorio Git
git clone <url-repositorio>
cd corestream/corestream/backend

# O descargar archivos manualmete
# Asegurar que estés en el directorio backend
cd /ruta/a/corestream/corestream/backend
```

### 4. Crear Entorno Virtual

```bash
# Con venv (recomendado)
python3.10 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Verificar que está activado (verás "venv" en el prompt)
which python  # Debe mostrar la ruta del venv
```

### 5. Instalar Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Verificar que se instaló correctamente
pip list | grep fastapi
```

### 6. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores (si es necesario)
nano .env  # O usa tu editor favorito

# Variables importantes a verificar:
# DATABASE_URL=postgresql+asyncpg://corestream:corestream@localhost:5432/corestream
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=generar-una-clave-segura
# DEBUG=True (para desarrollo)
```

### 7. Generar Clave Secreta Segura

```bash
# Generar clave segura (opcional, ya tiene un valor por defecto)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copiar el resultado en SECRET_KEY en .env
```

### 8. Verificar Conexiones

```bash
# Verificar PostgreSQL
psql -U corestream -d corestream -h localhost -c "SELECT version();"

# Verificar Redis
redis-cli ping
# Debería responder: PONG
```

## Ejecución de la Aplicación

### Desarrollo

```bash
# Asegurar que el entorno virtual está activado
source venv/bin/activate  # Linux/macOS

# Ejecutar la aplicación
python app/main.py

# O con uvicorn directamente (con recargas automáticas)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# La salida debe mostrar:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started server process [PID]
# INFO:     Started reloader process
```

### Acceso a la Aplicación

Una vez corriendo, puedes acceder a:
- **API Base**: http://localhost:8000/api
- **Documentación Swagger**: http://localhost:8000/api/docs
- **Documentación ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

### Verificar que Todo Funciona

```bash
# En otra terminal
curl http://localhost:8000/api/health

# Respuesta esperada:
# {"status":"ok","message":"API CoreStream funcionando correctamente","timestamp":"..."}
```

## Estructura de la Respuesta

### Esquemas Implementados

Todos los esquemas están documentados en el código con comentarios en español:

#### Usuario
```python
# Registro
POST /api/auth/register
{
  "email": "user@example.com",
  "full_name": "Juan Pérez",
  "specialty": "Backend",
  "password": "SecurePass123"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

# Respuesta
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Aplicación
```python
# Crear
POST /api/applications
{
  "name": "Mi Proyecto",
  "description": "Descripción del proyecto",
  "color": "#FF5733",
  "icon": "rocket"
}

# Respuesta incluye: id, nombre, owner_id, epic_count, pending_count, etc.
```

#### Épica
```python
# Crear
POST /api/epics
{
  "title": "Implementar autenticación",
  "description": "Sistema de login con JWT",
  "application_id": "uuid",
  "due_date": "2026-04-01T00:00:00Z"
}
```

#### Ticket
```python
# Crear
POST /api/tickets
{
  "title": "Crear endpoint de login",
  "description": "POST /auth/login",
  "epic_id": "uuid",
  "assignee_id": "uuid",
  "priority": "HIGH",
  "due_date": "2026-03-10T00:00:00Z"
}

# Completar
POST /api/tickets/{ticket_id}/complete
{
  "pr_link": "https://github.com/org/repo/pull/123"
}

# Hacer pregunta
POST /api/tickets/{ticket_id}/question
{
  "question_text": "¿Debo usar bcrypt o argon2 para hash de contraseñas?"
}

# Redirigir
POST /api/tickets/{ticket_id}/redirect
{
  "to_user_id": "uuid",
  "reason": "No tengo acceso a la base de datos para este cambio"
}
```

#### Subtarea
```python
# Crear
POST /api/subtasks
{
  "title": "Implementar hash de contraseña",
  "ticket_id": "uuid"
}
```

#### Notificación
```python
# Listar
GET /api/notifications

# Marcar como leído
PUT /api/notifications/mark-read
{
  "notification_ids": ["uuid1", "uuid2"]
}

# WebSocket (tiempo real)
WS /api/ws/notifications/{user_id}?token=jwt_token
```

#### Analítica
```python
# Resumen
GET /api/analytics/summary

# Desempeño de usuarios
GET /api/analytics/users/performance

# Mapa de calor
GET /api/analytics/heatmap

# Deuda de trabajo
GET /api/analytics/epics/{epic_id}/burndown
```

## Validaciones Implementadas

### Usuarios
- Email válido y único
- Contraseña mínimo 8 caracteres
- Nombre completo no vacío

### Aplicaciones
- Nombre no vacío
- Color en formato hexadecimal válido (#RRGGBB)

### Épicas
- Título no vacío
- Fecha límite válida

### Tickets
- Título no vacío
- Prioridad válida (CRITICAL, HIGH, MEDIUM, LOW)
- PR Link válido (GitHub, GitLab, Bitbucket)
- Pregunta mínimo 10 caracteres
- Motivo de redirección mínimo 10 caracteres

### Subtareas
- Título no vacío
- Índice de orden no negativo

### Analítica
- Métricas no negativas
- Porcentajes entre 0 y 100
- Datos de heatmap con exactamente 7 valores

## Testing (Opcional)

```bash
# Instalar dependencias de testing (ya incluidas en requirements.txt)
pip install pytest pytest-asyncio httpx

# Ejecutar tests
pytest

# Con verbosidad
pytest -v

# Con coverage
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Error: "could not connect to the server"
**Problema**: PostgreSQL no está corriendo o credenciales incorrectas
**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
psql -U corestream -d corestream -h localhost
```

### Error: "Connection refused" (Redis)
**Problema**: Redis no está corriendo
**Solución**:
```bash
# Iniciar Redis
sudo systemctl start redis-server

# Verificar que está corriendo
redis-cli ping
```

### Error: "Port 8000 already in use"
**Problema**: Otro proceso está usando el puerto 8000
**Solución**:
```bash
# Usar otro puerto
uvicorn app.main:app --reload --port 8001

# O encontrar y matar el proceso
lsof -i :8000
kill -9 <PID>
```

### Error: "ModuleNotFoundError: No module named 'fastapi'"
**Problema**: Dependencias no instaladas o entorno virtual no activado
**Solución**:
```bash
# Activar entorno virtual
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Invalid token" en login
**Problema**: Contraseña incorrecta
**Solución**: Verificar que el usuario existe y la contraseña es correcta

## Próximos Pasos

1. **Crear modelos ORM** en `app/models/` (estructura ya existe)
2. **Crear servicios** en `app/services/` (estructura ya existe)
3. **Crear routers** en `app/routers/` (estructura ya existe)
4. **Configurar migraciones** con Alembic
5. **Escribir tests** en `tests/`
6. **Desplegar** en servidor de producción

## Documentación Adicional

- Ver `README.md` para descripción general
- Ver `STRUCTURE.md` para estructura de directorios
- Ver comentarios en código para detalles técnicos

## Soporte

Para preguntas o problemas:
1. Revisar logs de error
2. Verificar configuración en .env
3. Verificar que PostgreSQL y Redis están corriendo
4. Revisar documentación en README.md

¡Listo para comenzar el desarrollo!
