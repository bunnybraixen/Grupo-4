# =====================================================================
# DOCKERFILE PARA BACKEND (FASTAPI)
# =====================================================================
# Imagen base optimizada para Python en producción
# Utiliza Python 3.11 slim para reducir tamaño
# =====================================================================

FROM python:3.11-slim

# ===================================================================
# CONFIGURACIÓN DEL ENTORNO
# ===================================================================

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variable de entorno para evitar buffering de stdout
# Permite ver logs en tiempo real en contenedores Docker
ENV PYTHONUNBUFFERED=1

# Variable de entorno para no crear archivos .pyc
# Reduce el tamaño de la imagen
ENV PYTHONDONTWRITEBYTECODE=1

# ===================================================================
# INSTALACIÓN DE DEPENDENCIAS
# ===================================================================

# Copiar archivo de requisitos de Python
COPY requirements.txt .

# Instalar dependencias de producción
# --no-cache-dir reduce el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# ===================================================================
# COPIA DEL CÓDIGO FUENTE
# ===================================================================

# Copiar todo el código de la aplicación al contenedor
COPY . .

# ===================================================================
# EXPOSICIÓN DE PUERTOS
# ===================================================================

# Exponer puerto 8000 para la API REST
EXPOSE 8000

# ===================================================================
# COMANDO DE INICIO
# ===================================================================

# Comando por defecto para iniciar el servidor Uvicorn
# Uvicorn es un servidor ASGI para ejecutar FastAPI
# El reloading se maneja desde docker-compose.yml
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
