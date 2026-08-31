# CoreStream Team Management - Componentes y Composables

## Descripción General

Este documento describe los componentes Vue 3 y composables desarrollados para el módulo de gestión de equipos de CoreStream. Todos los archivos incluyen comentarios muy detallados en español, utilizan Composition API con script setup, TypeScript y Tailwind CSS.

**Base Path:** `/sessions/stoic-festive-noether/mnt/corestream/corestream/frontend/src/`

---

## Componentes Vue 3

### 1. MemberList.vue
**Ubicación:** `components/team/MemberList.vue` (22 KB)

#### Descripción
Componente principal para la gestión de miembros del equipo. Muestra una tabla completa de miembros con funcionalidades administrativas.

#### Características Principales
- **Tabla de miembros**: Lista completa con 6 columnas
  - Avatar: Círculo con iniciales, color según rol (Admin=Rojo, Leader=Oro, Dev=Gris)
  - Nombre + Email: Información de contacto
  - Rol: Badge coloreado (Administrador, Líder de Grupo, Desarrollador)
  - Especialidad: Campo técnico (Frontend, Backend, etc.)
  - Estadísticas: 4 mini-números con fondo coloreado
    - Completadas (verde)
    - Pendientes (amarillo)
    - Bloqueadas (rojo)
    - Tiempo promedio (azul)

- **Búsqueda y filtrado**
  - Input de búsqueda en tiempo real
  - Filtra por nombre o email (case-insensitive)

- **Acciones administrativas**
  - Botón "Promocionar a Líder" (solo para admins visualizando devs)
  - Botón "Degradar de Líder" (solo para admins visualizando líderes)
  - Botón "Editar" (ícono lápiz)
  - Botón "Eliminar" (ícono basura)

- **Modal de agregar miembro**
  - Formulario con campos: Nombre, Email, Especialidad
  - Solo visible para administradores

- **Estados visuales**
  - Tabla con hover effects
  - Estado vacío cuando no hay miembros
  - Contador de resultados en búsqueda

#### Interfaces TypeScript
```typescript
interface TeamMember {
  id: string
  name: string
  email: string
  role: 'admin' | 'leader' | 'developer'
  specialty?: string
  stats: {
    completed: number
    pending: number
    blocked: number
    avgTime: number
  }
}

interface NewMemberForm {
  name: string
  email: string
  specialty: string
}
```

#### Emits
```typescript
emit('edit', userId: string)    // Cuando se edita un miembro
emit('delete', userId: string)  // Cuando se elimina un miembro
```

#### Stores Utilizados
- `useTeamStore`: Gestiona lista de miembros y operaciones
- `useAuthStore`: Verifica permisos de administrador

#### Métodos Principales
- `getInitials(name)`: Obtiene iniciales (Juan Pérez → JP)
- `getAvatarColor(role)`: Color hexadecimal según rol
- `getRoleBadgeClass(role)`: Clases CSS del badge
- `getRoleLabel(role)`: Etiqueta en español del rol
- `handlePromote(userId)`: Promociona a líder
- `handleDemote(userId)`: Degrada de líder
- `handleEdit(userId)`: Emite evento de edición
- `handleDelete(userId)`: Emite evento de eliminación
- `handleAddMember()`: Crea nuevo miembro

---

### 2. AssignmentPanel.vue
**Ubicación:** `components/team/AssignmentPanel.vue` (24 KB)

#### Descripción
Panel exclusivo para Líderes de Grupo. Proporciona interfaz de distribución de tickets con vista de carga de trabajo.

#### Características Principales
- **Diseño de dos paneles**
  - Panel izquierdo (50%): Tickets sin asignar
  - Panel derecho (50%): Carga por desarrollador

- **Panel izquierdo - Tickets Sin Asignar**
  - Tarjetas de tickets con:
    - Título
    - Badge de prioridad (Baja=verde, Media=amarillo, Alta=naranja, Crítica=rojo)
    - Nombre de épica asociada
    - Fecha de vencimiento (formato: "15 de mar, 2026")
  - Botón "Asignar Ticket" en cada tarjeta
  - Estado vacío cuando no hay tickets
  - Contador de tickets disponibles

- **Panel derecho - Carga por Desarrollador**
  - Secciones por desarrollador con:
    - Avatar + nombre
    - Contador de tickets asignados
    - **Barra de carga coloreada:**
      - 1-3 tickets: Verde (carga baja)
      - 4-5 tickets: Amarillo (carga media)
      - 6+ tickets: Rojo (carga alta)
    - Lista de tickets asignados
    - Botón X para desasignar cada ticket

- **Modal de asignación**
  - Título: "Asignar Ticket"
  - Muestra ticket a asignar
  - Lista de desarrolladores con:
    - Avatar + nombre
    - Contador de tickets actual
    - Barra de carga miniatura
  - Click en desarrollador asigna el ticket

#### Interfaces TypeScript
```typescript
interface Ticket {
  id: string
  title: string
  epicName?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  dueDate: string
  assignedTo?: string
}

interface Developer {
  id: string
  name: string
  assignedTickets: Ticket[]
}
```

#### Stores Utilizados
- `useTeamStore`: Datos de desarrolladores
- `useTicketsStore`: Datos de tickets y operaciones
- `useAuthStore`: Validación de líder de grupo

#### Propiedades Computadas Principales
- `unassignedTickets`: Tickets sin asignar
- `developerWorkload`: Desarrolladores con sus tickets
- `availableDevelopers`: Lista de desarrolladores para asignación

#### Métodos Principales
- `getInitials(name)`: Iniciales del nombre
- `getPriorityBadgeClass(priority)`: Clases del badge
- `getPriorityLabel(priority)`: Etiqueta en español
- `getWorkloadBarColor(count)`: Color según carga
- `formatDate(dateString)`: Formato español de fecha
- `openAssignmentModal(ticket)`: Abre modal
- `closeAssignmentModal()`: Cierra modal
- `assignTicket(developerId)`: Asigna ticket
- `handleUnassign(ticketId, developerId)`: Desasigna ticket

#### Validación
- Solo líderes de grupo pueden acceder (validación en onMounted)
- No permite soltar sobre el mismo elemento

---

## Composables (Hooks)

### 3. useWebSocket.ts
**Ubicación:** `composables/useWebSocket.ts` (14 KB)

#### Descripción
Composable para gestionar conexiones WebSocket en tiempo real con notificaciones push desde FastAPI.

#### Características Principales
- **Conexión automática**
  - URL: `ws://{host}/api/ws/notifications/{userId}`
  - Protocolo automático (ws/wss según HTTPS)

- **Heartbeat automático**
  - Ping cada 30 segundos
  - Mantiene conexión viva contra timeout del servidor

- **Reconexión automática**
  - Backoff exponencial: delay = baseDelay × 2^intentos
  - Máximo: 10 intentos de reconexión
  - Retraso máximo: 30 segundos

- **Procesamiento de mensajes**
  - Tipos: 'notification', 'update', 'error', 'ping', 'pong'
  - Parseo automático JSON
  - Integración con notificationStore

- **Gestión de errores**
  - Logging detallado
  - Notificaciones de error al usuario
  - Validación de conexión antes de enviar

#### Interfaces TypeScript
```typescript
interface WebSocketMessage {
  type: 'notification' | 'update' | 'error' | 'ping' | 'pong'
  data?: any
  message?: string
  timestamp?: string
}
```

#### Propiedades Reactivas
```typescript
isConnected: Ref<boolean>        // Estado de conexión
reconnectAttempts: Ref<number>   // Número de intentos
```

#### Métodos Públicos
```typescript
connect(userId: string): void    // Conectar al servidor
disconnect(): void               // Desconectar
send(data: any): void           // Enviar mensaje
```

#### Constantes de Configuración
```
maxReconnectAttempts = 10        // Máximo de reconexiones
baseDelay = 1000                 // 1 segundo base
maxDelay = 30000                 // 30 segundos máximo
heartbeatInterval = 30000        // 30 segundos entre pings
```

#### Ejemplo de Uso
```typescript
const { isConnected, connect, disconnect, send } = useWebSocket()

onMounted(() => {
  connect('user-id-123')
})

// Enviar mensaje personalizado
send({
  type: 'custom-action',
  payload: { /* ... */ }
})

// Desconectar al desmontar
onUnmounted(() => {
  disconnect()
})
```

#### Flujo de Mensajes
1. Cliente conecta → servidor envía bienvenida
2. Cliente envía ping cada 30s
3. Servidor responde con pong
4. Servidor envía notificaciones → cliente procesa
5. Cliente desconecta → intenta reconectar con backoff

---

### 4. useTimer.ts
**Ubicación:** `composables/useTimer.ts` (11 KB)

#### Descripción
Composable de cronómetro reactivo para tracking de tiempo en tickets. Usa requestAnimationFrame para precisión y rendimiento.

#### Características Principales
- **Precisión de timestamp**
  - Basado en performance.now()
  - Delta de tiempo en cada frame (~60fps)
  - Acumulación precisa sin deriva

- **Estados del cronómetro**
  - Running: Contando tiempo
  - Paused: Tiempo acumulado pero detenido
  - Stopped: Finalizado

- **Formato automático**
  - Propiedad `formatted` devuelve "HH:MM:SS"
  - Actualización reactiva automática
  - Ejemplo: 3665 segundos → "01:01:05"

- **Operaciones de pausa**
  - Pausa cuando ticket se bloquea
  - Reanudación sin pérdida de tiempo
  - Ideal para tracking condicional

- **Limpieza automática**
  - Cancela requestAnimationFrame
  - Previene memory leaks
  - Cleanup en onUnmounted

#### Propiedades Reactivas
```typescript
elapsed: Ref<number>           // Segundos transcurridos (decimal)
isRunning: Ref<boolean>        // true = contando
isPaused: Ref<boolean>         // true = pausado
formatted: ComputedRef<string> // "HH:MM:SS"
```

#### Métodos Públicos
```typescript
start(): void      // Inicia o continúa desde pausa
pause(): void      // Pausa tiempo actual
resume(): void     // Reanuda desde pausa
stop(): number     // Detiene y retorna segundos totales
reset(): void      // Reinicia a cero
```

#### Ejemplo de Uso
```typescript
const { elapsed, formatted, start, pause, resume, stop } = useTimer(0)

// Iniciar cronómetro
start()

// Cuando ticket se bloquea
pause()

// Cuando se desbloquea
resume()

// Obtener tiempo final
const totalSeconds = stop()

// Ver tiempo formateado
console.log(formatted.value) // "00:15:30"
```

#### Máquina de Estados
```
IDLE ─start→ RUNNING ─pause→ PAUSED
                ↑              ↓
                └─resume───────┘

RUNNING ─stop→ STOPPED (valor guardado, estado limpio)
```

---

### 5. useDragDrop.ts
**Ubicación:** `composables/useDragDrop.ts` (13 KB)

#### Descripción
Composable para funcionalidad de Drag & Drop. Gestiona arrastres de épicas y tickets con feedback visual en tiempo real.

#### Características Principales
- **Soporte para dos tipos de items**
  - Épicas: Pueden ser reordenadas dentro del área de épicas
  - Tickets: Pueden moverse entre épicas

- **Validación de drops**
  - Épica solo puede soltarse en épica (reorden)
  - Ticket solo puede soltarse en épica (cambio de grupo)
  - Previene drop sobre el mismo elemento

- **Feedback visual dinámico**
  - Elemento arrastrado: Opacidad reducida
  - Zona de drop: Borde azul y fondo azul claro
  - Animaciones suaves con transiciones

- **Gestión de eventos**
  - dragstart: Inicia arrastre
  - dragover: Detecta zona sobre la cual se arrastra
  - drop: Completa el arrastre
  - dragend: Limpia estado

- **Prevención de comportamiento por defecto**
  - Evita que navegador maneje el drop
  - Permite operaciones personalizadas

#### Interfaces TypeScript
```typescript
interface DraggableItem {
  id: string
  [key: string]: any
}

interface DropResult {
  item: DraggableItem
  type: 'epic' | 'ticket'
  targetId: string
}
```

#### Propiedades Reactivas
```typescript
isDragging: Ref<boolean>           // Hay arrastre en progreso
dragItem: Ref<DraggableItem | null> // Item siendo arrastrado
dragType: Ref<'epic' | 'ticket' | null> // Tipo del item
dragOverTarget: Ref<string | null> // ID del destino actual
```

#### Métodos Públicos
```typescript
dragStart(item, type): void              // Inicia arrastre
dragEnd(): void                          // Finaliza y limpia
dragOver(e, targetId): void             // Maneja dragover
drop(e, targetId, targetType): DropResult | null  // Completa drop
getDragClasses(elementId): string       // Clases CSS para feedback
getDragInfo(): object                   // Info del estado actual
cancelDrag(): void                      // Cancela sin completar
```

#### Clases CSS de Feedback
```typescript
DRAGGING_CLASS = 'opacity-50 bg-gray-200 cursor-move'
DROP_ZONE_CLASS = 'border-2 border-blue-400 bg-blue-50'
DROP_DELETE_CLASS = 'border-2 border-red-400 bg-red-50'
```

#### Ejemplo de Uso en Template
```vue
<div
  draggable="true"
  @dragstart="dragStart(epic, 'epic')"
  @dragover="dragOver($event, epic.id)"
  @drop="drop($event, epic.id, 'epic')"
  @dragend="dragEnd"
  :class="getDragClasses(epic.id)"
>
  <!-- Contenido -->
</div>
```

#### Flujo de Operación
```
1. dragStart(item, 'epic')
   ↓ Establece dragItem, dragType
   
2. dragOver($event, targetId)
   ↓ Actualiza dragOverTarget
   ↓ Aplica clases visuales con getDragClasses()
   
3. drop($event, targetId, 'epic')
   ↓ Valida compatibilidad de tipos
   ↓ Retorna DropResult o null
   ↓ Componente padre maneja la operación
   
4. dragEnd()
   ↓ Limpia todo el estado
```

---

## Estructura de Directorios

```
/sessions/stoic-festive-noether/mnt/corestream/corestream/frontend/src/
├── components/
│   └── team/
│       ├── MemberList.vue (22 KB)
│       └── AssignmentPanel.vue (24 KB)
│
├── composables/
│   ├── useWebSocket.ts (14 KB)
│   ├── useTimer.ts (11 KB)
│   └── useDragDrop.ts (13 KB)
│
├── stores/
│   ├── team.ts (debe existir o crear)
│   ├── tickets.ts (debe existir o crear)
│   ├── auth.ts (debe existir o crear)
│   └── notifications.ts (debe existir o crear)
│
└── TEAM_COMPONENTS_README.md (este archivo)
```

---

## Dependencias y Requisitos

### Vue 3
- Composition API (script setup)
- Reactivity API (ref, computed, onMounted, onUnmounted)

### TypeScript
- Interfaces para type safety
- Tipos genéricos para composables

### Tailwind CSS
- Clases para styling completamente responsivo
- Grid, flexbox, transiciones, estados hover

### Pinia (Stores)
Deben implementarse los siguientes stores:

#### useTeamStore
```typescript
interface TeamMember {
  id: string
  name: string
  email: string
  role: 'admin' | 'leader' | 'developer'
  specialty?: string
  stats: { completed, pending, blocked, avgTime }
}

// Acciones requeridas
members: TeamMember[]
fetchMembers(): Promise<void>
addMember(member): Promise<void>
promoteToLeader(userId): Promise<void>
demoteFromLeader(userId): Promise<void>
```

#### useTicketsStore
```typescript
// Acciones requeridas
tickets: Ticket[]
fetchTickets(): Promise<void>
assignTicket(ticketId, developerId): Promise<void>
unassignTicket(ticketId): Promise<void>
```

#### useAuthStore
```typescript
currentUser?: { role: 'admin' | 'leader' | 'developer' }
// Métodos para autenticación
```

#### useNotificationStore
```typescript
// Acciones requeridas
addNotification(notification): void
// Estructura de notificación:
// { id, title, message, type, timestamp, read }
```

---

## Características de Diseño

### Paleta de Colores
- **Primario:** Azul (#3B82F6)
- **Éxito:** Verde (#10B981)
- **Advertencia:** Amarillo (#F59E0B)
- **Error:** Rojo (#EF4444)
- **Información:** Azul claro (#0EA5E9)

### Tipografía
- Fuentes: Sistema nativo (sans-serif)
- Escalas: Text-xs, text-sm, text-base, text-lg, text-xl, text-2xl
- Pesos: Regular (400), Semibold (600), Bold (700)

### Espaciado
- Gap/padding: 4px (p-1), 8px (p-2), 16px (p-4), 24px (p-6)
- Breakpoints responsive: sm, md, lg, xl, 2xl

### Animaciones
- Transiciones: 200ms ease-in-out
- Hover effects en botones y enlaces
- Cambios suaves de opacidad y color

---

## Patrones de Desarrollo

### Composables
1. Importar reactive utilities de Vue
2. Definir interfaces TypeScript
3. Inicializar estado reactivo (ref, computed)
4. Implementar métodos públicos
5. Agregar cleanup en onUnmounted
6. Retornar objeto con API pública

### Componentes
1. Template con v-if, v-for, event bindings
2. Comentarios HTML en español muy detallados
3. Script setup con imports necesarios
4. Definir interfaces para datos
5. Emits explícitos con tipos
6. Props computadas para datos derivados
7. Métodos para acciones
8. Scoped styles con transiciones

### Stores (Pinia)
Consultar documentación existente del proyecto para estructura.

---

## Testing Recomendado

### Tests Unitarios (Jest/Vitest)
- useTimer: start, pause, resume, stop, formatted
- useDragDrop: dragStart, drop validation, getDragClasses
- useWebSocket: connect/disconnect, message parsing

### Tests de Componentes (Vitest + Vue Test Utils)
- MemberList: Rendering, búsqueda, emits
- AssignmentPanel: Carga de desarrolladores, asignación

### Tests E2E (Cypress/Playwright)
- Flujo completo de asignación de tickets
- Drag & drop de épicas
- Conexión WebSocket en tiempo real

---

## Notas de Implementación

### Seguridad
- Validar IDs antes de operaciones
- Verificar permisos en backend
- Sanitizar inputs de usuario
- CORS configurado correctamente para WebSocket

### Rendimiento
- Timer usa requestAnimationFrame (eficiente)
- WebSocket solo envía heartbeat necesario
- Computed properties para datos derivados
- Scroll virtualization si lista es muy grande

### Accesibilidad
- ARIA labels en botones de acción
- Keyboard navigation soportada
- Contraste de colores WCAG AA
- Texto alternativo para iconos

### Mantenibilidad
- Comentarios en español muy detallados
- Nombres descriptivos de variables
- Interfaces TypeScript bien estructuradas
- Funciones pequeñas y reutilizables

---

## Autor y Fecha

**Generado por:** Claude Opus 4.6 (Anthropic)
**Fecha:** 2 de marzo, 2026
**Versión:** 1.0.0

---

## Licencia

Estos componentes y composables son parte del proyecto CoreStream.
Consultar licencia del proyecto principal para términos de uso.
