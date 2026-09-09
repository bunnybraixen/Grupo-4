<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: WorkbenchDashboard                                   -->
  <!-- ================================================================ -->
  <!-- Panel de "Mis Tickets" para el dashboard personal del dev.      -->
  <!-- Contiene: barra de filtros (estado + fecha) y grid de cards.    -->
  <!-- Usa el composable useWorkbenchTickets para obtener y filtrar     -->
  <!-- tickets desde el store, sin lógica duplicada.                   -->
  <!-- ================================================================ -->

  <div class="flex flex-col h-full bg-[var(--bg-app)]">

    <!-- ============================================================== -->
    <!-- BARRA DE FILTROS                                               -->
    <!-- ============================================================== -->
    <div class="flex-shrink-0 border-b border-[var(--border-subtle)] bg-[var(--bg-card)]/80 px-6 py-4 space-y-3">

      <!-- Encabezado de la sección -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon icon="mdi:ticket-account" class="text-[var(--teal)] text-lg" />
          <span class="text-sm font-semibold text-[var(--text-primary)]">{{ t('workbenchDashboard.myTickets') }}</span>
          <span class="px-2 py-0.5 text-xs font-medium bg-[var(--bg-panel)] text-[var(--text-secondary)] rounded-full">
            {{ tickets.length }}
          </span>
        </div>

        <!-- Botón de actualizar -->
        <button
          @click="refresh"
          :disabled="isLoading"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--text-secondary)] bg-[var(--bg-panel)] hover:bg-[var(--bg-panel)]/80 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Icon
            icon="mdi:refresh"
            :class="['text-sm', isLoading ? 'animate-spin' : '']"
          />
          {{ t('workbenchDashboard.refresh') }}
        </button>
      </div>

      <!-- ============================================================ -->
      <!-- FILTROS DE ESTADO                                            -->
      <!-- ============================================================ -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.statusLabel') }}</span>

        <button
          v-for="f in statusFilters"
          :key="f.value"
          @click="setStatusFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            statusFilter === f.value
              ? 'bg-[var(--lime)] text-[var(--dark-gray)] font-semibold'
              : 'bg-[var(--bg-panel)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- ============================================================ -->
      <!-- FILTROS DE FECHA                                             -->
      <!-- ============================================================ -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">{{ t('workbenchDashboard.dateLabel') }}</span>

        <button
          v-for="f in dateFilters"
          :key="f.value"
          @click="setDateFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            dateFilter === f.value
              ? f.activeClass
              : 'bg-[var(--bg-panel)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- ÁREA DE CONTENIDO: Loading / Empty / Grid de cards            -->
    <!-- ============================================================== -->
    <div class="flex-1 overflow-y-auto p-6">

      <!-- Estado: Error de carga -->
      <div
        v-if="error && !isLoading"
        class="flex flex-col items-center justify-center h-64 gap-3 text-slate-400"
      >
        <Icon icon="mdi:alert-circle-outline" class="text-5xl text-red-400 opacity-80" />
        <p class="text-sm font-medium text-red-300">{{ t('workbenchDashboard.errorLoading') }}</p>
        <p class="text-xs opacity-60 max-w-xs text-center">{{ error }}</p>
        <button
          @click="refresh"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-teal-30 border border-blue-500/40 rounded-lg hover:bg-blue-500/10 transition-colors"
        >
          {{ t('workbenchDashboard.retry') }}
        </button>
      </div>

      <!-- Estado: Cargando -->
      <div
        v-else-if="isLoading && tickets.length === 0"
        class="flex flex-col items-center justify-center h-64 gap-3 text-slate-400"
      >
        <Icon icon="mdi:loading" class="text-4xl animate-spin text-teal" />
        <p class="text-sm">{{ t('workbenchDashboard.loading') }}</p>
      </div>

      <!-- Estado: Sin resultados con filtros activos -->
      <div
        v-else-if="!error && tickets.length === 0 && hasActiveFilters"
        class="flex flex-col items-center justify-center h-64 gap-3 text-slate-400"
      >
        <Icon icon="mdi:filter-off-outline" class="text-5xl opacity-40" />
        <p class="text-sm font-medium">{{ t('workbenchDashboard.noResults') }}</p>
        <button
          @click="clearFilters"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-teal-30 border border-blue-500/40 rounded-lg hover:bg-blue-500/10 transition-colors"
        >
          {{ t('workbenchDashboard.clearFilters') }}
        </button>
      </div>

      <!-- Estado: Sin tickets asignados -->
      <div
        v-else-if="!error && tickets.length === 0"
        class="flex flex-col items-center justify-center h-64 gap-3 text-slate-400"
      >
        <Icon icon="mdi:inbox-outline" class="text-5xl opacity-40" />
        <p class="text-sm font-medium">{{ t('workbenchDashboard.noTickets') }}</p>
        <p class="text-xs opacity-60">{{ t('workbenchDashboard.ticketsWillAppear') }}</p>
      </div>

      <!-- Grid de tarjetas -->
      <div
        v-else-if="!error && tickets.length > 0"
        class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4"
      >
        <WorkbenchTicketCard
          v-for="ticket in tickets"
          :key="ticket.id"
          :ticket="ticket"
          :selected="selectedTicketId === ticket.id"
          @select="handleSelect"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import { useWorkbenchTickets } from '@/composables/useWorkbenchTickets'
import WorkbenchTicketCard from '@/components/workbench/WorkbenchTicketCard.vue'
import type { Ticket } from '@/types'

const { t } = useI18n()

// =====================================================================
// DATOS Y FILTROS DEL COMPOSABLE
// =====================================================================

const { tickets, statusFilter, dateFilter, isLoading, error, setStatusFilter, setDateFilter, refresh } =
  useWorkbenchTickets()

// =====================================================================
// SELECCIÓN LOCAL
// =====================================================================

const selectedTicketId = ref<string | null>(null)

const handleSelect = (ticket: Ticket) => {
  selectedTicketId.value = selectedTicketId.value === ticket.id ? null : ticket.id
  emit('ticketSelected', ticket)
}

// =====================================================================
// FILTROS COMPUTADOS (reactivos al idioma)
// =====================================================================

const statusFilters = computed(() => [
  { value: 'all' as const, label: t('workbenchDashboard.statusAll') },
  { value: 'in_progress' as const, label: t('workbenchDashboard.statusInProgress') },
  { value: 'todo' as const, label: t('workbenchDashboard.statusTodo') },
  { value: 'blocked' as const, label: t('workbenchDashboard.statusBlocked') },
  { value: 'completed' as const, label: t('workbenchDashboard.statusCompleted') },
])

const dateFilters = computed(() => [
  { value: 'all' as const, label: t('workbenchDashboard.dateAll'), activeClass: 'bg-[var(--lime)] text-[var(--dark-gray)] font-semibold' },
  { value: 'overdue' as const, label: t('workbenchDashboard.dateOverdue'), activeClass: 'bg-[var(--priority-urg-bg)] text-white font-semibold' },
  { value: 'today' as const, label: t('workbenchDashboard.dateToday'), activeClass: 'bg-[var(--lime)] text-[var(--dark-gray)] font-semibold' },
  { value: 'week' as const, label: t('workbenchDashboard.dateThisWeek'), activeClass: 'bg-[var(--lime)] text-[var(--dark-gray)] font-semibold' },
])

// =====================================================================
// UTILIDADES
// =====================================================================

const hasActiveFilters = computed(
  () => statusFilter.value !== 'all' || dateFilter.value !== 'all',
)

const clearFilters = () => {
  setStatusFilter('all')
  setDateFilter('all')
}

// =====================================================================
// EMITS
// =====================================================================

const emit = defineEmits<{
  ticketSelected: [ticket: Ticket]
}>()
</script>
