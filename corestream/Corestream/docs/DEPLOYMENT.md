# Despliegue de CoreStream en la VM

Esta VM (`spot-development`) ya corre varios proyectos en contenedores
Docker — CoreStream se suma al mismo patrón: cada proyecto publica sus
puertos directo en `0.0.0.0`, sin Nginx local. El enrutamiento público
(dominio, TLS) lo gestiona algo fuera de esta máquina; a nivel de la VM,
lo único que importa es en qué puerto escucha cada cosa.

Postgres y Redis **tampoco son contenedores propios de CoreStream**: esta
VM ya tiene ambos corriendo para otros proyectos, y CoreStream se conecta
a esa misma instancia con su propia base de datos y usuario — no se monta
infraestructura duplicada.

## Lo que ya existe en la VM y CoreStream reutiliza

- **Postgres**: contenedor `db-postgre` (`ankane/pgvector`), puerto `5432`.
- **Redis**: contenedor `directa-redis-1`, puerto `6379`, sin contraseña.

Ambos pertenecen al proyecto Directa (`/opt/alloxentric/directa`), pero
están publicados en el host y cualquier otro contenedor de la VM puede
alcanzarlos por la IP privada de la VM (`hostname -I` — en el momento de
escribir esto, `10.0.0.19`).

## Paso único pendiente en Postgres: crear la base y el usuario de CoreStream

No se reutiliza `directa_db` — CoreStream necesita su propia base y su
propio usuario dentro de la misma instancia, para no mezclar datos ni
permisos con Directa:

```bash
sudo docker exec -it db-postgre psql -U directa_user -d postgres -c "
CREATE USER corestream WITH PASSWORD 'GENERAR-con-openssl-rand-hex-24';
CREATE DATABASE corestream OWNER corestream;
"
```

Redis no necesita ningún paso previo: como no tiene contraseña, CoreStream
solo necesita usar un número de base de datos que nadie más use (`/5` en
el `.env.example`) y sus canales/claves ya llevan el prefijo `corestream:`
(ver `app/redis_client.py`) — el pub/sub de Redis no se aísla por número de
base de datos, así que ese prefijo es la barrera real, no el `/5`.

## Puertos de CoreStream

- **Backend**: `8010` (8000 ya lo usa otro proyecto de esta VM)
- **Frontend**: `8080`

Si quien configura el enrutamiento público necesita otra cosa, son solo
`BACKEND_PORT`/`FRONTEND_PORT` en el `.env` — no hay ninguna otra
coordinación que hacer.

## Checklist de despliegue

1. Crear la base y el usuario de Postgres (arriba) — el único paso que
   toca algo fuera del propio repositorio de CoreStream.
2. `.env` en la raíz del repo (no `backend/.env`, ese es solo para
   desarrollo sin Docker) con:
   - `ENVIRONMENT=production`, `DEBUG=false`
   - `SECRET_KEY` generada con `openssl rand -hex 32` (no el placeholder
     de `.env.example` — el backend aborta el arranque si lo es)
   - `ALLOWED_ORIGINS=https://corestream.alloxentric.com` (sin barra final,
     o el dominio real que se vaya a usar)
   - `DATABASE_URL` con el usuario/contraseña creados en el paso 1
   - `REDIS_URL` (el default de `.env.example` ya apunta a la instancia
     compartida, solo falta la IP si cambia)
3. `docker compose up -d --build` en la raíz (usa solo `docker-compose.yml`,
   **sin** `docker-compose.dev.yml` — ese overlay es solo para desarrollo
   local, con su propio Postgres/Redis descartables).
4. `curl http://localhost:8010/api/health` responde `{"status":"ok", ...}`
   con `database` y `redis` en `"ok"`.
5. `docker compose ps`: los 3 servicios (backend, frontend, worker) en
   `healthy`.
6. Ningún usuario `@example.com` en la base de datos (no debería haber
   ninguno — ya no existe ningún seeder que los cree).
7. Primer ADMIN creado con `docker compose exec backend python -m
   app.scripts.create_admin`, con una contraseña que no viva en ningún
   repositorio.
8. Comunicarle a quien configure el enrutamiento público los dos puertos
   de arriba (8010 backend, 8080 frontend) — dos puntos que se olvidan
   siempre en esa configuración:
   - WebSocket (`/api/ws/`): necesita `proxy_http_version 1.1` +
     `Upgrade`/`Connection: upgrade` + `proxy_read_timeout` alto (el
     default de 60s corta la conexión por inactividad).
   - `client_max_body_size`/límite de tamaño de subida: el backend acepta
     hasta 50 MB; con el default típico de 1MB los uploads fallarían antes
     de llegar a la app.
   - No exponer `/metrics` al dominio público — es solo para scraping
     interno.
9. Backup ejecutado una vez (`./backend/scripts/backup_db.sh`) y
   restauración ensayada en una base limpia
   (`./backend/scripts/restore_db.sh <dump>`), ver más abajo.
10. Suite de integración en verde contra una base de datos de prueba antes
    de dar por buena la versión que se despliega (no contra la de
    producción):
    ```bash
    docker compose exec backend pytest tests/integration -q
    ```

## Backups

`backend/scripts/backup_db.sh` hace un dump de la base `corestream` en la
instancia compartida de Postgres (formato custom, comprimido) y un tar del
volumen de storage (documentos/adjuntos), con rotación configurable. Cron
sugerido en la VM:

```cron
0 3 * * * cd /ruta/a/Corestream && ./backend/scripts/backup_db.sh >> /var/log/corestream-backup.log 2>&1
```

`backend/scripts/restore_db.sh <dump>` restaura (pide confirmación
explícita — sobrescribe la base actual). Ensayar la restauración contra una
base de datos limpia antes de necesitarla de verdad es parte del checklist,
no un paso opcional.

## Actualizar a una versión nueva

```bash
git pull
docker compose up -d --build   # reconstruye solo lo que cambió
docker compose ps              # confirmar que los 3 servicios vuelven a "healthy"
```

El volumen `storage-data` (documentos/adjuntos subidos) persiste entre
despliegues — no se recrea con `up`, solo con `down -v` (que no debería
usarse nunca en producción sin un backup fresco primero). Los datos en
Postgres/Redis viven en la instancia compartida, fuera del ciclo de vida de
CoreStream — no hay volumen propio que gestionar para ellos.
