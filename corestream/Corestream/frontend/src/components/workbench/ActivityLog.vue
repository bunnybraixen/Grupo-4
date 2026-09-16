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
    <h4 class="text-sm font-semibold text-white">Historial de Eventos</h4>

    <!-- ================================================================ -->
    <!-- LISTA DE EVENTOS -->
    <!-- ================================================================ -->
    <!-- Renderiza cada evento en orden cronológico inverso -->
    <!-- ================================================================ -->
    <div v-if="events.length === 0" class="text-center py-6 text-slate-400">
      <Icon icon="mdi:history" class="text-2xl mx-auto mb-1" />
      <p class="text-sm">Sin eventos registrados</p>
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
            getEventIconColor(event.type)
          ]"
        >
          <Icon :icon="getEventIcon(event.type)" class="text-sm" />
        </div>

        <!-- ================================================================ -->
        <!-- ELEMENTO: Contenedor de Información -->
        <!-- ================================================================ -->
        <div class="flex-1 min-w-0">
          <!-- Timestamp y Tipo de Evento -->
          <div class="flex items-start justify-between gap-2 mb-1">
            <p class="text-sm font-medium text-white">
              {{ getEventTypeLabel(event.type) }}
            </p>
            <span class="text-xs text-slate-400 flex-shrink-0">
              {{ formatTime(event.timestamp) }}
            </span>
          </div>

          <!-- Usuario y Descripción -->
          <div class="text-xs text-slate-400 mb-1">
            <span class="font-semibold text-slate-300">{{ event.user.name }}</span>
            <span v-if="event.description">
              - {{ event.description }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - REDIRECCIÓN -->
          <!-- ================================================================ -->
          <!-- Muestra flujo: Avatar A -> flecha -> Avatar B -->
          <!-- ================================================================ -->
          <div v-if="event.type === 'REDIRECTED' && event.redirectData" class="flex items-center gap-2 mt-2">
            <!-- Avatar usuario origen -->
            <div
              class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
              :title="event.redirectData.fromUserName"
            >
              {{ getInitials(event.redirectData.fromUserName) }}
            </div>

            <!-- Flecha de redirección -->
            <Icon icon="mdi:arrow-right" class="text-slate-400" />

            <!-- Avatar usuario destino -->
            <div
              class="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
              :title="event.redirectData.toUserName"
            >
              {{ getInitials(event.redirectData.toUserName) }}
            </div>

            <!-- Razón de redirección -->
            <span class="text-xs text-slate-400 ml-2">
              {{ event.redirectData.reason }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - PREGUNTA LEVANTADA -->
          <!-- ================================================================ -->
          <!-- Muestra la pregunta en un cuadro ámbar -->
          <!-- ================================================================ -->
          <div
            v-if="event.type === 'QUESTION_RAISED' && event.questionData"
            class="mt-2 p-2 bg-amber-900 bg-opacity-30 border border-amber-700 rounded text-xs text-amber-100"
          >
            {{ event.questionData.question }}
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - CAMBIO DE ESTADO -->
          <!-- ================================================================ -->
          <!-- Muestra transición: Estado Anterior -> Estado Nuevo -->
          <!-- ================================================================ -->
          <div v-if="event.type === 'STATUS_CHANGED' && event.statusData" class="mt-2 flex items-center gap-1 text-xs">
            <span :class="getStatusBadgeColor(event.statusData.from)">
              {{ getStatusLabel(event.statusData.from) }}
            </span>
            <Icon icon="mdi:arrow-right" class="text-slate-400" />
            <span :class="getStatusBadgeColor(event.statusData.to)">
              {{ getStatusLabel(event.statusData.to) }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- SECCIÓN: Evento Especial - COMENTARIO -->
          <!-- ================================================================ -->
          <!-- Muestra contenido de comentario en cuadro gris -->
          <!-- ================================================================ -->
          <div
            v-if="event.type === 'COMMENT' && event.commentData"
            class="mt-2 p-2 bg-slate-700 rounded text-xs text-slate-200"
          >
            {{ event.commentData.text }}
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

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface User {
  id: string
  name: string
  avatar?: string
}

interface TicketEvent {
  id: string
  type:
    | 'CREATED'
    | 'ASSIGNED'
    | 'STATUS_CHANGED'
    | 'QUESTION_RAISED'
    | 'QUESTION_RESOLVED'
    | 'REDIRECTED'
    | 'COMPLETED'
    | 'COMMENT'
  timestamp: string
  user: User
  description?: string
  statusData?: { from: string; to: string }
  redirectData?: {
    fromUserName: string
    toUserName: string
    reason: string
  }
  questionData?: { question: string }
  commentData?: { text: string }
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
    CREATED: 'bg-green-900 text-green-300',
    ASSIGNED: 'bg-blue-900 text-blue-300',
    STATUS_CHANGED: 'bg-slate-700 text-slate-300',
    QUESTION_RAISED: 'bg-amber-900 text-amber-300',
    QUESTION_RESOLVED: 'bg-green-900 text-green-300',
    REDIRECTED: 'bg-indigo-900 text-indigo-300',
    COMPLETED: 'bg-green-900 text-green-300',
    COMMENT: 'bg-slate-700 text-slate-300'
  }
  return colors[eventType] || 'bg-slate-700 text-slate-300'
}

/**
 * Retorna etiqueta en español para el tipo de evento
 * @param eventType - Tipo de evento
 * @returns Etiqueta en español
 */
const getEventTypeLabel = (eventType: string): string => {
  const labels: Record<string, string> = {
    CREATED: 'Ticket Creado',
    ASSIGNED: 'Asignado',
    STATUS_CHANGED: 'Estado Cambiado',
    QUESTION_RAISED: 'Pregunta Levantada',
    QUESTION_RESOLVED: 'Pregunta Resuelta',
    REDIRECTED: 'Redirigido',
    COMPLETED: 'Completado',
    COMMENT: 'Comentario'
  }
  return labels[eventType] || eventType
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
    TODO: 'Por Hacer',
    IN_PROGRESS: 'En Curso',
    BLOCKED: 'Bloqueado',
    DONE: 'Completado'
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
    IN_PROGRESS: 'px-2 py-1 bg-blue-600 text-blue-100 rounded text-xs',
    BLOCKED: 'px-2 py-1 bg-orange-600 text-orange-100 rounded text-xs',
    DONE: 'px-2 py-1 bg-green-600 text-green-100 rounded text-xs'
  }
  return colors[status] || 'px-2 py-1 bg-slate-600 text-slate-100 rounded text-xs'
}
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>
