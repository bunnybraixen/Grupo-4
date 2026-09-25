<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: WorkbenchDashboard                                   -->
  <!-- ================================================================ -->
  <!-- Panel de "Mis Tickets" para el dashboard personal del dev.      -->
  <!-- Incluye: filtros, controles de tickets (Iniciar, Finalizar,     -->
  <!-- Subtareas, Detalle), barra de progreso de subtareas y asignación-->
  <!-- de equipo para Team Leaders.                                    -->
  <!-- ================================================================ -->

  <div class="flex flex-col h-full bg-[var(--bg-app)]">

    <!-- ============================================================== -->
    <!-- BARRA DE FILTROS                                               -->
    <!-- ============================================================== -->
    <div class="flex-shrink-0 border-b border-[var(--border-subtle)] bg-[var(--bg-card)]/80 px-6 py-4 space-y-3">

      <!-- Encabezado de la sección -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-[var(--teal)] text-lg">🎫</span>
          <span class="text-sm font-semibold text-[var(--text-primary)]">Mis Tickets</span>
          <span class="px-2 py-0.5 text-xs font-medium bg-[var(--bg-app)] text-[var(--text-muted)] rounded-full border border-[var(--border-subtle)]">
            {{ tickets.length }}
          </span>
        </div>

        <!-- Botón de actualizar -->
        <button
          @click="refresh"
          :disabled="isLoading"
          class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[var(--text-muted)] bg-[var(--bg-app)] hover:bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span :class="['text-sm', isLoading ? 'animate-spin inline-block' : '']">↻</span>
          Actualizar
        </button>
      </div>

      <!-- Filtros de Estado -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">Estado:</span>
        <button
          v-for="f in statusFilters"
          :key="f.value"
          @click="setStatusFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            statusFilter === f.value
              ? 'bg-[var(--teal)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- Filtros de Fecha -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-xs font-medium text-[var(--text-muted)] flex-shrink-0">Fecha:</span>
        <button
          v-for="f in dateFilters"
          :key="f.value"
          @click="setDateFilter(f.value)"
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium transition-colors',
            dateFilter === f.value
              ? 'bg-[var(--teal)] text-white font-semibold'
              : 'bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:border-[var(--teal)]',
          ]"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- ÁREA DE CONTENIDO: Loading / Empty / Lista de tickets          -->
    <!-- ============================================================== -->
    <div class="flex-1 overflow-y-auto p-6">

      <!-- Estado: Error de carga -->
      <div
        v-if="error && !isLoading"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">⚠️</span>
        <p class="text-sm font-medium text-red-300">Error al cargar los tickets</p>
        <p class="text-xs opacity-60 max-w-xs text-center">{{ error }}</p>
        <button
          @click="refresh"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-[var(--teal)] border border-[var(--teal)]/40 rounded-lg hover:bg-[var(--teal)]/10 transition-colors"
        >
          Reintentar
        </button>
      </div>

      <!-- Estado: Cargando -->
      <div
        v-else-if="isLoading && tickets.length === 0"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-4xl animate-spin inline-block">↻</span>
        <p class="text-sm">Cargando tickets...</p>
      </div>

      <!-- Estado: Sin resultados con filtros activos -->
      <div
        v-else-if="!error && tickets.length === 0 && hasActiveFilters"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">🔍</span>
        <p class="text-sm font-medium">No hay tickets con los filtros seleccionados</p>
        <button
          @click="clearFilters"
          class="mt-1 px-4 py-1.5 text-xs font-medium text-[var(--teal)] border border-[var(--teal)]/40 rounded-lg hover:bg-[var(--teal)]/10 transition-colors"
        >
          Limpiar filtros
        </button>
      </div>

      <!-- Estado: Sin tickets asignados -->
      <div
        v-else-if="!error && tickets.length === 0"
        class="flex flex-col items-center justify-center h-48 gap-3 text-slate-400"
      >
        <span class="text-5xl opacity-40">📭</span>
        <p class="text-sm font-medium">No tienes tickets asignados</p>
        <p class="text-xs opacity-60">Las tareas que te asignen aparecerán aquí</p>
      </div>

      <!-- Lista de tarjetas de ticket con controles completos -->
      <div
        v-else-if="!error && tickets.length > 0"
        class="space-y-3"
      >
        <p v-if="actionError" class="px-4 py-2 text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg">
          {{ actionError }}
        </p>

        <div
          v-for="ticket in tickets"
          :key="ticket.id"
          class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4 space-y-3 hover:border-[var(--teal)]/40 transition-colors"
        >
          <!-- Breadcrumb App > Épica -->
          <div class="flex items-center gap-1 text-xs text-[var(--text-muted)] truncate">
            <span>📋</span>
            <span class="truncate max-w-[45%]">{{ ticket.appName || '—' }}</span>
            <span class="text-[var(--border-subtle)] flex-shrink-0">›</span>
            <span class="truncate">{{ ticket.epicTitle || '—' }}</span>
          </div>

          <!-- Título + estado + prioridad -->
          <div class="flex items-start justify-between gap-3">
            <h4 class="text-sm font-semibold text-[var(--text-primary)] leading-snug flex-1">
              {{ ticket.title }}
            </h4>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <span :class="statusClass(ticket.status)" class="px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap">
                {{ statusLabel(ticket.status) }}
              </span>
              <span :class="priorityClass(ticket.priority)" class="px-2 py-0.5 text-xs font-medium rounded-full whitespace-nowrap">
                {{ priorityLabel(ticket.priority) }}
              </span>
            </div>
          </div>

          <!-- Asignado + Fecha -->
          <div class="flex items-center gap-3 text-xs text-[var(--text-muted)] flex-wrap">
            <span v-if="ticket.assignee" class="text-[var(--teal)] font-medium">
              👤 {{ ticket.assignee.fullName || ticket.assignee.email }}
            </span>
            <span v-else>👤 Sin asignar</span>
            <span v-if="ticket.dueDate">📅 {{ ticket.dueDate.slice(0, 10) }}</span>
          </div>

          <!-- Barra de progreso subtareas -->
          <div v-if="getSubtaskStats(ticket).total > 0" class="space-y-1">
            <div class="flex items-center justify-between text-[11px] text-[var(--text-muted)]">
              <span>Subtareas: {{ getSubtaskStats(ticket).completed }}/{{ getSubtaskStats(ticket).total }} completadas</span>
              <span class="font-medium text-[var(--teal)]">{{ getSubtaskStats(ticket).percentage }}%</span>
            </div>
            <div class="h-1.5 w-full rounded-full overflow-hidden bg-[var(--bg-app)] border border-[var(--border-subtle)]">
              <div
                class="h-full rounded-full bg-[var(--teal)] transition-all duration-300"
                :style="{ width: getSubtaskStats(ticket).percentage + '%' }"
              ></div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-wrap gap-2 pt-1 border-t border-[var(--border-subtle)]">
            <!-- Asignar (solo Team Leader / Admin) -->
            <select
              v-if="canAssignTickets"
              :value="ticket.assigneeId || ''"
              @change="handleAssigneeChange(ticket, $event)"
              :disabled="working"
              class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)] disabled:opacity-50"
            >
              <option value="">👤 Asignar a...</option>
              <option v-for="u in assignableUsers" :key="u.id" :value="u.id">
                {{ u.fullName || u.email }}
              </option>
            </select>

            <button
              v-if="ticket.status === 'TODO'"
              :disabled="working"
              @click="startTicket(ticket)"
              class="px-3 py-1 rounded-lg text-xs bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 disabled:opacity-50 font-medium"
            >
              ▶ Iniciar
            </button>

            <button
              v-if="ticket.status === 'IN_PROGRESS'"
              :disabled="working"
              @click="completeTicket(ticket)"
              class="px-3 py-1 rounded-lg text-xs bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-600/30 disabled:opacity-50 font-medium"
            >
              ✓ Finalizar
            </button>

            <button
              @click="toggleSubtaskPanel(ticket.id)"
              class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              ☑ Subtareas ({{ (ticket.subtasks ?? []).length }})
            </button>

            <button
              @click="toggleDetail(ticket.id)"
              class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
            >
              👁 Detalle
            </button>
          </div>

          <!-- Panel de Subtareas -->
          <div
            v-if="openSubtasksFor === ticket.id"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 space-y-2"
          >
            <p v-if="!(ticket.subtasks ?? []).length" class="text-xs text-[var(--text-muted)]">
              Este ticket todavía no tiene subtareas.
            </p>
            <ul v-else class="space-y-1.5">
              <li v-for="sub in ticket.subtasks" :key="sub.id" class="flex items-center gap-2 text-xs">
                <input
                  type="checkbox"
                  :checked="sub.isCompleted"
                  :disabled="working"
                  @change="toggleSubtask(ticket, sub)"
                  class="accent-[var(--teal)] rounded cursor-pointer"
                />
                <span :class="sub.isCompleted ? 'line-through text-[var(--text-muted)]' : 'text-[var(--text-primary)]'">
                  {{ sub.title }}
                </span>
              </li>
            </ul>
            <div
              v-if="canManageSubtasks"
              class="flex gap-2 pt-1 border-t border-[var(--border-subtle)]"
            >
              <input
                v-model="newSubtaskTitle"
                @keyup.enter="addSubtask(ticket)"
                placeholder="Nueva subtarea…"
                class="flex-1 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1 text-xs outline-none focus:border-[var(--teal)]"
              />
              <button
                :disabled="working || !newSubtaskTitle.trim()"
                @click="addSubtask(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30 disabled:opacity-50 font-medium"
              >
                Añadir
              </button>
            </div>
          </div>

          <!-- Panel de Detalle -->
          <div
            v-if="openDetailFor === ticket.id"
            class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 text-xs space-y-1.5"
          >
            <p><span class="text-[var(--text-muted)]">Descripción:</span> {{ ticket.description || '—' }}</p>
            <p><span class="text-[var(--text-muted)]">Épica:</span> {{ ticket.epicTitle || '—' }}</p>
            <p><span class="text-[var(--text-muted)]">Asignado:</span> {{ ticket.assignee ? (ticket.assignee.fullName || ticket.assignee.email) : 'Sin asignar' }}</p>
            <p v-if="ticket.prLink"><span class="text-[var(--text-muted)]">PR:</span>
              <a :href="ticket.prLink" target="_blank" rel="noopener" class="text-[var(--teal)] underline break-all ml-1">{{ ticket.prLink }}</a>
            </p>
            <p><span class="text-[var(--text-muted)]">Fecha límite:</span> {{ ticket.dueDate ? ticket.dueDate.slice(0, 10) : '—' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useWorkbenchTickets } from '@/composables/useWorkbenchTickets'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import { api } from '@/services/api'
import type { Subtask, Ticket, User } from '@/types'

// =====================================================================
// COMPOSABLE: tickets del workbench + filtros
// =====================================================================

const { tickets, statusFilter, dateFilter, isLoading, error, setStatusFilter, setDateFilter, refresh } =
  useWorkbenchTickets()

// =====================================================================
// AUTH / PERMISOS
// =====================================================================

const authStore = useAuthStore()
const teamsStore = useTeamsStore()
const userRole = computed(() => authStore.user?.role || localStorage.getItem('userRole') || 'DEVELOPER')
const isGroupLeader = computed(() => {
  const role = String(userRole.value || '').toUpperCase()
  return role === 'GROUP_LEADER' || role === 'TEAM_LEADER'
})
const isAdmin = computed(() => userRole.value === 'ADMIN')
const canAssignTickets = computed(() => isGroupLeader.value || isAdmin.value)

/**
 * Solo ADMIN/TEAM_LEADER crean subtareas (el backend responde 403 a un
 * DEVELOPER en `POST /api/subtasks/`).
 */
const canManageSubtasks = computed(() => authStore.isTeamLeader || isAdmin.value)

// =====================================================================
// ESTADO LOCAL
// =====================================================================

const openSubtasksFor = ref<string | null>(null)
const openDetailFor = ref<string | null>(null)
const newSubtaskTitle = ref('')
const working = ref(false)
const actionError = ref('')
const availableUsers = ref<User[]>([])

/**
 * Solo los miembros del equipo del líder pueden recibir el ticket; un ADMIN
 * asigna a cualquiera. `availableUsers` trae la lista completa de la API y el
 * filtro se hace aquí porque los equipos viven en el cliente (localStorage).
 */
const assignableUsers = computed(() =>
  teamsStore.filterUsersByTeams(
    availableUsers.value,
    authStore.user?.email || localStorage.getItem('userEmail'),
    isAdmin.value
  )
)

// =====================================================================
// HELPERS
// =====================================================================

const getSubtaskStats = (ticket: Ticket) => {
  const subs = ticket.subtasks ?? []
  const total = subs.length
  const completed = subs.filter((s) => s.isCompleted).length
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)
  return { total, completed, percentage }
}

const hasActiveFilters = computed(
  () => statusFilter.value !== 'all' || dateFilter.value !== 'all',
)

const clearFilters = () => {
  setStatusFilter('all')
  setDateFilter('all')
}

// =====================================================================
// FILTROS
// =====================================================================

const statusFilters = computed(() => [
  { value: 'all' as const, label: 'Todos' },
  { value: 'in_progress' as const, label: 'En progreso' },
  { value: 'todo' as const, label: 'Por hacer' },
  { value: 'blocked' as const, label: 'Bloqueado' },
  { value: 'completed' as const, label: 'Completados' },
])

const dateFilters = computed(() => [
  { value: 'all' as const, label: 'Todas las fechas' },
  { value: 'overdue' as const, label: 'Atrasados' },
  { value: 'today' as const, label: 'Hoy' },
  { value: 'week' as const, label: 'Esta semana' },
])

// =====================================================================
// ACCIONES DE TICKET
// =====================================================================

const startTicket = async (ticket: Ticket) => {
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo iniciar el ticket.'
  } finally {
    working.value = false
  }
}

const completeTicket = async (ticket: Ticket) => {
  const prLink = window.prompt('Enlace del Pull Request para finalizar el ticket (opcional):')
  if (prLink === null) return
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.complete(ticket.id, prLink.trim())
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo finalizar el ticket.'
  } finally {
    working.value = false
  }
}

const toggleSubtaskPanel = (ticketId: string) => {
  openSubtasksFor.value = openSubtasksFor.value === ticketId ? null : ticketId
  openDetailFor.value = null
  newSubtaskTitle.value = ''
}

const toggleDetail = (ticketId: string) => {
  openDetailFor.value = openDetailFor.value === ticketId ? null : ticketId
  openSubtasksFor.value = null
}

const addSubtask = async (ticket: Ticket) => {
  const title = newSubtaskTitle.value.trim()
  if (!title) return
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.createSubtask(ticket.id, title)
    newSubtaskTitle.value = ''
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo crear la subtarea.'
  } finally {
    working.value = false
  }
}

const toggleSubtask = async (ticket: Ticket, sub: Subtask) => {
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.updateSubtask(ticket.id, sub.id, { isCompleted: !sub.isCompleted })
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo actualizar la subtarea.'
  } finally {
    working.value = false
  }
}

const handleAssigneeChange = async (ticket: Ticket, event: Event) => {
  const select = event.target as HTMLSelectElement
  const assigneeId = select.value || null
  working.value = true
  actionError.value = ''
  try {
    await api.tickets.update(ticket.id, { assigneeId } as unknown as Partial<Ticket>)
    await refresh()
  } catch (err: any) {
    actionError.value = err?.response?.data?.detail || 'No se pudo asignar el usuario al ticket.'
  } finally {
    working.value = false
  }
}

// =====================================================================
// CLASES CSS
// =====================================================================

const statusLabel = (status: string): string =>
  ({ TODO: 'Por hacer', IN_PROGRESS: 'En progreso', BLOCKED: 'Bloqueado', REDIRECTED: 'Redirigido', DONE: 'Completado', COMPLETED: 'Completado' })[status] ?? status

const priorityLabel = (priority: string): string =>
  ({ LOW: 'Baja', MEDIUM: 'Media', HIGH: 'Alta', URGENT: 'Urgente' })[priority] ?? priority

const statusClass = (status: string): string =>
  ({
    TODO: 'bg-slate-500/20 text-slate-300',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-300',
    BLOCKED: 'bg-red-500/20 text-red-300',
    REDIRECTED: 'bg-amber-500/20 text-amber-300',
    DONE: 'bg-emerald-500/20 text-emerald-300',
    COMPLETED: 'bg-emerald-500/20 text-emerald-300'
  })[status] ?? 'bg-slate-500/20 text-slate-300'

const priorityClass = (priority: string): string =>
  ({
    LOW: 'bg-slate-500/20 text-slate-300',
    MEDIUM: 'bg-yellow-500/20 text-yellow-300',
    HIGH: 'bg-orange-500/20 text-orange-300',
    URGENT: 'bg-red-500/20 text-red-300'
  })[priority] ?? 'bg-slate-500/20 text-slate-300'

// =====================================================================
// INIT
// =====================================================================

onMounted(async () => {
  if (canAssignTickets.value) {
    try {
      const res: any = await api.users.list({ limit: 100 })
      availableUsers.value = Array.isArray(res) ? res : (res?.items ?? res?.data ?? [])
    } catch (e) {
      console.error('Error cargando usuarios:', e)
    }
  }
})
</script>
