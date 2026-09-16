<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Log de Actividad -->
  <!-- ================================================================ -->
  <!-- Historial cronológico de eventos del ticket -->
  <!-- Eventos: creación, asignación, cambios de estado, preguntas, etc. -->
  <!-- Cada evento muestra: ícono, timestamp, usuario, descripción -->
  <!-- ================================================================ -->

  <div class="space-y-4">
    <!-- ================================================================ -->
    <!-- ENCABEZADO -->
    <!-- ================================================================ -->
    <h4 class="text-sm font-semibold text-[var(--text-primary)]">{{ t('activityLog.title') }}</h4>

    <!-- ================================================================ -->
    <!-- LISTA DE EVENTOS -->
    <!-- ================================================================ -->
    <!-- Renderiza cada evento en orden cronológico inverso -->
    <!-- ================================================================ -->
    <div v-if="events.length === 0" class="text-center py-6 text-[var(--text-muted)]">
      <Icon icon="mdi:history" class="text-2xl mx-auto mb-1" />
      <p class="text-sm">{{ t('activityLog.noEvents') }}</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="event in events"
        :key="event.id"
        class="flex gap-3"
      >
        <!-- ================================================================ -->
        <!-- ELEMENTO: Ícono del Evento -->
        <!-- ================================================================ -->
        <!-- Color y tipo depende del tipo de evento -->
        <!-- ================================================================ -->
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1',
            getEventIconColor(event.event_type)
          ]"
        >
          <Icon :icon="getEventIcon(event.event_type)" class="text-sm" />
        </div>

        <!-- ================================================================ -->
        <!-- ELEMENTO: Contenedor de Información -->
        <!-- ================================================================ -->
        <div class="flex-1 min-w-0">
          <!-- Timestamp y Tipo de Evento -->
          <div class="flex items-start justify-between gap-2 mb-1">
            <p class="text-sm font-medium text-[var(--text-primary)]">
              {{ getEventTypeLabel(event.event_type) }}
            </p>
            <span class="text-xs text-[var(--text-muted)] flex-shrink-0">
              {{ formatTime(event.created_at) }}
            </span>
          </div>

          <!-- Usuario y Descripción -->
          <div
            class="text-xs text-[var(--text-muted)] mb-1">
            <span class="font-semibold text-[var(--text-secondary)]">{{ event.user?.full_name || event.user?.name || 'Sistema' }}</span>
            
            <span 
              v-if="event.detail?.description || event.detail?.message">
              - {{ event.detail?.description || event.detail?.message }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - REDIRECCIÓN -->
          <!-- ================================================================ -->
          <!-- Muestra flujo: Avatar A -> flecha -> Avatar B -->
          <!-- ================================================================ -->
          <div
            v-if="event.event_type === 'REDIRECTED'" class="flex items-center gap-2 mt-2">
            <!-- Avatar usuario origen -->
            <div
              class="w-6 h-6 rounded-full bg-[var(--teal)] flex items-center justify-center text-xs font-bold text-[var(--text-primary)] flex-shrink-0"
              :title="event.from_user?.full_name"
            >
              {{ getInitials(event.from_user?.full_name || 'U') }}
            </div>

            <Icon icon="mdi:arrow-right" class="text-[var(--text-muted)]" />

            <!-- Avatar usuario destino -->
            <div
              class="w-6 h-6 rounded-full bg-[var(--status-done-bg)] flex items-center justify-center text-xs font-bold text-[var(--text-primary)] flex-shrink-0"
              :title="event.to_user?.full_name"
            >
              {{ getInitials(event.to_user?.full_name || 'U') }}
            </div>

            <!-- Razón de redirección -->
            <span
              v-if="event.detail?.reason" class="text-xs text-[var(--text-muted)] ml-2 italic">
              "{{ event.detail.reason }}"
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - PREGUNTA LEVANTADA -->
          <!-- ================================================================ -->
          <!-- Muestra la pregunta en un cuadro ámbar -->
          <!-- ================================================================ -->
          <div
            v-if="event.event_type === 'QUESTION_RAISED' && event.detail?.question"
            class="mt-2 p-2 bg-amber-900/30 border border-amber-700/50 rounded-lg text-xs text-amber-100">
            <Icon icon="mdi:format-quote-open" class="inline mr-1 text-amber-500"/>
            {{ event.detail.question }}
          </div>

          <div
            v-if="event.event_type === 'QUESTION_RESOLVED' && event.detail?.resolution" class="mt-2 p-2 bg-[var(--status-done-bg)]/30 border border-[var(--status-done-bg)]/50 rounded-lg text-xs text-white">
            <Icon icon="mdi:check-all" class="inline mr-1 text-[var(--status-done-bg)]"/>
            {{ event.detail.resolution }}
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - CAMBIO DE ESTADO -->
          <!-- ================================================================ -->
          <!-- Muestra transición: Estado Anterior -> Estado Nuevo -->
          <!-- ================================================================ -->
          <div
            v-if="event.event_type === 'STATUS_CHANGED' && (event.detail?.from_status || event.detail?.previous_status)" class="mt-2 flex items-center gap-2 text-xs">
            <span :class="getStatusBadgeColor((event.detail?.from_status || event.detail?.previous_status) || '')">
              {{ getStatusLabel((event.detail?.from_status || event.detail?.previous_status) || '') }}
            </span>
            <Icon icon="mdi:arrow-right" class="text-[var(--text-muted)]" />
            <span :class="getStatusBadgeColor((event.detail?.to_status || event.detail?.new_status) || '')">
              {{ getStatusLabel((event.detail?.to_status || event.detail?.new_status) || '') }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - COMENTARIO -->
          <!-- ================================================================ -->
          <!-- Muestra contenido de comentario en cuadro gris -->
          <!-- ================================================================ -->
          <div
            v-if="(event.detail?.text || event.detail?.message)" class="mt-2 p-2 bg-[var(--bg-card)] rounded-lg text-xs text-[var(--text-secondary)] border-l-2 border-[var(--border-subtle)]">
            {{ event.detail.text || event.detail.message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface User {
  id: string
  name?: string
  full_name?: string
  avatar?: string
}

type EventType = 
  | 'CREATED'
  | 'ASSIGNED'
  | 'TICKET_ASSIGNED'
  | 'STATUS_CHANGED'
  | 'QUESTION_RAISED'
  | 'QUESTION_RESOLVED'
  | 'REDIRECTED'
  | 'COMPLETED'
  | 'COMMENT'
  | 'TIMER_START'
  | 'TIMER_PAUSE'
  | 'TIMER_SYNC'
  | 'SUBTASK_CREATED'
  | 'SUBTASK_COMPLETED'
  | 'SUBTASK_DELETED'
  | 'UPDATED'
  | 'MOVED'

interface EventDetail {
  from_status?: string
  previous_status?: string // Usado en redirection_service
  to_status?: string
  new_status?: string      // Usado en redirection_service
  reason?: string
  justification?: string   // Usado en redirection_service
  question?: string
  resolution?: string      // Usado al resolver preguntas
  text?: string
  message?: string         // Usado al crear/actualizar tickets
  description?: string
}

interface TicketEvent {
  id: string
  event_type: EventType
  created_at: string
  user?: User
  from_user?: User
  to_user?: User
  detail?: EventDetail
}

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  events: TicketEvent[]
}

defineProps<Props>()

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Retorna el ícono de Iconify según el tipo de evento
 * @param eventType - Tipo de evento
 * @returns Código del ícono de Iconify
 */
const getEventIcon = (eventType: string): string => {
  const icons: Record<string, string> = {
    CREATED: 'mdi:plus-circle',
    ASSIGNED: 'mdi:account-check',
    STATUS_CHANGED: 'mdi:swap-horizontal-circle',
    QUESTION_RAISED: 'mdi:help-circle-outline',
    QUESTION_RESOLVED: 'mdi:check-circle',
    REDIRECTED: 'mdi:arrow-right-circle',
    COMPLETED: 'mdi:party-popper',
    COMMENT: 'mdi:chat-outline'
  }
  return icons[eventType] || 'mdi:information-outline'
}

/**
 * Retorna clase de color para el ícono según el tipo de evento
 * @param eventType - Tipo de evento
 * @returns String de clases Tailwind
 */
const getEventIconColor = (eventType: string): string => {
  const colors: Record<string, string> = {
    CREATED: 'bg-[var(--status-done-bg)]/30 text-[var(--status-done-bg)]/80',
    ASSIGNED: 'bg-[var(--teal)]/30 text-[var(--teal)]/80',
    STATUS_CHANGED: 'bg-[var(--bg-panel)] text-[var(--text-secondary)]',
    QUESTION_RAISED: 'bg-amber-900 text-amber-300',
    QUESTION_RESOLVED: 'bg-[var(--status-done-bg)]/30 text-[var(--status-done-bg)]/80',
    REDIRECTED: 'bg-indigo-900 text-indigo-300',
    COMPLETED: 'bg-[var(--status-done-bg)]/30 text-[var(--status-done-bg)]/80',
    COMMENT: 'bg-[var(--bg-panel)] text-[var(--text-secondary)]'
  }
  return colors[eventType] || 'bg-[var(--bg-panel)] text-[var(--text-secondary)]'
}

/**
 * Retorna etiqueta en español para el tipo de evento
 * @param eventType - Tipo de evento
 * @returns Etiqueta en español
 */
const getEventTypeLabel = (eventType: string): string => {
  const labels: Record<string, string> = {
    CREATED: t('activityLog.eventCreated'),
    ASSIGNED: t('activityLog.eventAssigned'),
    TICKET_ASSIGNED: t('activityLog.eventAssigned'),
    STATUS_CHANGED: t('activityLog.eventStatusChanged'),
    QUESTION_RAISED: t('activityLog.eventQuestionRaised'),
    QUESTION_RESOLVED: t('activityLog.eventQuestionResolved'),
    REDIRECTED: t('activityLog.eventRedirected'),
    COMPLETED: t('activityLog.eventCompleted'),
    COMMENT: t('activityLog.eventComment'),
    UPDATED: t('activityLog.eventUpdated'),
    TIMER_START: t('activityLog.eventTimerStart'),
    TIMER_PAUSE: t('activityLog.eventTimerPause'),
    TIMER_SYNC: t('activityLog.eventTimerSync'),
    SUBTASK_CREATED: t('activityLog.eventSubtaskCreated'),
    SUBTASK_COMPLETED: t('activityLog.eventSubtaskCompleted'),
    SUBTASK_DELETED: t('activityLog.eventSubtaskDeleted'),
    MOVED: t('activityLog.eventMoved'),
    BLOCKED: t('activityLog.eventBlocked'),
    BLOCKED_QUESTION: t('activityLog.eventBlockedQuestion'),
  }
  return labels[eventType] ?? eventType.split('_').map(w => w.charAt(0) + w.slice(1).toLowerCase()).join(' ')
}

/**
 * Formatea timestamp a formato legible (ej: "hace 2 horas")
 * @param timestamp - Fecha ISO string
 * @returns Tiempo relativo formateado
 */
const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'justo ahora'
  if (diffMins < 60) return `hace ${diffMins}m`
  if (diffHours < 24) return `hace ${diffHours}h`
  if (diffDays < 7) return `hace ${diffDays}d`

  // Si es más de 7 días, mostrar fecha
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}`
}

/**
 * Obtiene iniciales de un nombre
 * @param name - Nombre completo
 * @returns Iniciales (máximo 2 caracteres)
 */
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Retorna etiqueta en español para un estado
 * @param status - Estado del ticket
 * @returns Etiqueta en español
 */
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    TODO: t('statuses.todo'),
    IN_PROGRESS: t('statuses.inProgress'),
    BLOCKED: t('statuses.blocked'),
    DONE: t('statuses.done'),
  }
  return labels[status] || status
}

/**
 * Retorna clase de color para badge de estado
 * @param status - Estado del ticket
 * @returns String de clases Tailwind
 */
const getStatusBadgeColor = (status: string): string => {
  const colors: Record<string, string> = {
    TODO: 'px-2 py-1 bg-gray-600 text-gray-100 rounded text-xs',
    IN_PROGRESS: 'px-2 py-1 bg-[var(--teal)] text-blue-100 rounded text-xs',
    BLOCKED: 'px-2 py-1 bg-[var(--priority-high-bg)] text-[var(--text-primary)] rounded text-xs',
    DONE: 'px-2 py-1 bg-[var(--status-done-bg)] text-green-100 rounded text-xs'
  }
  return colors[status] || 'px-2 py-1 bg-slate-600 text-slate-100 rounded text-xs'
}
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>


