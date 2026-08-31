# CoreStream Frontend

Plataforma de Gestión de Proyectos - Interfaz Frontend con Vue 3

## Descripción

CoreStream Frontend es una aplicación moderna construida con Vue 3, TypeScript y Tailwind CSS. Proporciona una interfaz intuitiva para gestionar proyectos, épicas, tareas y equipos.

## Tecnologías

- **Vue 3.4** - Framework progresivo de JavaScript
- **Vite 5** - Herramienta de construcción rápida
- **TypeScript** - JavaScript con tipos estáticos
- **Tailwind CSS 3** - Framework de estilos por utilidad
- **Pinia 2** - Gestor de estado
- **Vue Router 4** - Enrutamiento
- **Axios** - Cliente HTTP
- **Vue i18n 9** - Internacionalización
- **Chart.js + vue-chartjs** - Gráficos y visualizaciones
- **Vuedraggable** - Drag & drop

## Instalación

```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev

# Compilar para producción
npm run build

# Verificar tipos TypeScript
npm run type-check
```

## Estructura del Proyecto

```
src/
├── main.ts                 # Punto de entrada de la aplicación
├── App.vue                # Componente raíz
├── index.html             # Archivo HTML principal
│
├── types/
│   └── index.ts          # Definiciones de tipos TypeScript
│
├── services/
│   └── api.ts            # Cliente HTTP y métodos de API
│
├── router/
│   └── index.ts          # Configuración de Vue Router
│
├── stores/               # Estado global con Pinia (pendiente)
├── components/           # Componentes reutilizables
├── views/                # Vistas/páginas
│   ├── LoginView.vue     # Página de login
│   ├── NotFoundView.vue  # Página 404
│   ├── admin/            # Vistas de administración
│   └── dev/              # Vistas de desarrollo
├── layouts/              # Layouts para diferentes secciones
│   ├── AdminLayout.vue
│   └── DeveloperLayout.vue
└── assets/
    └── styles/
        └── global.css    # Estilos globales y Tailwind
```

## Configuración

### Vite (`vite.config.ts`)

- Plugin Vue 3
- Alias `@/` apunta a `src/`
- Proxy de API a `localhost:8000`
- Proxy de WebSocket a `localhost:8000`

### Tailwind (`tailwind.config.js`)

Colores personalizados de CoreStream:
- Primary: #2563EB (Azul)
- Success: #10B981 (Verde)
- Warning: #F59E0B (Ámbar)
- Danger: #EF4444 (Rojo)
- Indigo: #6366F1 (Índigo)

Tema oscuro habilitado con clase `dark` en elemento `<html>`

### TypeScript (`tsconfig.json`)

- Modo estricto activado
- Alias `@/*` para importaciones desde `src/`
- Tipos incluyen Node.js y Vite

## Características

### Autenticación
- Login/Registro de usuarios
- JWT tokens con refresh automático
- Guards de navegación por rol
- Gestión de sesión

### Roles y Permisos
- **ADMIN**: Acceso total al sistema, gestión de usuarios
- **GROUP_LEADER**: Gestión de equipo, asignación de tareas
- **DEVELOPER**: Trabajar en tareas asignadas

### Módulos Principales

#### Administración
- Constructor de aplicaciones y épicas
- Analítica global del sistema
- Gestión de documentación técnica
- Gestión de equipo y usuarios

#### Desarrollo
- Workbench personal (tareas asignadas)
- Gestión de cargas/documentos
- Asignación de tareas (solo líderes)

### Funcionalidades

- Gestión de aplicaciones (proyectos)
- Gestión de épicas (conjuntos de tareas)
- Gestión de tareas/tickets con drag & drop
- Subtareas y checklists
- Sistema de notificaciones
- Documentos y archivos adjuntos
- Análisis y reportes
- Internacionalización (español/inglés)
- Tema oscuro/claro

## API Service

El archivo `src/services/api.ts` centraliza toda la comunicación con el backend:

```typescript
// Autenticación
await api.auth.login(credentials)
await api.auth.register(data)
await api.auth.getMe()

// Aplicaciones
await api.applications.list()
await api.applications.create(data)
await api.applications.getById(appId)

// Épicas
await api.epics.list(appId)
await api.epics.create(appId, data)

// Tickets
await api.tickets.list(filters)
await api.tickets.create(data)
await api.tickets.getById(ticketId)
await api.tickets.move(ticketId, newEpicId, orderIndex)

// Análisis
await api.analytics.getSummary()
await api.analytics.getBurndown(appId)

// Notificaciones
await api.notifications.list()
await api.notifications.getUnreadCount()
```

## Tipos TypeScript

Todos los tipos están definidos en `src/types/index.ts`:

- `User` - Información del usuario
- `UserRole` - Roles del sistema
- `Application` - Proyecto
- `Epic` - Conjunto de tareas
- `Ticket` - Tarea individual
- `Subtask` - Subtarea
- `Notification` - Notificación
- `Document` - Archivo adjunto
- `AnalyticsSummary` - Resumen de análisis
- Y muchos más...

## Componentes Principales

### App.vue
- Componente raíz
- Gestión de tema oscuro/claro
- Validación de autenticación
- RouterView

### Layouts
- `AdminLayout.vue` - Layout para administradores
- `DeveloperLayout.vue` - Layout para desarrolladores
- Ambos incluyen sidebar de navegación

### NotificationContainer
- Muestra notificaciones toast globales
- Se disparan desde cualquier parte de la aplicación

## Internacionalización

Soporta español (es) e inglés (en) por defecto. Los mensajes se definen en `src/main.ts` usando Vue i18n.

Para usar traducciones en componentes:

```vue
<template>
  <button>{{ $t('common.save') }}</button>
</template>
```

## Modo Oscuro

El modo oscuro se controla con la clase `dark` en el elemento `<html>`:

```typescript
// Activar modo oscuro
document.documentElement.classList.add('dark')

// Desactivar modo oscuro
document.documentElement.classList.remove('dark')
```

Los estilos Tailwind se adaptan automáticamente con selectores `dark:`:

```html
<!-- Bg blanco en claro, gris en oscuro -->
<div class="bg-white dark:bg-gray-900"></div>
```

## Desarrollo

### Comandos

```bash
# Desarrollo
npm run dev         # Inicia Vite en http://localhost:5173

# Producción
npm run build       # Compila para producción
npm run preview     # Previsualiza compilación

# Tipos
npm run type-check  # Verifica tipos TypeScript
```

### Proxy de API

Vite automáticamente redirige:
- `/api/*` → `http://localhost:8000/api/*`
- `/ws` → `ws://localhost:8000/ws`

### Hot Module Replacement (HMR)

Vite proporciona HMR automático:
- Cambios en componentes `.vue` se reflejan al instante
- Estado se preserva durante cambios
- Servidor mantiene actualizaciones sin reload

## Interceptores de Axios

El servicio API incluye interceptores para:
- Agregar token JWT automáticamente a cada request
- Renovar token cuando expira (401)
- Reintentar request original con nuevo token
- Limpiar tokens si refresh falla

## Estructura de Rutas

```
/                          # Raíz (redirige según rol)
/login                     # Login (público)
/admin                     # Admin layout
  /admin/builder           # Constructor de proyectos
  /admin/analytics         # Analítica global
  /admin/code-docs         # Documentación técnica
  /admin/team              # Gestión de equipo
/dev                       # Developer layout
  /dev/workbench           # Tareas personales
  /dev/uploads             # Cargas de documentos
  /dev/team-assignment     # Asignación (solo líder)
```

## Performance

- Lazy loading de rutas con `import()`
- Tree-shaking de dependencias no utilizadas
- Code splitting automático con Vite
- Optimización de CSS con Tailwind (purga de clases no usadas)
- Compresión gzip en producción

## Accesibilidad

- Navegación por teclado soportada
- Focus visible en elementos interactivos
- Semántica HTML correcta
- Contraste de colores según WCAG
- ARIA labels donde es necesario

## Próximos Pasos

- [ ] Implementar componentes UI reutilizables
- [ ] Crear stores Pinia para estado global
- [ ] Implementar sistema de notificaciones
- [ ] Agregar formularios validados
- [ ] Implementar tablas de datos
- [ ] Agregar gráficos y visualizaciones
- [ ] Testing con Vitest
- [ ] E2E testing con Cypress

## Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.

## Licencia

Todos los derechos reservados - CoreStream Project
