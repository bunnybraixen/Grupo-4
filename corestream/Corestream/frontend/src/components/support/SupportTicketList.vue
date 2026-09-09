<template>
  <div class="flex flex-col gap-2">
    <!-- Filtros -->
    <div class="flex flex-wrap gap-2 mb-3">
      <button
        v-for="opt in statusOptions"
        :key="opt.value"
        @click="store.setStatusFilter(opt.value as any)"
        :class="[
          'px-3 py-1 rounded-full text-xs font-medium transition-colors',
          store.statusFilter === opt.value
            ? 'bg-blue-600 text-white'
            : 'bg-[var(--bg-app)] text-[var(--text-secondary)] border border-[var(--border-subtle)] hover:bg-[var(--bg-panel)]'
        ]"
      >
        {{ opt.label }}
        <span v-if="opt.count" class="ml-1 opacity-70">({{ opt.count }})</span>
      </button>

      <select
        v-model="severityValue"
        class="ml-auto px-3 py-1 rounded-full text-xs bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-secondary)] focus:outline-none"
      >
        <option value="all">{{ t('supportTicketsView.severityAll') || 'Todas las severidades' }}</option>
        <option value="critical">{{ t('supportTicketsView.severityCritical') || '🔴 Crítica' }}</option>
        <option value="high">{{ t('supportTicketsView.severityHigh') || '🟠 Alta' }}</option>
        <option value="medium">{{ t('supportTicketsView.severityMedium') || '🟡 Media' }}</option>
        <option value="low">{{ t('supportTicketsView.severityLow') || '🟢 Baja' }}</option>
      </select>
    </div>

    <!-- Lista vacía -->
    <div v-if="store.filteredTickets.length === 0 && !store.isLoading" class="text-center py-12 text-[var(--text-muted)]">
      <p class="text-4xl mb-3">🐛</p>
      <p class="text-sm">{{ t('supportTicketsView.emptyList') || 'No hay tickets de soporte' }}</p>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="text-center py-8 text-[var(--text-muted)] text-sm">
      {{ t('supportTicketsView.loading') || 'Cargando tickets...' }}
    </div>

    <!-- Tarjetas -->
    <div
      v-for="ticket in store.filteredTickets"
      :key="ticket.id"
      @click="$emit('select', ticket)"
      :class="[
        'p-3 rounded-lg border cursor-pointer transition-colors',
        selectedId === ticket.id
          ? 'border-blue-500 bg-blue-500/10'
          : 'border-[var(--border-subtle)] bg-[var(--bg-panel)] hover:bg-[var(--bg-app)]'
      ]"
    >
      <div class="flex items-start gap-2">
        <span :class="['text-xs font-bold mt-0.5', severityColor(ticket.severity)]">
          {{ severityIcon(ticket.severity) }}
        </span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-[var(--text-primary)] truncate">{{ ticket.title }}</p>
          <div class="flex items-center gap-2 mt-1">
            <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', statusBadge(ticket.status)]">
              {{ statusLabel(ticket.status) }}
            </span>
            <span v-if="ticket.assignee" class="text-xs text-[var(--text-muted)] truncate">
              → {{ ticket.assignee.fullName }}
            </span>
            <span v-else class="text-xs text-[var(--text-muted)]">{{ t('supportTicketsView.unassigned') || 'Sin asignar' }}</span>
          </div>
          <p v-if="ticket.linkedTicketTitle" class="text-xs text-[var(--text-muted)] truncate mt-0.5">
            🔗 {{ ticket.linkedTicketTitle }}<span v-if="ticket.originEpicTitle"> · {{ ticket.originEpicTitle }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ticket } from '@/types'
import { TicketStatus } from '@/types'
import { useSupportTicketsStore } from '@/stores/supportTickets'

defineProps<{ selectedId?: string }>()
defineEmits<{ select: [ticket: Ticket] }>()

const { t } = useI18n()
const store = useSupportTicketsStore()

const statusOptions = computed(() => [
  { value: 'all', label: t('supportTicketsView.statusAll') || 'Todos', count: store.tickets.length },
  { value: 'reported', label: t('supportTicketsView.statusReported') || 'Reportado', count: store.reportedTickets.length },
  { value: 'investigating', label: t('supportTicketsView.statusInvestigating') || 'En Investigación', count: store.investigatingTickets.length },
  { value: 'resolved', label: t('supportTicketsView.statusResolved') || 'Resuelto', count: store.resolvedTickets.length },
])

const severityValue = computed({
  get: () => store.severityFilter,
  set: (v: string) => store.setSeverityFilter(v as any),
})

function severityIcon(severity?: string): string {
  const map: Record<string, string> = {
    CRITICAL: '🔴', HIGH: '🟠', MEDIUM: '🟡', LOW: '🟢',
  }
  return map[severity ?? ''] ?? '⚪'
}

function severityColor(severity?: string): string {
  // Variables CSS calibradas para modo claro y oscuro (global.css)
  const map: Record<string, string> = {
    CRITICAL: 'text-[var(--priority-urg-text)]',
    HIGH: 'text-[var(--priority-high-text)]',
    MEDIUM: 'text-[var(--priority-med-text)]',
    LOW: 'text-[var(--priority-low-text)]',
  }
  return map[severity ?? ''] ?? 'text-[var(--text-muted)]'
}

function statusBadge(status: string): string {
  // Variables CSS calibradas para modo claro y oscuro (global.css)
  const map: Record<string, string> = {
    REPORTED: 'bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]',
    INVESTIGATING: 'bg-[var(--status-progress-bg)] text-[var(--status-progress-text)]',
    RESOLVED: 'bg-[var(--status-done-bg)] text-[var(--status-done-text)]',
  }
  return map[status] ?? 'bg-[var(--bg-app)] text-[var(--text-muted)]'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    REPORTED: t('supportTicketsView.statusReported') || 'Reportado',
    INVESTIGATING: t('supportTicketsView.statusInvestigating') || 'En Investigación',
    RESOLVED: t('supportTicketsView.statusResolved') || 'Resuelto',
  }
  return map[status] ?? status
}
</script>
