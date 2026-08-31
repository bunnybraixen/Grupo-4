<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Panel Lateral de Ticket (Lado Derecho) -->
  <!-- ================================================================ -->
  <!-- Panel deslizable desde la derecha que muestra detalles del ticket -->
  <!-- Incluye: encabezado con timer, descripción, subtareas, actividad -->
  <!-- Footer con acciones: Completar, Levantar Pregunta, Redireccionar -->
  <!-- ================================================================ -->

  <Transition name="slide-right">
    <div
      v-if="isOpen"
      class="fixed inset-y-0 right-0 w-2/5 bg-slate-800 shadow-2xl overflow-hidden flex flex-col z-40"
    >
      <!-- ================================================================ -->
      <!-- SECCIÓN: Encabezado (Sticky) -->
      <!-- ================================================================ -->
      <!-- Breadcrumbs, título, asignado y timer -->
      <!-- ================================================================ -->
      <div class="flex-shrink-0 p-6 border-b border-slate-700 space-y-3">
        <!-- Botón cerrar en esquina superior derecha -->
        <div class="absolute top-4 right-4">
          <button
            @click="$emit('close')"
            class="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
            aria-label="Cerrar panel"
          >
            <Icon icon="mdi:close" class="text-xl" />
          </button>
        </div>

        <!-- Breadcrumbs: Aplicación > Épica > Ticket -->
        <div class="flex items-center gap-1 text-xs text-slate-400">
          <span>{{ ticket.appName }}</span>
          <Icon icon="mdi:chevron-right" class="inline" />
          <span>{{ ticket.epicName }}</span>
          <Icon icon="mdi:chevron-right" class="inline" />
          <span class="text-blue-400 font-semibold">T-{{ ticket.id }}</span>
        </div>

        <!-- Título principal del ticket -->
        <h1 class="text-2xl font-bold text-white pr-8">
          {{ ticket.title }}
        </h1>

        <!-- Fila de meta-información -->
        <div class="flex items-center gap-3 pt-2">
          <!-- Avatar del asignado -->
          <div
            v-if="ticket.assignee"
            class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold bg-blue-600 text-white"
            :title="ticket.assignee.name"
          >
            {{ getInitials(ticket.assignee.name) }}
          </div>

          <!-- Nombre del asignado -->
          <span class="text-sm text-slate-300">
            {{ ticket.assignee?.name || 'Sin asignar' }}
          </span>

          <!-- Espaciador -->
          <div class="flex-1" />

          <!-- Timer de ejecución -->
          <TimerDisplay
            :seconds="elapsedSeconds"
            :is-running="ticket.status === 'IN_PROGRESS' && !isBlocked"
            :is-paused="isBlocked"
          />
        </div>
      </div>

      <!-- ================================================================ -->
      <!-- SECCIÓN: Contenido Principal (Scrollable) -->
      <!-- ================================================================ -->
      <!-- Descripción, subtareas, y log de actividad -->
      <!-- ================================================================ -->
      <div class="flex-1 overflow-y-auto">
        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Descripción -->
        <!-- ================================================================ -->
        <div class="p-6 border-b border-slate-700">
          <h3 class="text-sm font-semibold text-white mb-3">Descripción</h3>
          <div class="text-sm text-slate-300 whitespace-pre-wrap">
            {{ ticket.description || 'Sin descripción' }}
          </div>
        </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Subtareas -->
        <!-- ================================================================ -->
        <div class="p-6 border-b border-slate-700">
          <SubtaskChecklist
            :subtasks="ticket.subtasks || []"
            :ticket-id="ticket.id"
            @update="handleSubtaskUpdate"
            @create="handleSubtaskCreate"
            @delete="handleSubtaskDelete"
          />
        </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Log de Actividad -->
        <!-- ================================================================ -->
        <div class="p-6">
          <h3 class="text-sm font-semibold text-white mb-3">Actividad</h3>
          <ActivityLog :events="ticket.events || []" />
        </div>
      </div>

      <!-- ================================================================ -->
      <!-- SECCIÓN: Footer con Acciones (Sticky) -->
      <!-- ================================================================ -->
      <!-- Componente ActionDock con botones principales -->
      <!-- ================================================================ -->
      <div class="flex-shrink-0 border-t border-slate-700 bg-slate-750">
        <ActionDock
          :ticket="ticket"
          @complete="handleComplete"
          @question="handleQuestion"
          @redirect="handleRedirect"
          @resolve="handleResolve"
        />
      </div>

      <!-- ================================================================ -->
      <!-- ANIMACIÓN: Confetti (oculto) -->
      <!-- ================================================================ -->
      <ConfettiAnimation ref="confettiRef" />
    </div>
  </Transition>

  <!-- Overlay oscuro detrás del panel -->
  <Transition name="fade">
    <div
      v-if="isOpen"
      @click="$emit('close')"
      class="fixed inset-0 bg-black bg-opacity-50 z-30"
    />
  </Transition>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import TimerDisplay from '@/components/shared/TimerDisplay.vue'
import SubtaskChecklist from './SubtaskChecklist.vue'
import ActivityLog from './ActivityLog.vue'
import ActionDock from './ActionDock.vue'
import ConfettiAnimation from '@/components/shared/ConfettiAnimation.vue'
import { useTimer } from '@/composables/useTimer'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Assignee {
  id: string
  name: string
  avatar: string
}

interface Subtask {
  id: string
  title: string
  completed: boolean
}

interface TicketEvent {
  id: string
  type: string
  timestamp: string
  user: Assignee
  description: string
}

interface Ticket {
  id: string
  title: string
  description?: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
  appName: string
  epicName: string
  assignee?: Assignee
  subtasks?: Subtask[]
  events?: TicketEvent[]
  createdAt: string
}

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  ticket: Ticket
  isOpen: boolean
}

const props = defineProps<Props>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Referencia al componente de confetti para animación
const confettiRef = ref()

// Composable para manejar el timer
const { seconds: elapsedSeconds, start, pause, stop } = useTimer()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Determina si el ticket está bloqueado
 */
const isBlocked = computed(() => props.ticket.status === 'BLOCKED')

// =====================================================================
// WATCHERS
// =====================================================================

/**
 * Observa cambios en el estado del ticket
 * Inicia, pausa o detiene el timer según corresponda
 */
watch(
  () => props.ticket.status,
  (newStatus) => {
    if (newStatus === 'IN_PROGRESS') {
      start()
    } else if (newStatus === 'BLOCKED') {
      pause()
    } else if (newStatus === 'DONE') {
      stop()
    }
  },
  { immediate: true }
)

/**
 * Observa si el panel se abre o cierra
 * Inicia el timer cuando se abre si el ticket está en progreso
 */
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen && props.ticket.status === 'IN_PROGRESS') {
      start()
    } else if (!isOpen) {
      pause()
    }
  }
)

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Obtiene iniciales de un nombre
 */
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// =====================================================================
// MANEJADORES DE EVENTOS
// =====================================================================

/**
 * Maneja completación del ticket
 * Emite evento con datos de PR
 */
const handleComplete = (prUrl: string) => {
  // Disparar animación de confetti
  confettiRef.value?.fireConfetti()

  // Emitir evento
  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'complete',
    data: { prUrl }
  })
}

/**
 * Maneja levantamiento de pregunta
 * Bloquea el ticket y pausa el timer
 */
const handleQuestion = (question: string) => {
  pause()

  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'question',
    data: { question }
  })
}

/**
 * Maneja redirección de ticket
 * Cambia asignado y pausa timer
 */
const handleRedirect = (data: { toUserId: string; reason: string }) => {
  pause()

  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'redirect',
    data
  })
}

/**
 * Maneja resolución de pregunta
 * Reanuda el timer
 */
const handleResolve = (resolution: string) => {
  start()

  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'resolve',
    data: { resolution }
  })
}

/**
 * Maneja actualización de subtarea
 */
const handleSubtaskUpdate = (subtask: Subtask) => {
  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'updateSubtask',
    data: { subtask }
  })
}

/**
 * Maneja creación de nueva subtarea
 */
const handleSubtaskCreate = (title: string) => {
  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'createSubtask',
    data: { title }
  })
}

/**
 * Maneja eliminación de subtarea
 */
const handleSubtaskDelete = (subtaskId: string) => {
  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'deleteSubtask',
    data: { subtaskId }
  })
}

// =====================================================================
// EMITS
// =====================================================================

const emit = defineEmits<{
  close: []
  ticketUpdated: [data: any]
}>()
</script>

<style scoped>
/* ================================================================ */
/* TRANSICIONES */
/* ================================================================ */

/* Transición de panel deslizable desde la derecha */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}

/* Transición de fade para overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
