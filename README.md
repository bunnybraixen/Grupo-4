**PROYECTO: CORESTREAM WEB**

**DESCRIPCIÓN**
CoreStream es una plataforma web de inteligencia operacional para la gestión y control de proyectos de desarrollo de software. Está dirigida principalmente a equipos de desarrollo, líderes de grupo y administradores, permitiendo organizar y monitorear el trabajo mediante la jerarquía: Aplicaciones -> Épicas -> Tickets -> Subtareas.

Nota de versión: Este proyecto corresponde a la continuidad de CoreStream 1.0, con el objetivo de incorporar nuevas funcionalidades y mejoras para evolucionar la plataforma hacia una solución más completa y competitiva en la gestión de proyectos.

**TECNOLOGÍAS UTILIZADAS**

Frontend:

Lenguajes: TypeScript, JavaScript, HTML5, CSS3

Framework: Vue 3

Build Tool: Vite

Estado Global: Pinia

Navegación: Vue Router

Cliente HTTP: Axios

Estilos UI: Tailwind CSS

Componentes e Interacción: Vue Draggable, Vue-i18n (Internacionalización)

Visualización y Reportes: Chart.js, ApexCharts, jsPDF

Testing: Vitest, Cypress

Backend:

Lenguaje: Python

Framework Web: FastAPI

Servidor ASGI: Uvicorn

Validación de Datos: Pydantic v2

ORM y Migraciones: SQLAlchemy, Alembic

Conector BD: asyncpg (PostgreSQL asíncrono)

Cache y Tareas Asíncronas: Redis, ARQ

Comunicación en Tiempo Real: WebSockets

Seguridad: JWT (JSON Web Tokens), bcrypt, RBAC (Control de Acceso Basado en Roles)

Testing: pytest, pytest-asyncio

Base de Datos:

Motor Principal: PostgreSQL

Memoria / Cache / PubSub: Redis

DevOps, Infraestructura y CI/CD:

Contenedorización: Docker, Docker Compose

Control de Versiones y CI/CD: Git, GitHub, GitHub Actions

Despliegue Cloud: Vercel (Frontend), Railway (Backend, PostgreSQL y Redis)

**ARQUITECTURA DE LA SOLUCIÓN**

La plataforma sigue una arquitectura desacoplada (Decoupled System) basada en servicios distribuidos con comunicación asíncrona:

Capa de Presentación (Frontend): Single Page Application (SPA) construida en Vue 3 y Vite. Se comunica con la API Backend mediante peticiones REST (Axios) y conexiones persistentes en tiempo real vía WebSockets.

Capa de Aplicación (Backend): API REST asíncrona construida con FastAPI. Cuenta con capa de autenticación y autorización mediante JWT y middleware RBAC, además de encolado y procesamiento de tareas en segundo plano a través de ARQ y Redis.

Capa de Datos (Persistencia y Caching): PostgreSQL como base de datos relacional principal (gestionada por SQLAlchemy y Alembic). Redis actúa como intermediario para caché de respuestas, cola de tareas de ARQ y broker para eventos/PubSub en tiempo real.

**INSTRUCCIONES PARA EJECUTAR EL PROYECTO LOCALMENTE**

Prerrequisitos:
Asegúrate de tener instalados los siguientes componentes en tu sistema: Git, Docker, Docker Compose, Node.js (v18+ recomendado) y Python (v3.10+ recomendado).

Opción 1: Ejecución mediante Docker Compose (Recomendado)
Es la forma más rápida de levantar todos los servicios (Frontend, Backend, PostgreSQL y Redis) en contenedores.

Clonar el repositorio:
git clone https://github.com/tu-usuario/corestream.git
cd corestream

Configurar variables de entorno:
cp .env.example .env

Levantar servicios:
docker-compose -f docker-compose.dev.yml up --build

Acceso a los servicios:

Frontend: http://localhost:5173

Backend API Docs: http://localhost:8000/docs

Opción 2: Ejecución Manual por Separado

Servicios Base (PostgreSQL y Redis):
docker-compose up -d postgres redis

Configurar y Ejecutar el Backend (Python / FastAPI):
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn main:app --reload --port 8000

Configurar y Ejecutar el Frontend (Vue 3 / Vite):
cd frontend
npm install
npm run dev

Ejecución de Tests:

Backend (Pytest): pytest

Frontend (Vitest y Cypress): npm run test:unit / npm run test:e2e

**INTEGRANTES DEL EQUIPO Y ROLES**

Pablo Figueroa: Líder de Proyecto / Backend Developer. Responsable de la gestión del proyecto, arquitectura del sistema, desarrollo de API REST (FastAPI) e integraciones.

Diego Fevre: Backend & Database Developer. Responsable del diseño, modelado y optimización de la base de datos (PostgreSQL), migraciones y consultas.

Diego Jeldres: Frontend Developer. Responsable del diseño e implementación de la interfaz de usuario (Vue 3, Tailwind CSS) y la lógica del cliente.

**METODOLOGÍA DE TRABAJO**

El equipo utiliza un enfoque Híbrido (Cascada / Scrum):

Fase de Análisis y Diseño (Cascada): Definición formal previa del alcance del sistema, modelo de datos, arquitectura general y requerimientos del proyecto.

Fase de Desarrollo Iterativo (Scrum): Desarrollo organizado en ciclos/sprints, gestión de tareas y seguimiento del progreso mediante la jerarquía del proyecto (Épicas, Tickets y Subtareas), e integración continua (CI/CD) automatizada a través de GitHub Actions.
