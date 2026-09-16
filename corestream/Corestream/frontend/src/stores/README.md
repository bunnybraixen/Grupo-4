# CoreStream Pinia Stores

Tienda de estado centralizada para CoreStream Vue 3 frontend usando Pinia con Composition API (Setup Stores).

## Archivos de Tiendas

### 1. **auth.ts** (11 KB)
**Store de Autenticación**
- Gestiona sesión JWT, usuario actual y permisos RBAC
- **Estado**: `user`, `tokens`, `isAuthenticated`, `isLoading`, `error`
- **Getters**: `isAdmin`, `isDeveloper`, `isGroupLeader`, `userRole`, `fullName`, `userEmail`, `isTokenExpiringSoon`
- **Acciones**:
  - `initialize()` - Restaura sesión desde localStorage
  - `login(email, password)` - Autentica usuario
  - `register(data)` - Registra nuevo usuario
  - `fetchMe()` - Obtiene datos actuales del usuario
  - `refreshToken()` - Refresca access token
  - `updateProfile(data)` - Actualiza perfil del usuario
  - `changePassword(oldPassword, newPassword)` - Cambia contraseña
  - `logout()` - Cierra sesión
  - `requestPasswordReset(email)` - Solicita reset por email
  - `confirmPasswordReset(token, newPassword)` - Confirma reset

### 2. **applications.ts** (8.8 KB)
**Store de Aplicaciones**
- Gestiona lista de aplicaciones del sistema
- **Estado**: `applications`, `selectedApp`, `isLoading`, `error`
- **Getters**: `selectedAppId`, `sortedByName`, `sortedByPending`, `sortedByDelayed`, `overallProgress`, `totalDelayedTickets`
- **Acciones**:
  - `fetchAll()` - Obtiene todas las aplicaciones
  - `create(data)` - Crea nueva aplicación
  - `update(id, data)` - Actualiza aplicación
  - `remove(id)` - Elimina aplicación
  - `selectApp(app)` - Selecciona aplicación activa
  - `selectAppById(id)` - Selecciona por ID
  - `getApplicationById(id)` - Obtiene por ID
  - `searchApplications(query)` - Busca por nombre
  - `refreshApplication(id)` - Refresca una app específica
  - `clear()` - Limpia estado

### 3. **epics.ts** (11 KB)
**Store de Épicos**
- Gestiona épicos dentro de aplicaciones con reordenamiento y progreso
- **Estado**: `epics`, `isLoading`, `error`, `collapsedEpics`, `associatedTickets`
- **Getters**: `sortedByOrder`, `withProgress`, `collapsedEpicIds`, `expandedEpics`, `overallEpicsProgress`
- **Acciones**:
  - `fetchByApp(appId)` - Obtiene épicos de una app
  - `create(data)` - Crea nuevo épico
  - `update(id, data)` - Actualiza épico
  - `remove(id)` - Elimina épico
  - `reorder(epicId, newIndex)` - Reordena épico (PATCH API)
  - `toggleCollapse(epicId)` - Alterna collapse
  - `expand(epicId)` - Expande épico
  - `collapse(epicId)` - Colapsa épico
  - `expandAll()` / `collapseAll()` - Operaciones globales
  - `getEpicById(id)` - Obtiene por ID
  - `setEpicTickets(epicId, tickets)` - Actualiza tickets asociados
  - `clear()` - Limpia estado

### 4. **tickets.ts** (20 KB) ⭐ MÁS IMPORTANTE
**Store de Tickets - Funcionalidad Compleja**
- Gestiona ciclo de vida completo de tickets con flujos avanzados
- **Estado**: `tickets`, `selectedTicket`, `myWorkbench`, `statusFilter`, `dateFilter`, `isLoading`, `error`, `epicIdContext`
- **Getters**:
  - `filteredTickets` - Aplica filtros de estado y fecha
  - `overdueTickets`, `inProgressTickets`, `todoTickets`, `completedTickets`, `blockedTickets`
  - `completedCount`, `blockedCount`, `epicProgress`
  - `sortedByDueDate`, `sortedByPriority`
- **Acciones**:
  - `fetchByEpic(epicId)` - Obtiene tickets del épico
  - `fetchMyWorkbench()` - Obtiene workbench personal
  - `create(data)` - Crea ticket
  - `update(id, data)` - Actualiza ticket
  - `remove(id)` - Elimina ticket
  - `moveToEpic(ticketId, newEpicId)` - Drag & drop entre épicos
  - `completeTicket(ticketId, prLink)` - Completa con validación PR
  - `startWorking(ticketId)` - TODO → IN_PROGRESS
  - `raiseQuestion(ticketId, questionText)` - Levanta pregunta/bloqueo (min 10 chars)
  - `resolveQuestion(ticketId)` - Resuelve pregunta
  - `redirectTicket(ticketId, toUserId, reason)` - Redirige con validación (min 10 chars)
  - `selectTicket(ticket)` - Selecciona ticket
  - `getTicketById(id)` - Obtiene por ID
  - `setStatusFilter(filter)` - Filtra por estado
  - `setDateFilter(filter)` - Filtra por fecha
  - `clear()` - Limpia estado

### 5. **analytics.ts** (14 KB)
**Store de Analíticas**
- Gestiona datos de reportes y rendimiento
- **Estado**: `summary`, `performance`, `heatmapData`, `burndownData`, `isLoading`, `error`, `dateRange`, `sortColumn`, `sortDirection`
- **Getters**:
  - `sortedPerformance` - Ordenado por columna+dirección (name, completed, velocity, blockedRate, avgCompletionTime)
  - `topPerformer` - Mejor rendimiento
  - `teamAverageVelocity`, `teamBlockedRate`, `teamAverageCompletionTime`
- **Acciones**:
  - `fetchSummary(appId)` - Resumen de app
  - `fetchPerformance(appId, from, to)` - Rendimiento de usuarios
  - `fetchHeatmap(appId, from, to)` - Mapa de calor de actividad
  - `fetchBurndown(epicId)` - Datos de burndown
  - `setDateRange(from, to)` - Establece rango de fechas
  - `setDateRangeLastDays(days)` - Últimos N días
  - `setSortColumn(column)` - Cambia columna de ordenamiento
  - `setSortDirection(direction)` - Cambia dirección
  - `exportCsv(appId)` - Exporta a CSV
  - `exportPdf(appId)` - Exporta a PDF
  - `clear()` - Limpia estado

### 6. **notifications.ts** (11 KB)
**Store de Notificaciones**
- Gestiona sistema de notificaciones en tiempo real
- **Estado**: `notifications`, `unreadCount`, `isLoading`, `error`, `currentPage`, `totalNotifications`, `pageSize`
- **Getters**:
  - `unreadNotifications` - Notificaciones sin leer
  - `recentNotifications` - Últimas 10
  - `sortedByDate` - Ordenadas por fecha
  - `hasMore` - Indica si hay más para cargar
  - `groupedByDate` - Agrupadas por fecha (Hoy, Ayer, Esta semana, Más antiguas)
  - `getNotificationsByType(type)` - Filtra por tipo
- **Acciones**:
  - `fetch(page, limit)` - Obtiene notificaciones con paginación
  - `fetchUnreadCount()` - Obtiene contador de no leídas
  - `markAsRead(ids)` - Marca como leídas
  - `markAllAsRead()` - Marca todas como leídas
  - `addNotification(notification)` - Agrega desde WebSocket
  - `deleteNotification(id)` - Elimina una
  - `deleteAllRead()` - Elimina todas las leídas
  - `getNotificationById(id)` - Obtiene por ID
  - `loadMore()` - Carga siguiente página
  - `clear()` - Limpia estado

### 7. **team.ts** (13 KB)
**Store de Equipo**
- Gestiona miembros del equipo, roles y asignaciones
- **Estado**: `members`, `unassignedTickets`, `isLoading`, `error`, `showAddModal`, `currentAppId`
- **Getters**:
  - `leaders` - Miembros con rol GROUP_LEADER/ADMIN
  - `developers` - Miembros con rol DEVELOPER
  - `admin` - Admin del grupo
  - `memberCount`, `developerCount`
  - `sortedByName` - Ordenados alfabéticamente
  - `groupedByRole` - Agrupados por rol
  - `unassignedTicketCount` - Cantidad de sin asignar
  - `unassignedSortedByPriority` - Ordenados por prioridad
- **Acciones**:
  - `fetchMembers(appId?)` - Obtiene miembros del equipo
  - `addMember(data)` - Añade nuevo miembro
  - `updateMember(id, data)` - Actualiza miembro
  - `deleteMember(id)` - Elimina miembro
  - `promoteToLeader(userId)` - Promociona a líder
  - `demoteLeader(userId)` - Degrada líder
  - `fetchUnassigned(appId?)` - Obtiene tickets sin asignar
  - `assignTicket(ticketId, userId)` - Asigna ticket
  - `unassignTicket(ticketId)` - Desasigna ticket
  - `getMemberById(id)` - Obtiene por ID
  - `getMemberByEmail(email)` - Obtiene por email
  - `searchMembers(query)` - Busca por nombre/email
  - `openAddModal()` / `closeAddModal()` - Controla modal
  - `clear()` - Limpia estado

## Características Comunes

✅ **TypeScript Completo** - Tipado fuerte en todo el código
✅ **Comentarios en Español** - Documentación muy detallada en español
✅ **Manejo de Errores** - Try/catch en todas las acciones async
✅ **Validaciones** - Validación de datos según especificaciones
✅ **Loading States** - `isLoading` manejado correctamente (true antes, false en finally)
✅ **Error Handling** - Error messages persistidos en estado
✅ **Setup Store Pattern** - Composition API style con ref/computed/function
✅ **API Integration** - Usa `api` service con namespaced methods
✅ **State Persistence** - localStorage donde aplica (auth tokens)

## Patrón de Llamadas API

Todas las tiendas siguen este patrón:

```typescript
const action = async (params) => {
  isLoading.value = true
  error.value = null
  
  try {
    const result = await api.resource.method(params)
    // Actualizar estado local
    return result
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Mensaje genérico'
    error.value = message
    console.error('Error context:', err)
    throw err
  } finally {
    isLoading.value = false
  }
}
```

## Integración con API

Se espera que el servicio `@/services/api` tenga estas namespaces:

- `api.auth` - Login, register, me, refresh, logout, etc.
- `api.applications` - CRUD de aplicaciones
- `api.epics` - CRUD de épicos
- `api.tickets` - CRUD de tickets + operaciones especiales
- `api.analytics` - Obtención de datos analíticos
- `api.notifications` - Gestión de notificaciones
- `api.team` - Gestión de miembros y asignaciones

## Tipado desde @/types

Se requieren las siguientes interfaces TypeScript:

- `User` - Usuario del sistema
- `Application` - Aplicación
- `Epic` - Épico
- `Ticket` - Ticket
- `Subtask` - Subtarea (referencia)
- `Notification` - Notificación
- `UserPerformance` - Datos de rendimiento
- `HeatmapEntry` - Entrada de mapa de calor
- `BurndownData` - Datos de burndown
- `AnalyticsSummary` - Resumen analítico
- `AuthTokens` - Tokens JWT
- `TicketStatus` - Estados de ticket
- `UserRole` - Roles de usuario

## Flujos de Trabajo Típicos

### Autenticación
1. `auth.login()` → almacena tokens → `fetchMe()` → establece `isAuthenticated`
2. En app init: `auth.initialize()` restaura desde localStorage
3. Refrescamiento automático: `refreshToken()` cuando `isTokenExpiringSoon`

### Navegación de Aplicación
1. `applications.fetchAll()` → lista de apps
2. `applications.selectApp()` → selecciona app
3. `epics.fetchByApp()` → carga épicos
4. `tickets.fetchByEpic()` → carga tickets del épico

### Flujo de Ticket
1. Usuario ve lista en workbench: `tickets.fetchMyWorkbench()`
2. Abre ticket: `tickets.selectTicket()`
3. Inicia trabajo: `tickets.startWorking()` (TODO → IN_PROGRESS)
4. Si hay bloqueo: `tickets.raiseQuestion()`
5. Al terminar: `tickets.completeTicket(prLink)` (IN_PROGRESS → COMPLETED)

### Notificaciones en Tiempo Real
1. WebSocket composable escucha eventos
2. Llama `notifications.addNotification()` cuando llega nueva
3. UI actualiza automáticamente desde `unreadNotifications`
4. Usuario hace clic: `notifications.markAsRead()`

---

**Creado**: Marzo 2026
**Framework**: Vue 3 + Pinia + TypeScript
**Patrón**: Setup Stores (Composition API)
