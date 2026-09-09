<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: WorkbenchTicketCard                                  -->
  <!-- ================================================================ -->
  <!-- Tarjeta de ticket para el dashboard personal del desarrollador. -->
  <!-- Diseño más amplio que la tarjeta compacta del swimlane.         -->
  <!-- Muestra: breadcrumb app/épica, título, estado, prioridad, fecha -->
  <!-- ================================================================ -->

  <div
    data-cy="ticket-card"
    :data-status="ticket.status"
    @click="$emit('select', ticket)"
    :class="[
      'relative p-4 rounded-xl border cursor-pointer transition-all duration-200 select-none',
      'bg-[var(--bg-card)] hover:bg-[var(--bg-panel)]',
      ticket.status === 'BLOCKED' || ticket.status === 'BLOCKED_QUESTION'
        ? 'border-[var(--priority-urg-bg)]/60 shadow-[var(--priority-urg-bg)]/30 shadow-md'
        : selected
          ? 'border-[var(--teal)] shadow-[var(--teal)]/40 shadow-lg'
          : 'border-[var(--border-subtle)] hover:border-[var(--border-subtle)] hover:shadow-lg hover:shadow-[var(--shadow-invert)]',
    ]"
  >
    <!-- ============================================================== -->
    <!-- BREADCRUMB: App › Épica                                        -->
    <!-- ============================================================== -->
    <div class="flex items-center gap-1 mb-2.5 text-xs text-[var(--text-muted)] truncate">
      <Icon icon="mdi:layers-outline" class="flex-shrink-0 text-[var(--text-secondary)]" />
      <span class="truncate max-w-[45%]">{{ ticket.appName || '—' }}</span>
      <span class="flex-shrink-0 text-[var(--border-subtle)]">›</span>
      <span class="truncate">{{ ticket.epicTitle || '—' }}</span>
    </div>

    <!-- ============================================================== -->
    <!-- FILA PRINCIPAL: Título + Badge de estado                       -->
    <!-- ============================================================== -->
    <div class="flex items-start justify-between gap-2 mb-3">
      <h4 class="text-sm font-semibold text-[var(--text-primary)] leading-snug line-clamp-2 flex-1">
        {{ ticket.title }}
      </h4>
      <span
        :class="[
          'px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap flex-shrink-0',
          statusClasses,
        ]"
      >
        {{ statusLabel }}
      </span>
    </div>

    <!-- ============================================================== -->
    <!-- FILA INFERIOR: Prioridad + Fecha + Días atrasado              -->
    <!-- ============================================================== -->
    <div class="flex items-center gap-3">
      <!-- Indicador de prioridad -->
      <span
        :class="['w-2.5 h-2.5 rounded-full flex-shrink-0', priorityColor]"
        :title="`Prioridad: ${ticket.priority}`"
      />

      <!-- Fecha de vencimiento -->
      <div
        v-if="ticket.dueDate"
        :class="[
          'flex items-center gap-1 text-xs',
          isOverdue ? 'text-[var(--priority-urg-bg)] font-semibold' : 'text-[var(--text-secondary)]',
        ]"
      >
        <Icon
          :icon="isOverdue ? 'mdi:alert-circle-outline' : 'mdi:calendar-clock-outline'"
          class="flex-shrink-0"
        />
        {{ formattedDueDate }}
      </div>

      <!-- Días atrasado -->
      <span
        v-if="isOverdue"
        class="ml-auto text-xs font-semibold text-[var(--priority-urg-bg)] flex items-center gap-0.5"
      >
        <Icon icon="mdi:clock-alert-outline" class="flex-shrink-0" />
        {{ daysOverdue }}d atrasado
      </span>
    </div>

    <!-- ============================================================== -->
    <!-- PULSO: Indica ticket bloqueado                                 -->
    <!-- ============================================================== -->
    <div
      v-if="ticket.status === 'BLOCKED' || ticket.status === 'BLOCKED_QUESTION'"
      class="absolute inset-0 rounded-xl border border-[var(--priority-urg-bg)]/50 animate-pulse pointer-events-none"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ticket } from '@/types'

// =====================================================================
// PROPS Y EMITS
// =====================================================================

const props = defineProps<{
  ticket: Ticket
  /** Resalta la tarjeta cuando está seleccionada */
  selected?: boolean
}>()

defineEmits<{
  select: [ticket: Ticket]
}>()

// =====================================================================
// COMPUTADAS
// =====================================================================

const isOverdue = computed(() => {
  if (!props.ticket.dueDate) return false
  const [y, m, d] = props.ticket.dueDate.split('T')[0].split('-').map(Number)
  const due = new Date(y, m - 1, d)
  const today = new Date()
  return due < new Date(today.getFullYear(), today.getMonth(), today.getDate())
})

const daysOverdue = computed(() => {
  if (!isOverdue.value) return 0
  const [y, m, d] = props.ticket.dueDate!.split('T')[0].split('-').map(Number)
  const due = new Date(y, m - 1, d)
  const today = new Date()
  return Math.ceil((new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime() - due.getTime()) / 86_400_000)
})

const formattedDueDate = computed(() => {
  if (!props.ticket.dueDate) return ''
  const [y, m, d] = props.ticket.dueDate.split('T')[0].split('-').map(Number)
  return `${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}/${y}`
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    TODO: 'Por Hacer',
    IN_PROGRESS: 'En Progreso',
    BLOCKED: 'Bloqueado',
    BLOCKED_QUESTION: 'Bloqueado',
    COMPLETED: 'Completado',
    DONE: 'Completado',
    REDIRECTED: 'Redirigido',
  }
  return labels[props.ticket.status] ?? props.ticket.status
})

const statusClasses = computed(() => {
  const map: Record<string, string> = {
    TODO: 'bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]',
    IN_PROGRESS: 'bg-[var(--status-progress-bg)] text-[var(--status-progress-text)]',
    BLOCKED: 'bg-[var(--status-blocked-bg)] text-[var(--status-blocked-text)] animate-pulse',
    BLOCKED_QUESTION: 'bg-[var(--status-blocked-bg)] text-[var(--status-blocked-text)] animate-pulse',
    COMPLETED: 'bg-[var(--status-done-bg)] text-[var(--status-done-text)]',
    DONE: 'bg-[var(--status-done-bg)] text-[var(--status-done-text)]',
    REDIRECTED: 'bg-[var(--bg-panel)] text-[var(--text-primary)]',
  }
  return map[props.ticket.status] ?? 'bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]'
})

const priorityColor = computed(() => {
  const map: Record<string, string> = {
    LOW: 'bg-[var(--priority-low-bg)]',
    MEDIUM: 'bg-[var(--priority-med-bg)]',
    HIGH: 'bg-[var(--priority-high-bg)]',
    URGENT: 'bg-[var(--priority-urg-bg)]',
  }
  return map[props.ticket.priority] ?? 'bg-[var(--text-secondary)]'
})
</script>
