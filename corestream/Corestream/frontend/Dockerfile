# =====================================================================
# DOCKERFILE PARA FRONTEND (VUE.JS 3 + VITE)
# =====================================================================
# Imagen base optimizada Node.js Alpine para mínimo tamaño
# Utiliza dos etapas: construcción y ejecución
# =====================================================================

FROM node:20-alpine

# ===================================================================
# CONFIGURACIÓN DEL ENTORNO
# ===================================================================

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Variable de entorno para modo desarrollo
ENV NODE_ENV=development

# ===================================================================
# INSTALACIÓN DE DEPENDENCIAS
# ===================================================================

# Copiar archivos de configuración de npm
# package.json contiene dependencias principales
# package-lock.json asegura versiones exactas reproducibles
COPY package*.json ./

# Instalar todas las dependencias de npm
# Incluye dependencias de desarrollo y producción
RUN npm install

# ===================================================================
# COPIA DEL CÓDIGO FUENTE
# ===================================================================

# Copiar todo el código fuente de la aplicación
COPY . .

# ===================================================================
# EXPOSICIÓN DE PUERTOS
# ===================================================================

# Exponer puerto 5173 para servidor de desarrollo Vite
# Este puerto es donde está disponible la aplicación Vue.js
EXPOSE 5173

# ===================================================================
# COMANDO DE INICIO
# ===================================================================

# Comando por defecto para iniciar servidor de desarrollo Vite
# --host 0.0.0.0 permite acceso desde fuera del contenedor
# En desarrollo, Vite proporciona hot-module-replacement automático
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
