# Guía de Instalación de CoreStream

Esta guía explica cómo ejecutar el proyecto CoreStream localmente, tanto
para desarrollo como para probar el perfil de producción antes de
desplegarlo. Para el despliegue real en la VM, ver
[`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Requisitos previos

- **Docker y Docker Compose** (todo lo demás se ejecuta dentro de contenedores)
- Node.js y Python locales solo son necesarios si se quiere ejecutar algo
  fuera de Docker (por ejemplo, el editor con autocompletado de tipos).

## Estructura de los ficheros de Compose

Hay dos ficheros de Compose que se combinan, no se sustituyen:

- `docker-compose.yml` — perfil de **producción**: imágenes construidas
  (sin bind mounts), sin `--reload`, red bridge sin `network_mode: host`.
  No corre Postgres ni Redis propios — se conecta a instancias ya
  existentes (compartidas con otros proyectos en la misma VM). Es el que
  se usa en la VM.
- `docker-compose.dev.yml` — overlay de **desarrollo**: añade bind mounts
  con recarga en caliente, el servidor de Vite (no la build de Nginx), y
  sus propios Postgres/Redis descartables, publicados en `127.0.0.1`.

Para desarrollo local siempre se usan los dos juntos:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

## Inicio rápido (desarrollo)

1. Copiar las variables de entorno (en la raíz del repositorio, **no** en `backend/`):

   ```bash
   cp .env.example .env
   ```

   Los valores por defecto de `docker-compose.dev.yml` ya son seguros para
   desarrollo local (contraseñas de ejemplo, `ENVIRONMENT=development`);
   normalmente no hace falta editar nada de `.env` solo para levantar el
   entorno de desarrollo. `.env` sí es obligatorio y debe rellenarse con
   valores reales para el perfil de producción — ver `DEPLOYMENT.md`.

2. Levantar el stack:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
   ```

   El backend aplica las migraciones de Alembic automáticamente al
   arrancar; si fallan, el contenedor no arranca (por diseño — no hay
   arranque silencioso contra un esquema a medio migrar).

3. Comprobar que todo está sano:

   ```bash
   docker compose ps                        # los 5 servicios deben estar "healthy"
   curl http://localhost:8000/api/health    # {"status":"ok", "checks": {...}}
   ```

**URLs de acceso (desarrollo):**

- Frontend: <http://localhost:5173> (servidor de Vite, con HMR)
- Backend: <http://localhost:8000>
- Documentación interactiva de la API: <http://localhost:8000/api/docs>
  (Swagger UI — deshabilitada automáticamente si `ENVIRONMENT=production`)

## Primer usuario administrador

No existe ningún usuario por defecto ni seeder que cree uno: es deliberado
(antes había credenciales conocidas — `admin@example.com` — que se
recreaban en cada arranque). El primer ADMIN se crea a mano, una vez:

```bash
docker compose exec backend python -m app.scripts.create_admin \
    --email tu-email@empresa.com --password "unaClaveSegura123!"
```

El script se niega a correr si ya existe un ADMIN. El resto de usuarios se
crean por invitación: como ADMIN, desde **Equipo → Invitar**, se genera un
enlace de un solo uso que el invitado usa para elegir su propia contraseña.

## Ejecutar la suite de tests

```bash
# Tests unitarios (lógica pura, SQLite en memoria, rápidos)
docker compose exec backend pytest tests/ --ignore=tests/integration -q

# Tests de integración (Postgres y Redis reales, más lentos)
docker compose exec backend pytest tests/integration -q

# Lint
docker compose exec backend ruff check app/ tests/
```

Los tests de integración crean y migran su propia base de datos
(`corestream_test`) en cada sesión — no tocan los datos de desarrollo.

## Probar el perfil de producción en local

Antes de desplegar, vale la pena levantar el perfil de producción tal cual
se usará en la VM (sin el overlay de desarrollo):

```bash
cp .env.example .env
# Rellenar DATABASE_URL, REDIS_URL (una instancia de Postgres/Redis real,
# aunque sea local — el perfil de producción no levanta la suya propia),
# SECRET_KEY (openssl rand -hex 32), ALLOWED_ORIGINS, y dejar
# ENVIRONMENT=production

docker compose up -d --build
curl http://127.0.0.1:8010/api/health
curl -H "Host: tu-dominio-real.com" http://127.0.0.1:8080/   # debe dar 200
```

Con `ENVIRONMENT=production`, el backend **aborta el arranque** si
`SECRET_KEY` sigue siendo un placeholder, si `DEBUG=true`, o si
`ALLOWED_ORIGINS` es `"*"` — es intencional, no un bug.

## Backups

```bash
./backend/scripts/backup_db.sh        # backup de Postgres + volumen de storage
./backend/scripts/restore_db.sh <ruta-al-dump.sql.gz>   # restauración (pide confirmación)
```

Ver `DEPLOYMENT.md` para la configuración de cron en la VM.
