# =====================================================================
# DOCKERFILE PARA BACKEND (FASTAPI) — imagen de producción
# =====================================================================
# Un solo servidor ASGI (uvicorn con varios workers), sin --reload, sin
# bind mount del código (se copia a la imagen), y ejecutando como usuario
# sin privilegios. El worker de ARQ (servicio `worker` en docker-compose)
# usa esta MISMA imagen con otro comando — ver docker-compose.yml.
# =====================================================================

FROM python:3.11-slim

WORKDIR /app

# PYTHONUNBUFFERED: los logs salen en tiempo real, no al cerrar el proceso.
# PYTHONDONTWRITEBYTECODE: no escribir .pyc, innecesario en un contenedor
# que se reconstruye desde la imagen en cada despliegue.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# gcc/python3-dev: hacen falta para compilar dependencias con extensiones C
# (p. ej. bcrypt) en la instalación de pip de más abajo.
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# INSTALL_DEV_DEPS: pytest/ruff/mypy no van en la imagen de producción, pero
# el mismo Dockerfile sirve de imagen de desarrollo (docker-compose.dev.yml
# pasa este build arg en true) para poder correr la suite de integración y
# el lint dentro del contenedor, contra Postgres/Redis reales.
ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

# Usuario sin privilegios: si un endpoint tiene una vulnerabilidad de
# escritura de archivos (path traversal, etc.), no corre como root.
#
# Los directorios de storage se crean y se chown-ean AQUÍ, antes del
# volumen: cuando docker-compose monta un volumen nombrado sobre una ruta
# que ya existe en la imagen, copia el contenido Y los permisos de esa ruta
# al volumen la primera vez — si no existieran ya con dueño "app" en la
# imagen, el volumen se crearía con dueño root y el proceso (corriendo como
# "app") no podría escribir en él.
RUN useradd --create-home --shell /usr/sbin/nologin app && \
    mkdir -p /app/storage/documents /app/storage/uploads && \
    chown -R app:app /app
USER app

EXPOSE 8000

# UVICORN_WORKERS es configurable por variable de entorno para ajustarlo a
# los núcleos de la VM de destino; 4 es un punto de partida razonable.
# FORWARDED_ALLOW_IPS: por defecto solo confía en loopback. El Nginx real de
# la VM llega por la red de Docker, no por 127.0.0.1 — hay que fijar esto a
# la IP real del proxy (o al gateway del bridge) en el .env de producción;
# ver docs/DEPLOYMENT.md. Dejarlo en "*" aceptaría X-Forwarded-For de
# cualquiera, permitiendo falsear la IP de origen ante el rate limiter.
# alembic upgrade head va con && (no con "|| echo … continuing"): si la
# migración falla, el contenedor debe morir, no arrancar contra un esquema
# a medio migrar.
ENV UVICORN_WORKERS=4
ENV FORWARDED_ALLOW_IPS=127.0.0.1
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS} --forwarded-allow-ips=${FORWARDED_ALLOW_IPS}"]
