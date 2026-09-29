<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: TicketHistory (WEB-11)                               -->
  <!-- ================================================================ -->
  <!-- Historial de eventos de un ticket en orden cronológico: autor,    -->
  <!-- fecha/hora y datos relevantes de cada acción.                     -->
  <!-- ================================================================ -->

  <div>
    <p v-if="loading" class="text-xs text-[var(--text-muted)]">Cargando historial…</p>
    <p v-else-if="error" class="text-xs text-red-400">{{ error }}</p>
    <p v-else-if="!eventList.length" class="text-xs italic text-[var(--text-muted)]">
      Sin eventos registrados.
    </p>

    <ol v-else class="space-y-2.5">
      <li v-for="event in eventList" :key="event.id" class="flex gap-2">
        <span
          :class="[
            'mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full text-[11px]',
            iconClass(event.eventType),
          ]"
          aria-hidden="true"
        >
          {{ icon(event.eventType) }}
        </span>

        <div class="min-w-0 flex-1">
          <p class="text-xs text-[var(--text-primary)]">
            <span class="font-medium">{{ label(event.eventType) }}</span>
            <span class="text-[var(--text-muted)]"> · {{ author(event) }}</span>
          </p>
          <p
            v-if="description(event)"
            class="text-[11px] break-words text-[var(--text-muted)]"
          >
            {{ description(event) }}
          </p>
          <p class="text-[10px] text-[var(--text-muted)]">{{ formatDateTime(event.createdAt) }}</p>
        </div>
      </li>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TicketHistoryEvent } from '@/types'

const props = withDefaults(
  defineProps<{
    /** Eventos del ticket (tal como los devuelve GET /tickets/{id}/events) */
    events?: TicketHistoryEvent[] | null
    /** Mientras se cargan los eventos */
    loading?: boolean
    /** Mensaje de error de la carga */
    error?: string
  }>(),
  {
    events: null,
    loading: false,
    error: '',
  }
)

const eventList = computed<TicketHistoryEvent[]>(() => props.events ?? [])

/** Etiquetas en español por tipo de evento (TicketEventType del backend) */
const EVENT_LABELS: Record<string, string> = {
  CREATED: 'Ticket creado',
  ASSIGNED: 'Asignación',
  TICKET_ASSIGNED: 'Ticket asignado',
  STATUS_CHANGED: 'Cambio de estado',
  MOVED: 'Movido de épica',
  UPDATED: 'Actualización',
  QUESTION_RAISED: 'Pregunta planteada',
  QUESTION_RESOLVED: 'Pregunta resuelta',
  REDIRECTED: 'Redirección',
  COMPLETED: 'Completado',
  COMMENT: 'Comentario',
  SUBTASK_CREATED: 'Subtarea creada',
  SUBTASK_COMPLETED: 'Subtarea completada',
  SUBTASK_DELETED: 'Subtarea eliminada',
  TIMER_START: 'Temporizador iniciado',
  TIMER_PAUSE: 'Temporizador pausado',
}

const EVENT_ICONS: Record<string, string> = {
  CREATED: '✨',
  ASSIGNED: '👤',
  TICKET_ASSIGNED: '👤',
  STATUS_CHANGED: '🔄',
  MOVED: '📦',
  UPDATED: '✏️',
  QUESTION_RAISED: '❓',
  QUESTION_RESOLVED: '💬',
  REDIRECTED: '↪️',
  COMPLETED: '✅',
  COMMENT: '💬',
  SUBTASK_CREATED: '➕',
  SUBTASK_COMPLETED: '✔️',
  SUBTASK_DELETED: '🗑',
  TIMER_START: '⏱',
  TIMER_PAUSE: '⏸',
}

const EVENT_CLASSES: Record<string, string> = {
  CREATED: 'bg-emerald-500/15 text-emerald-300',
  COMPLETED: 'bg-emerald-500/15 text-emerald-300',
  SUBTASK_COMPLETED: 'bg-emerald-500/15 text-emerald-300',
  STATUS_CHANGED: 'bg-blue-500/15 text-blue-300',
  TICKET_ASSIGNED: 'bg-blue-500/15 text-blue-300',
  ASSIGNED: 'bg-blue-500/15 text-blue-300',
  QUESTION_RAISED: 'bg-amber-500/15 text-amber-300',
  REDIRECTED: 'bg-purple-500/15 text-purple-300',
  MOVED: 'bg-purple-500/15 text-purple-300',
}

const label = (type: string): string => EVENT_LABELS[type] ?? type
const icon = (type: string): string => EVENT_ICONS[type] ?? '•'
const iconClass = (type: string): string =>
  EVENT_CLASSES[type] ?? 'bg-[var(--bg-app)] text-[var(--text-muted)]'

/** Autor del evento: nombre, email o "Sistema" si no hay usuario */
const author = (event: TicketHistoryEvent): string =>
  event.user?.fullName || event.user?.email || 'Sistema'

/** Claves técnicas que no aportan a la descripción */
const DETAIL_NOISE = [
  'message',
  'action',
  'changes',
  'tags',
  'timestamp',
  'recordedAt',
  'recorded_at',
  'transitionedAt',
  'transitioned_at',
]

/**
 * Descripción legible del evento.
 *
 * Se prefiere el `message` que guarda el backend; si no existe se arma con los
 * datos relevantes (estado origen/destino, etiquetas, campos cambiados...).
 * Ojo: el interceptor camelCase del cliente convierte también las claves de
 * `detail`, así que se aceptan ambas formas.
 */
const description = (event: TicketHistoryEvent): string => {
  const detail: Record<string, any> = event.detail ?? {}

  if (typeof detail.message === 'string' && detail.message) return detail.message

  const fromStatus = detail.fromStatus ?? detail.from_status
  const toStatus = detail.toStatus ?? detail.to_status
  if (fromStatus && toStatus) return `${fromStatus} → ${toStatus}`

  if (Array.isArray(detail.tags)) {
    return detail.tags.length ? `Etiquetas: ${detail.tags.join(', ')}` : 'Sin etiquetas'
  }

  const extraKeys = Object.keys(detail).filter((key) => !DETAIL_NOISE.includes(key))
  return extraKeys.length ? `Datos registrados: ${extraKeys.join(', ')}` : ''
}

/** Fecha y hora local del evento (dd/mm/aaaa hh:mm) */
const formatDateTime = (iso: string): string => {
  if (!iso) return '—'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  const pad = (value: number): string => String(value).padStart(2, '0')
  return `${pad(date.getDate())}/${pad(date.getMonth() + 1)}/${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
</script>
