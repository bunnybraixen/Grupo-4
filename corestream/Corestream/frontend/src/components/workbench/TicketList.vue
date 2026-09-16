<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Lista de Tickets del Desarrollador -->
  <!-- ================================================================ -->
  <!-- Panel izquierdo con lista de tickets asignados al desarrollador -->
  <!-- Soporta: filtrado por estado, filtrado por fecha, búsqueda -->
  <!-- Muestra: título, épica, estado, prioridad, fecha, tiempo transcurrido -->
  <!-- ================================================================ -->

  <div class="flex flex-col h-full bg-[var(--bg-app)] border-r border-[var(--border-subtle)]">
    <!-- ================================================================ -->
    <!-- SECCIÓN: Encabezado -->
    <!-- ================================================================ -->
    <!-- Título y opciones de filtrado -->
    <!-- ================================================================ -->
    <div class="p-4 border-b border-[var(--border-subtle)] space-y-4">
      <h2 class="text-lg font-bold text-[var(--text-primary)]">Mis Tickets</h2>

      <!-- ================================================================ -->
      <!-- FILA DE FILTROS: Estado -->
      <!-- ================================================================ -->
      <div>
        <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-2">
          Estado
        </label>
        <div class="flex gap-2 flex-wrap">
          <button
            @click="statusFilter = null"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              statusFilter === null
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Todos
          </button>
          <button
            @click="statusFilter = 'IN_PROGRESS'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              statusFilter === 'IN_PROGRESS'
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            En Curso
          </button>
          <button
            @click="statusFilter = 'TODO'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              statusFilter === 'TODO'
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Por Hacer
          </button>
        </div>
      </div>

      <!-- ================================================================ -->
      <!-- FILA DE FILTROS: Fecha -->
      <!-- ================================================================ -->
      <div>
        <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-2">
          Fecha
        </label>
        <div class="flex gap-2 flex-wrap">
          <button
            @click="dateFilter = null"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              dateFilter === null
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Todas
          </button>
          <button
            @click="dateFilter = 'overdue'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              dateFilter === 'overdue'
                ? 'bg-red-600 text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Atrasados
          </button>
          <button
            @click="dateFilter = 'today'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              dateFilter === 'today'
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Hoy
          </button>
          <button
            @click="dateFilter = 'week'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              dateFilter === 'week'
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Esta Semana
          </button>
          <button
            @click="dateFilter = 'later'"
            :class="[
              'px-3 py-1 rounded-full text-xs font-medium transition-colors',
              dateFilter === 'later'
                ? 'bg-[var(--teal)] text-[var(--text-primary)]'
                : 'bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]'
            ]"
          >
            Después
          </button>
        </div>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Lista de Tickets -->
    <!-- ================================================================ -->
    <!-- Renderiza tickets filtrados y ordenados -->
    <!-- ================================================================ -->
    <div class="flex-1 overflow-y-auto">
      <div
        v-if="filteredTickets.length === 0"
        class="p-8 text-center text-[var(--text-muted)]"
      >
        <Icon icon="mdi:inbox-outline" class="text-5xl mx-auto mb-3 opacity-50" />
        <p class="text-sm font-medium">No hay tickets asignados</p>
        <p class="text-xs mt-1">Los tickets aparecerán aquí cuando te los asignen</p>
      </div>

      <div v-else class="p-2 space-y-2">
        <button
          v-for="ticket in filteredTickets"
          :key="ticket.id"
          draggable="true"
          @dragstart="dragStart(ticket, 'ticket', $event)"
          @dragend="dragEnd"
          @click="selectTicket(ticket)"
          :class="[
            'w-full p-3 text-left rounded-lg border transition-all duration-200',
            'hover:shadow-lg hover:border-blue-500',
            selectedTicketId === ticket.id
              ? 'bg-[var(--bg-panel)] border-blue-500 shadow-lg'
              : 'bg-[var(--bg-card)] border-[var(--border-subtle)] hover:bg-slate-750'
          ]"
        >
          <!-- ================================================================ -->
          <!-- FILA 1: Título y Estado -->
          <!-- ================================================================ -->
          <div class="flex items-start justify-between gap-2 mb-2">
            <h4 class="text-sm font-medium text-[var(--text-primary)] flex-1 line-clamp-2">
              {{ ticket.title }}
            </h4>
            <span
              :class="[
                'inline-block px-2 py-1 text-xs font-semibold rounded whitespace-nowrap flex-shrink-0',
                getStatusColor(ticket.status)
              ]"
            >
              {{ getStatusLabel(ticket.status) }}
            </span>
          </div>

          <!-- ================================================================ -->
          <!-- FILA 2: Épica (breadcrumb) -->
          <!-- ================================================================ -->
          <div class="flex items-center gap-2 mb-2 text-xs text-[var(--text-muted)]">
            <Icon icon="mdi:folder-outline" class="flex-shrink-0" />
            <span class="truncate">{{ ticket.epicName || 'Sin épica' }}</span>
          </div>

          <!-- ================================================================ -->
          <!-- FILA 3: Indicadores (Prioridad, Fecha, Tiempo) -->
          <!-- ================================================================ -->
          <div class="flex items-center justify-between gap-2">
            <!-- Punto de prioridad -->
            <div
              :class="[
                'w-2 h-2 rounded-full flex-shrink-0',
                getPriorityColor(ticket.priority)
              ]"
              :title="`Prioridad: ${ticket.priority}`"
            />

            <!-- Indicador de vencimiento -->
            <div
              v-if="ticket.dueDate"
              :class="[
                'text-xs flex items-center gap-1 flex-shrink-0',
                isTicketOverdue(ticket) ? 'text-[var(--priority-urg-bg)] font-semibold' : 'text-[var(--text-muted)]'
              ]"
            >
              <Icon
                :icon="isTicketOverdue(ticket) ? 'mdi:alert-circle' : 'mdi:calendar'"
              />
              {{ formatDate(ticket.dueDate) }}
            </div>

            <!-- Indicador de tiempo transcurrido -->
            <div v-if="ticket.timeSpentSeconds" class="text-xs text-[var(--text-muted)] flex items-center gap-1 flex-shrink-0">
              <Icon icon="mdi:clock-outline" />
              {{ formatTime(ticket.timeSpentSeconds) }}
            </div>
          </div>

          <!-- ================================================================ -->
          <!-- INDICADOR: Ticket Atrasado -->
          <!-- ================================================================ -->
          <div
            v-if="isTicketOverdue(ticket)"
            class="mt-2 text-xs font-semibold text-[var(--priority-urg-bg)] flex items-center gap-1"
          >
            <Icon icon="mdi:close-circle" />
            {{ getDaysOverdue(ticket) }} días atrasado
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useTicketsStore } from '@/stores/tickets'
import { useDragDrop } from '@/composables/useDragDrop'
import type { Ticket } from '@/types'

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Filtro de estado actual
const statusFilter = ref<string | null>(null)

// Filtro de fecha actual
const dateFilter = ref<string | null>(null)

// ID del ticket actualmente seleccionado
const selectedTicketId = ref<string | null>(null)

// =====================================================================
// STORE Y DATOS
// =====================================================================

// Acceso al store de tickets
const ticketsStore = useTicketsStore()

// Drag & Drop composable
const { dragStart, dragEnd } = useDragDrop()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Filtra y ordena los tickets según los filtros aplicados
 * Combina filtro de estado y filtro de fecha
 */
const filteredTickets = computed(() => {
  let filtered: Ticket[] = ticketsStore.myWorkbench

  // Aplicar filtro de estado si está seleccionado
  if (statusFilter.value) {
    filtered = filtered.filter((t: Ticket) => t.status === statusFilter.value)
  }

  // Aplicar filtro de fecha si está seleccionado
  if (dateFilter.value) {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    filtered = filtered.filter((ticket: Ticket) => {
      if (!ticket.dueDate) return dateFilter.value === 'later'

      const dueDate = new Date(ticket.dueDate)
      dueDate.setHours(0, 0, 0, 0)

      switch (dateFilter.value) {
        case 'overdue':
          return dueDate < today
        case 'today':
          return dueDate.getTime() === today.getTime()
        case 'week': {
          const weekEnd = new Date(today)
          weekEnd.setDate(weekEnd.getDate() + 7)
          return dueDate >= today && dueDate <= weekEnd
        }
        case 'later':
          return dueDate > today
        default:
          return true
      }
    })
  }

  // Ordenar por fecha de vencimiento (más próximas primero)
  return filtered.sort((a: Ticket, b: Ticket) => {
    if (!a.dueDate) return 1
    if (!b.dueDate) return -1
    return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
  })
})

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Retorna clases de color para el badge de estado
 */
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'TODO':
      return 'bg-gray-600 text-gray-100'
    case 'IN_PROGRESS':
      return 'bg-[var(--teal)] text-[var(--text-primary)]'
    case 'BLOCKED':
      return 'bg-[var(--priority-high-bg)] text-[var(--text-primary)]'
    case 'DONE':
      return 'bg-[var(--status-done-bg)] text-[var(--text-primary)]'
    default:
      return 'bg-slate-600 text-slate-100'
  }
}

/**
 * Retorna etiqueta en español para el estado
 */
const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'TODO':
      return 'Por Hacer'
    case 'IN_PROGRESS':
      return 'En Curso'
    case 'BLOCKED':
      return 'Bloqueado'
    case 'COMPLETED':
    case 'DONE':
      return 'Completado'
    default:
      return status
  }
}

/**
 * Retorna clase de color para el punto de prioridad
 */
const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'LOW':
      return 'bg-[var(--priority-low-bg)]'
    case 'MEDIUM':
      return 'bg-[var(--priority-med-bg)]'
    case 'HIGH':
      return 'bg-[var(--priority-high-bg)]'
    case 'URGENT':
      return 'bg-[var(--priority-urg-bg)]'
    default:
      return 'bg-[var(--text-muted)]'
  }
}

/**
 * Formatea una fecha en formato dd/MM/yyyy
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

/**
 * Formatea tiempo en segundos a formato HH:MM:SS
 */
const formatTime = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${hours}h ${minutes}m`
}

/**
 * Determina si un ticket está atrasado
 */
const isTicketOverdue = (ticket: Ticket): boolean => {
  if (!ticket.dueDate) return false
  return new Date(ticket.dueDate) < new Date()
}

/**
 * Calcula días atrasados
 */
const getDaysOverdue = (ticket: Ticket): number => {
  if (!ticket.dueDate) return 0
  const dueDate = new Date(ticket.dueDate)
  const today = new Date()
  const diffTime = Math.abs(today.getTime() - dueDate.getTime())
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Selecciona un ticket y emite evento
 */
const selectTicket = (ticket: Ticket) => {
  selectedTicketId.value = ticket.id
  emit('selectTicket', ticket)
}

// =====================================================================
// EMITS
// =====================================================================

const emit = defineEmits<{
  selectTicket: [ticket: Ticket]
}>()
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>


