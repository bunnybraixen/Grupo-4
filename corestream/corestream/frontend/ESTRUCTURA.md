# Estructura del Proyecto CoreStream Frontend

Este documento detalla la estructura completa del proyecto frontend de CoreStream.

## Archivos de Configuración (Raíz)

### `package.json`
**Propósito**: Define dependencias, scripts y metadatos del proyecto

**Contenido**:
- Nombre: `corestream-frontend`
- Versión: 1.0.0
- Scripts: dev, build, preview, type-check
- Dependencias principales:
  - vue@3.4: Framework Vue
  - vue-router@4: Enrutamiento
  - pinia@2: Gestión de estado
  - axios: Cliente HTTP
  - tailwindcss: Framework de estilos
  - typescript: Tipos estáticos

### `vite.config.ts`
**Propósito**: Configuración del bundler Vite

**Configuración**:
- Plugin Vue 3 para procesar archivos .vue
- Alias `@/` apunta a `src/`
- Proxy `/api` a `http://localhost:8000`
- Proxy `/ws` a `ws://localhost:8000` (WebSocket)
- Puerto desarrollo: 5173

**Comentarios**: Muy detallado en español explicando cada sección

### `tailwind.config.js`
**Propósito**: Configuración de Tailwind CSS

**Configuración**:
- Content paths: `./src/**/*.{vue,ts,tsx}`
- Colores personalizados:
  - primary: #2563EB (Azul)
  - success: #10B981 (Verde)
  - warning: #F59E0B (Ámbar)
  - danger: #EF4444 (Rojo)
  - indigo: #6366F1 (Índigo)
- darkMode: 'class' (usa clase `dark` en <html>)

**Comentarios**: Explicación detallada de cada color corporativo

### `postcss.config.js`
**Propósito**: Configuración de PostCSS

**Plugins**:
- tailwindcss: Genera clases CSS
- autoprefixer: Añade prefijos de navegador

**Comentarios**: Explicación clara del orden de ejecución

### `tsconfig.json`
**Propósito**: Configuración de TypeScript

**Configuración**:
- target: ES2020
- module: ESNext
- strict: true
- moduleResolution: bundler
- Paths alias: `@/*` apunta a `./src/*`

**Comentarios**: Explicación de cada opción y su propósito

### `index.html`
**Propósito**: Punto de entrada HTML

**Contenido**:
- Meta tags (charset, viewport)
- Elemento `<div id="app">` para montar Vue
- Script que carga `main.ts`

**Comentarios**: Explicación de cada sección

### `.env.example`
**Propósito**: Plantilla de variables de entorno

**Variables**:
- VITE_PORT: Puerto de desarrollo
- VITE_API_BASE_URL: URL de API
- VITE_BACKEND_URL: URL del backend
- VITE_PUBLIC_URL: URL pública en producción
- Otras variables de configuración

### `.gitignore`
**Propósito**: Define archivos que Git ignora

**Excludes**:
- node_modules
- dist, build
- archivos de editor (.vscode, .idea)
- .env (no commitear variables sensibles)
- Archivos temporales y logs

### `README.md`
**Propósito**: Documentación del proyecto

**Secciones**:
- Descripción general
- Tecnologías utilizadas
- Instrucciones de instalación
- Estructura del proyecto
- Características principales
- Ejemplos de uso de API
- Guía de desarrollo

---

## Código Fuente (src/)

### `main.ts`
**Propósito**: Punto de entrada de la aplicación Vue

**Responsabilidades**:
- Crear instancia de Vue con `createApp(App)`
- Instalar plugins: Pinia (estado), Router (navegación), i18n (idiomas)
- Importar estilos globales (Tailwind CSS)
- Montar aplicación en `#app`
- Configurar i18n con idiomas español e inglés

**Comentarios**: Muy detallado explicando cada etapa de inicialización

### `App.vue`
**Propósito**: Componente raíz de la aplicación

**Funcionalidades**:
- Renderiza RouterView (ruta actual)
- Gestiona tema oscuro/claro
- Valida autenticación al cargar
- Restaura tokens de sesión
- Escucha cambios de preferencia del sistema
- Renderiza NotificationContainer

**Comentarios**: Explicación de cada método y ciclo de vida

### `assets/styles/global.css`
**Propósito**: Estilos globales de la aplicación

**Contenido**:
- Importación de Tailwind (@tailwind directives)
- Variables CSS personalizadas
- Estilos base (html, body)
- Estilos de scrollbar
- Estilos de enlaces y botones
- Estilos de inputs
- Estilos de tablas
- Utilidades personalizadas (truncate, fade, pulse)

**Comentarios**: Cada sección tiene comentarios explicativos

### `types/index.ts`
**Propósito**: Definiciones centralizadas de tipos TypeScript

**Enumeraciones**:
- `UserRole`: ADMIN, GROUP_LEADER, DEVELOPER
- `TicketStatus`: TODO, IN_PROGRESS, BLOCKED, REDIRECTED, DONE
- `TicketPriority`: LOW, MEDIUM, HIGH, URGENT
- `EventType`: 12 tipos de eventos registrados
- `NotificationType`: ASSIGNMENT, STATUS_CHANGE, COMMENT, BLOCKED, SYSTEM
- `DocumentType`: SPECIFICATION, TEST_CASE, SCREENSHOT, SOURCE_CODE, CONFIG, OTHER

**Interfaces Principales**:
- `User`: Información de usuario (id, email, fullName, role, specialty, avatarUrl)
- `Application`: Proyecto (id, name, description, color, icon, counts)
- `Epic`: Conjunto de tareas (title, description, progress, tickets)
- `Ticket`: Tarea individual (title, status, priority, assignee, time tracking)
- `Subtask`: Subtarea de un ticket
- `Notification`: Notificación del sistema
- `Document`: Archivo adjunto
- `AnalyticsSummary`: Resumen de métricas

**Interfaces de Utilidad**:
- `ApiResponse<T>`: Envuelve respuestas del servidor
- `AuthTokens`: JWT tokens de autenticación
- `PaginatedResponse<T>`: Respuestas con paginación
- `TicketFilters`: Filtros para búsqueda de tareas

**Comentarios**: Cada tipo, enum e interfaz tiene comentarios detallados en español

### `services/api.ts`
**Propósito**: Cliente HTTP centralizado y métodos de API

**Características**:
- Instancia de Axios con baseURL `/api`
- Interceptor de request: agrega token JWT automáticamente
- Interceptor de response: maneja tokens expirados, intenta renovar
- Métodos organizados en módulos:
  - `auth`: login, register, refresh, getMe, updateMe, logout
  - `users`: list, getById, update, delete, changeRole, getStats
  - `applications`: list, create, getById, update, delete
  - `epics`: list, create, getById, update, delete, reorder, uploadDoc
  - `tickets`: list, create, getById, update, delete, move, complete, question, etc.
  - `subtasks`: create, update, delete, reorder
  - `analytics`: getSummary, getPerformance, getHeatmap, getBurndown, exportCsv
  - `documents`: list, upload, download, delete, translate
  - `notifications`: list, getUnreadCount, markRead, markAllRead

**Funciones Exportadas**:
- `setAuthTokens(tokens)`: Actualiza tokens en servicio
- `clearAuthTokens()`: Limpia tokens de sesión

**Comentarios**: Cada método y módulo tiene documentación extensiva en español

### `router/index.ts`
**Propósito**: Configuración de Vue Router

**Rutas Definidas**:
```
/ (raíz)
/login (público)
/admin (requiere ADMIN)
  /admin/builder
  /admin/analytics
  /admin/code-docs
  /admin/team
/dev (requiere DEVELOPER o GROUP_LEADER)
  /dev/workbench
  /dev/uploads
  /dev/team-assignment (solo GROUP_LEADER)
/:pathMatch (404)
```

**Guards de Navegación**:
- Valida autenticación antes de rutas protegidas
- Valida roles requeridos
- Redirige a login si no autenticado
- Actualiza título de página
- Scroll al top en nuevas rutas

**Configuración**:
- Modo history: URLs limpias sin #
- Lazy loading de componentes con `import()`

**Comentarios**: Explicación detallada de cada ruta y guard

### `layouts/AdminLayout.vue`
**Propósito**: Layout para sección de administración

**Estructura**:
- Sidebar con navegación a:
  - Constructor
  - Analítica
  - Documentación
  - Equipo
- RouterView para contenido principal

### `layouts/DeveloperLayout.vue`
**Propósito**: Layout para sección de desarrollo

**Estructura**:
- Sidebar con navegación a:
  - Workbench
  - Mis Cargas
  - Asignación de Equipo (solo visible para GROUP_LEADER)
- RouterView para contenido principal

### Vistas (views/)

#### `LoginView.vue`
- Placeholder para formulario de autenticación
- Centro de pantalla con logo y formulario

#### `NotFoundView.vue`
- Página 404
- Link para volver al inicio

#### Admin Views

**`admin/BuilderView.vue`**
- Gestión de aplicaciones y épicas
- Interfaz drag & drop

**`admin/AnalyticsView.vue`**
- Estadísticas globales del sistema
- Rendimiento del equipo

**`admin/CodeDocsView.vue`**
- Gestión de documentación técnica
- Especificaciones y archivos

**`admin/TeamView.vue`**
- Gestión de usuarios
- Asignación de roles

#### Developer Views

**`dev/WorkbenchView.vue`**
- Panel personal de tareas
- Tareas asignadas y en progreso

**`dev/UploadsView.vue`**
- Gestión de documentos
- Subida y descarga de archivos

**`dev/TeamAssignmentView.vue`**
- Asignación de tareas al equipo
- Solo para líderes de grupo

### `components/NotificationContainer.vue`
**Propósito**: Componente para mostrar notificaciones globales

**Funcionalidad**:
- Renderiza notificaciones toast
- Posicionado en esquina superior derecha
- Se dispara desde cualquier parte de la app

---

## Arquitetura y Patrones

### Estructura de Carpetas
```
frontend/
├── src/
│   ├── main.ts                    # Entrada principal
│   ├── App.vue                    # Componente raíz
│   ├── index.html                 # HTML base
│   ├── assets/
│   │   └── styles/
│   │       └── global.css         # Estilos globales
│   ├── types/
│   │   └── index.ts               # Todos los tipos TS
│   ├── services/
│   │   └── api.ts                 # Cliente HTTP
│   ├── router/
│   │   └── index.ts               # Rutas y guards
│   ├── stores/                    # Pinia stores (pendiente)
│   ├── components/                # Componentes reutilizables
│   │   └── NotificationContainer.vue
│   ├── views/                     # Páginas/vistas
│   │   ├── LoginView.vue
│   │   ├── NotFoundView.vue
│   │   ├── admin/
│   │   │   ├── BuilderView.vue
│   │   │   ├── AnalyticsView.vue
│   │   │   ├── CodeDocsView.vue
│   │   │   └── TeamView.vue
│   │   └── dev/
│   │       ├── WorkbenchView.vue
│   │       ├── UploadsView.vue
│   │       └── TeamAssignmentView.vue
│   └── layouts/                   # Layouts
│       ├── AdminLayout.vue
│       └── DeveloperLayout.vue
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── index.html
├── .env.example
├── .gitignore
└── README.md
```

### Flujo de Autenticación

1. Usuario accede a `/login`
2. Formulario envía credentials a `/api/auth/login`
3. Backend responde con usuario y tokens
4. App almacena tokens en localStorage
5. `setAuthTokens()` actualiza servicio de API
6. Router redirige según rol del usuario
7. Interceptor automáticamente agrega JWT a requests
8. Cuando token expira (401), interceptor intenta renovar con refreshToken
9. Si renovación exitosa, reintenta request original
10. Si renovación falla, limpia tokens y redirige a login

### Flujo de Navigación

1. Usuario hace clic en link o `router.push()`
2. Router guard `beforeEach` se ejecuta
3. Guard valida:
   - ¿Ruta requiere autenticación? ¿Tiene token?
   - ¿Tiene rol requerido?
   - ¿Ya está en login? Redirige a dashboard
4. Guard actualiza título de página desde `meta.title`
5. Router permite navegación
6. Componente nuevo se monta
7. Router hook `afterEach` se ejecuta (scroll a top)

### Comunicación con API

1. Componente importa `api` desde `services/api.ts`
2. Llama método de API: `await api.applications.list()`
3. Axios interceptor automáticamente agrega token JWT
4. Request se envía a `/api/applications`
5. Vite proxy redirige a `http://localhost:8000/api/applications`
6. Backend procesa y responde
7. Response interceptor maneja errores 401
8. Promise se resuelve/rechaza según resultado
9. Componente actualiza state y UI reactiva se actualiza

---

## Técnicas y Características

### Composition API + Script Setup
```typescript
<script setup lang="ts">
// Sintaxis moderna de Vue 3
const message = ref('Hola')
const handleClick = () => {
  message.value = 'Adiós'
}
</script>
```

### Lazy Loading de Rutas
```typescript
component: () => import('@/views/admin/BuilderView.vue')
// Se carga solo cuando se navega a la ruta
```

### Tipos Tipados
Toda comunicación con API está tipada:
```typescript
const response = await api.applications.list()
// response tiene tipo ApiResponse<PaginatedResponse<Application>>
// Autocompletado y type-checking en compilación
```

### Interceptores Automáticos
- JWT token se agrega automáticamente
- Renovación de token transparente
- Reintentos automáticos
- Manejo de errores centralizado

### Temas Oscuro/Claro
- Clase `dark` en <html>
- Selectores `dark:` en Tailwind
- Escucha cambios de preferencia del sistema
- Guarda preferencia en localStorage

### Internacionalización
- Soporte para múltiples idiomas
- Fácil agregar nuevos idiomas
- Acceso con `$t('clave')`

---

## Próximas Fases de Desarrollo

1. **Stores Pinia**: Estado global para usuario, notificaciones, preferencias
2. **Componentes**: Botones, inputs, modales, tablas reutilizables
3. **Formularios**: Validación con VeeValidate o Zod
4. **Testing**: Vitest para unitarios, Cypress para E2E
5. **Componentes Avanzados**: Drag & drop, gráficos, editor rich text
6. **PWA**: Service worker, offline support
7. **Analytics**: Tracking de eventos de usuario
8. **Performance**: Code splitting, lazy loading, caching

---

## Referencias de Comentarios

Todos los archivos tienen comentarios extensivos en ESPAÑOL:
- Cada función tiene descripción de propósito
- Parámetros explicados
- Ejemplos de uso donde aplica
- Secciones lógicas separadas con headers
- Variables explicadas con sus roles

Esto facilita:
- Onboarding de nuevos desarrolladores
- Comprensión del flujo
- Mantenimiento a futuro
- Debugging rápido

