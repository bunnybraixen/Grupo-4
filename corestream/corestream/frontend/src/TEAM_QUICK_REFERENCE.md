# CoreStream Team Management - Guía Rápida de Referencia

## Rutas de Archivos

```
/sessions/stoic-festive-noether/mnt/corestream/corestream/frontend/src/
├── components/team/
│   ├── MemberList.vue              (22 KB) - Tabla de miembros
│   └── AssignmentPanel.vue         (24 KB) - Panel de asignación
├── composables/
│   ├── useWebSocket.ts             (14 KB) - WebSocket tiempo real
│   ├── useTimer.ts                 (11 KB) - Cronómetro
│   └── useDragDrop.ts              (13 KB) - Drag & drop
```

## Importes Rápidos

### Componentes
```typescript
import MemberList from '@/components/team/MemberList.vue'
import AssignmentPanel from '@/components/team/AssignmentPanel.vue'
```

### Composables
```typescript
import { useWebSocket } from '@/composables/useWebSocket'
import { useTimer } from '@/composables/useTimer'
import { useDragDrop } from '@/composables/useDragDrop'
```

---

## Cheat Sheet - MemberList.vue

### Básico
```vue
<template>
  <MemberList @edit="handleEdit" @delete="handleDelete" />
</template>

<script setup lang="ts">
import MemberList from '@/components/team/MemberList.vue'

function handleEdit(userId: string) {
  // Abrir diálogo de edición
}

function handleDelete(userId: string) {
  // Confirmar y eliminar
}
</script>
```

### Características
| Feature | Visible Para | Descripción |
|---------|--------------|-------------|
| Agregar Desarrollador | Admin | Botón + en encabezado |
| Promocionar a Líder | Admin | Ícono corona para devs |
| Degradar de Líder | Admin | Flecha hacia abajo para líderes |
| Editar | Todos | Ícono lápiz |
| Eliminar | Todos | Ícono basura |

### Colores de Avatar
```typescript
Admin      → #DC2626 (Rojo)
Leader     → #D97706 (Oro)
Developer  → #6B7280 (Gris)
```

---

## Cheat Sheet - AssignmentPanel.vue

### Básico
```vue
<template>
  <AssignmentPanel />
</template>

<script setup lang="ts">
import AssignmentPanel from '@/components/team/AssignmentPanel.vue'
// Solo Líderes de Grupo pueden usar este componente
</script>
```

### Validación
- Solo accesible para `role === 'leader'`
- Valida automáticamente en `onMounted`

### Colores de Prioridad
```typescript
low      → bg-green-600   (Baja)
medium   → bg-yellow-600  (Media)
high     → bg-orange-600  (Alta)
critical → bg-red-600     (Crítica)
```

### Colores de Carga
```typescript
1-3 tickets  → bg-green-500   (Carga baja)
4-5 tickets  → bg-yellow-500  (Carga media)
6+ tickets   → bg-red-500     (Carga alta)
```

---

## Cheat Sheet - useWebSocket.ts

### Conectar
```typescript
const { isConnected, connect, disconnect, send } = useWebSocket()

onMounted(() => {
  connect('user-id-123')
})

onUnmounted(() => {
  disconnect()
})
```

### Enviar Mensaje
```typescript
// Mensaje personalizado
send({
  type: 'custom-action',
  payload: { /* datos */ }
})

// Automático: heartbeat cada 30s
```

### Monitorear Conexión
```typescript
watch(isConnected, (connected) => {
  if (connected) {
    console.log('Conectado')
  } else {
    console.log('Desconectado')
  }
})

// Ver intentos de reconexión
console.log(reconnectAttempts.value)
```

### Tipos de Mensajes
```typescript
'notification'  // Notificación para el usuario
'update'        // Actualización de datos en tiempo real
'error'         // Mensaje de error
'ping'          // Heartbeat del cliente
'pong'          // Respuesta del servidor
```

---

## Cheat Sheet - useTimer.ts

### Básico
```typescript
const { elapsed, formatted, start, pause, resume, stop, reset } = useTimer()

// Iniciar
start()

// Ver tiempo
console.log(formatted.value) // "00:01:30"
console.log(elapsed.value)   // 90

// Pausar cuando se bloquea
pause()

// Reanudar
resume()

// Finalizar
const totalSeconds = stop() // 90
```

### Estados
```typescript
isRunning.value  // true = contando, false = parado
isPaused.value   // true = pausado, false = normal
```

### Inicializar con Valor
```typescript
const { formatted } = useTimer(3600) // Comienza en 1:00:00
```

### Watch del Tiempo
```typescript
watch(formatted, (newTime) => {
  console.log(`Tiempo: ${newTime}`)
})
```

---

## Cheat Sheet - useDragDrop.ts

### Básico en Template
```vue
<div
  draggable="true"
  @dragstart="dragStart(epic, 'epic')"
  @dragover="dragOver($event, epic.id)"
  @drop="handleDrop($event, epic.id, 'epic')"
  @dragend="dragEnd"
  :class="getDragClasses(epic.id)"
>
  {{ epic.name }}
</div>

<script setup lang="ts">
const { dragStart, dragOver, drop, dragEnd, getDragClasses } = useDragDrop()

function handleDrop(e: DragEvent, targetId: string, type: string) {
  const result = drop(e, targetId, type)
  if (result) {
    // Procesar drop válido
    console.log(`${result.type} movido a ${result.targetId}`)
  }
}
</script>
```

### Validación de Drops
```typescript
// VÁLIDO
epic → soltar sobre → epic (reorden)
ticket → soltar sobre → epic (cambio de grupo)

// INVÁLIDO
epic → soltar sobre → ticket
ticket → soltar sobre → ticket
elemento → soltar sobre → elemento mismo
```

### Obtener Información
```typescript
const info = getDragInfo()
// { isDragging, dragItem, dragType, dragOverTarget, dragData }

// Cancelar arrastre
cancelDrag()
```

### Clases CSS de Feedback
```typescript
// Elemento siendo arrastrado
'opacity-50 bg-gray-200 cursor-move'

// Zona de drop válida
'border-2 border-blue-400 bg-blue-50'

// Zona de drop inválida
'border-2 border-red-400 bg-red-50'
```

---

## Stores Requeridos

### useTeamStore
```typescript
// Propiedades
members: TeamMember[]

// Métodos
fetchMembers()
addMember(data)
promoteToLeader(userId)
demoteFromLeader(userId)
```

### useTicketsStore
```typescript
// Propiedades
tickets: Ticket[]

// Métodos
fetchTickets()
assignTicket(ticketId, developerId)
unassignTicket(ticketId)
```

### useAuthStore
```typescript
// Propiedades
currentUser: { role: 'admin' | 'leader' | 'developer' }

// Métodos
login()
logout()
```

### useNotificationStore
```typescript
// Métodos
addNotification(notification)
clearNotification(id)
```

---

## Interfaces TypeScript Principales

### TeamMember
```typescript
{
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
```

### Ticket
```typescript
{
  id: string
  title: string
  epicName?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  dueDate: string
  assignedTo?: string
}
```

### Notification
```typescript
{
  id: string
  title: string
  message: string
  type: 'info' | 'success' | 'warning' | 'error'
  timestamp: string
  read: boolean
}
```

---

## Tips y Trucos

### Performance
- useTimer usa requestAnimationFrame (muy eficiente)
- Computed properties se cachean automáticamente
- WebSocket solo envía heartbeat mínimo necesario

### Debugging
```typescript
// WebSocket
const { isDragging, dragItem, dragType, dragOverTarget } = useDragDrop()
console.log(getDragInfo())

// Timer
console.log(`${formatted.value} | ${elapsed.value}s`)

// Team
console.log(members.value, teamStore.members)
```

### Patrones Comunes

#### Validación de Admin
```typescript
const isAdmin = computed(() => authStore.currentUser?.role === 'admin')
if (isAdmin.value) { /* mostrar */ }
```

#### Búsqueda Reactiva
```typescript
const query = ref('')
const filtered = computed(() => {
  return items.filter(item => 
    item.name.toLowerCase().includes(query.value.toLowerCase())
  )
})
```

#### Watch de Cambios
```typescript
watch(selectedTicket, async (newTicket) => {
  if (newTicket) {
    await assignTicket(newTicket.id)
  }
}, { deep: true })
```

---

## Errores Comunes

### ❌ WebSocket
```typescript
// MAL: No desconectar
const { connect } = useWebSocket()
onMounted(() => connect('user'))
// Falta onUnmounted(() => disconnect())

// BIEN
onUnmounted(() => disconnect())
```

### ❌ Timer
```typescript
// MAL: No resetear después de stop
const total = stop()
// elapsed aún tiene valor

// BIEN: Resetear para siguiente uso
const total = stop()
reset() // Ahora elapsed = 0
```

### ❌ DragDrop
```typescript
// MAL: No prevenir comportamiento por defecto
@dragover="dragOver($event, id)"
// function dragOver(e, id) { dragOverTarget = id }

// BIEN: Prevenir default
function dragOver(e: DragEvent, targetId: string) {
  e.preventDefault() // IMPORTANTE
  dragOverTarget.value = targetId
}
```

---

## Generado por Claude Opus 4.6
**Fecha:** 2 de marzo, 2026
**Versión:** 1.0.0

Consultar TEAM_COMPONENTS_README.md para documentación completa.
