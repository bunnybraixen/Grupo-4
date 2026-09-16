# =====================================================================
# DOCKERFILE PARA FRONTEND (VUE 3 + VITE) — imagen de producción
# =====================================================================
# Multi-stage: se compila con Node y se sirve con Nginx. El resultado no
# lleva Node, npm, ni node_modules — solo los estáticos compilados.
#
# El servidor de desarrollo de Vite NUNCA debe usarse en producción: valida
# la cabecera Host y responde 403 Blocked request para cualquier dominio no
# incluido en su allowlist (verificado con corestream.alloxentric.com). Este
# Dockerfile reemplaza eso por Nginx sirviendo la build, que no tiene esa
# restricción. Para desarrollo local sigue existiendo Dockerfile.dev.
# =====================================================================

FROM node:20-bookworm AS build

WORKDIR /app

COPY package*.json ./
RUN npm cache clean --force && npm ci --force

COPY . .

# Las variables VITE_* solo existen en tiempo de build (Vite las incrusta en
# el bundle, no las lee en runtime). Por defecto no se fija ninguna: api.ts
# ya usa '/api' si VITE_API_BASE_URL no está definida, que es lo correcto
# cuando el Nginx de la VM sirve el frontend y el backend bajo el mismo
# dominio y hace proxy_pass de /api hacia el backend.
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# ---------------------------------------------------------------------
# Etapa final: solo Nginx + los estáticos compilados
# ---------------------------------------------------------------------
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- --timeout=3 http://127.0.0.1:80/ || exit 1
