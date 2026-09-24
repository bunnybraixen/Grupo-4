<!--
  Vista de Workbench (Developer & Team Leader)
  
  Muestra los proyectos y tareas asignados únicamente a los equipos del usuario actual.
  Permite ver la lista de proyectos, épicas con progreso y tickets.
  Permite a Developers y Team Leaders:
  - Iniciar tickets (TODO -> IN_PROGRESS)
  - Finalizar tickets (IN_PROGRESS -> DONE con PR)
  - Marcar/desmarcar subtareas y ver su progreso
  - Ver detalle completo del ticket
  Permite a Team Leaders (y Admin):
  - Asignar miembros del equipo a los tickets
-->
<template>
  <div class="p-8 max-w-6xl mx-auto text-[var(--text-primary)] space-y-6">
    <!-- Header banner del usuario y su equipo -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold">Mi Workbench</h1>
        <p class="mt-1 text-sm text-[var(--text-muted)]">
          Bienvenido {{ userName }}. Revisa los proyectos y tareas asignados a tu equipo.
        </p>
      </div>

      <div class="flex items-center gap-2 flex-wrap">
        <span class="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-400/30 uppercase tracking-wider">
          {{ userRole }}
        </span>
        <span v-for="team in userTeams" :key="team.id" class="px-3 py-1 rounded-full text-xs font-semibold bg-[var(--teal)]/20 text-[var(--teal)] border border-[var(--teal)]/40 flex items-center gap-1">
          👥 {{ team.name }}
        </span>
        <span v-if="userTeams.length === 0" class="px-3 py-1 rounded-full text-xs bg-slate-500/20 text-slate-300 border border-slate-500/30">
          Sin equipo asignado
        </span>
      </div>
    </div>

    <!-- Proyectos Asignados a mi Equipo -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold flex items-center gap-2">
          <span>🚀</span> Proyectos Asignados a mi Equipo ({{ teamApplications.length }})
        </h2>
      </div>

      <div v-if="teamApplications.length === 0" class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-[var(--text-muted)]">
        No tienes proyectos asignados actualmente a tu equipo.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="app in teamApplications"
          :key="app.id"
          @click="selectApp(app.id)"
          class="rounded-2xl border transition-all duration-200 cursor-pointer p-5 shadow-sm space-y-3"
          :class="[
            selectedAppId === app.id
              ? 'border-[var(--teal)] bg-[var(--teal)]/5 ring-2 ring-[var(--teal)]/40 shadow-md'
              : 'border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--teal)]/50'
          ]"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="flex items-center gap-2.5">
                <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: app.color || '#14b8a6' }"></span>
                <h3 class="font-bold text-lg text-[var(--text-primary)]">{{ app.name }}</h3>
              </div>
              <p class="text-xs text-[var(--text-muted)] mt-1 line-clamp-2">
                {{ app.description || 'Sin descripción disponible.' }}
              </p>
            </div>
            <span
              v-if="teamsStore.getTeamForApp(app.id)"
              class="px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 flex-shrink-0"
            >
              👥 {{ teamsStore.getTeamForApp(app.id)?.name }}
            </span>
          </div>

          <!-- Barra de Progreso del Proyecto -->
          <div class="mt-3 border-t border-[var(--border-subtle)] pt-3">
            <div class="flex items-center justify-between text-xs uppercase tracking-wider text-[var(--text-muted)] mb-1">
              <span>{{ getAppProgress(app.id).completedEpics }}/{{ getAppProgress(app.id).totalEpics }} Épicas listas</span>
              <span class="font-bold text-[var(--teal)]">{{ getAppProgress(app.id).percentage }}%</span>
            </div>

            <div class="h-2 w-full rounded-full overflow-hidden bg-[var(--bg-app)] border border-[var(--border-subtle)]">
              <div
                class="h-full rounded-full bg-gradient-to-r from-[var(--teal)] to-emerald-400 transition-all duration-300"
                :style="{ width: getAppProgress(app.id).percentage + '%' }"
              ></div>
            </div>

            <div class="mt-1 flex items-center justify-between text-[11px] text-[var(--text-muted)]">
              <span>{{ getAppProgress(app.id).completedTickets }}/{{ getAppProgress(app.id).totalTickets }} tickets completados</span>
              <span>{{ getAppProgress(app.id).remainingTickets }} pendientes</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Detalle del Proyecto Seleccionado (Épicas y Tickets) -->
    <div v-if="selectedApp" class="space-y-4 rounded-2xl border border-[var(--teal)]/40 bg-[var(--bg-card)] p-6 shadow-md">
      <div class="flex items-center justify-between gap-3 border-b border-[var(--border-subtle)] pb-4">
        <div>
          <span class="text-xs font-semibold text-[var(--teal)] uppercase tracking-wider">Proyecto Seleccionado</span>
          <h2 class="text-2xl font-bold text-[var(--text-primary)] mt-0.5">{{ selectedApp.name }}</h2>
        </div>
        <button
          @click="selectedAppId = null"
          class="px-3 py-1.5 rounded-lg text-xs border border-[var(--border-subtle)] bg-[var(--bg-app)] hover:border-[var(--teal)]"
        >
          Cerrar vista
        </button>
      </div>

      <p v-if="ticketError" class="p-3 text-xs text-red-400 bg-red-500/10 border border-red-500/30 rounded-lg">
        {{ ticketError }}
      </p>

      <div v-if="(appEpicsMap[selectedApp.id] ?? []).length === 0" class="text-center py-8 text-[var(--text-muted)] text-sm">
        Este proyecto no tiene épicas registradas.
      </div>

      <!-- Lista de Épicas del Proyecto -->
      <div
        v-for="(epic, index) in (appEpicsMap[selectedApp.id] ?? [])"
        :key="epic.id"
        class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-app)]/50 overflow-hidden"
      >
        <!-- Encabezado de la Épica -->
        <div class="p-4 bg-[var(--bg-card)]/60 flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-[var(--border-subtle)]">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <span class="text-xs text-[var(--text-muted)] font-mono">#{{ index + 1 }}</span>
              <h3 class="font-bold text-base text-[var(--text-primary)]">{{ epic.title }}</h3>
            </div>
            <p v-if="epic.description" class="text-xs text-[var(--text-muted)] mt-0.5">
              {{ epic.description }}
            </p>

            <!-- Barra de Progreso de la Épica -->
            <div class="mt-2 max-w-md">
              <div class="flex items-center justify-between text-[10px] uppercase tracking-wider text-[var(--text-muted)] mb-1">
                <span>{{ getEpicProgress(epic.id).completed }}/{{ getEpicProgress(epic.id).total }} tickets completados</span>
                <span class="font-semibold text-[var(--teal)]">{{ getEpicProgress(epic.id).percentage }}%</span>
              </div>
              <div class="h-2 w-full rounded-full overflow-hidden bg-[var(--bg-app)] border border-[var(--border-subtle)]">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all duration-300"
                  :style="{ width: getEpicProgress(epic.id).percentage + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <span
            :class="getEpicProgress(epic.id).isComplete ? 'bg-emerald-500/15 text-emerald-300 border-emerald-400/30' : 'bg-slate-500/15 text-slate-300 border-slate-400/30'"
            class="px-2.5 py-1 text-xs font-semibold rounded-full border self-start md:self-center"
          >
            {{ getEpicProgress(epic.id).isComplete ? 'ÉPICA COMPLETA' : `${getEpicProgress(epic.id).remaining} pendientes` }}
          </span>
        </div>

        <!-- Lista de Tickets de la Épica -->
        <div v-if="(epicTicketsMap[epic.id] ?? []).length === 0" class="p-4 text-xs text-[var(--text-muted)] italic">
          No hay tickets creados en esta épica.
        </div>

        <div v-else class="divide-y divide-[var(--border-subtle)]">
          <div
            v-for="ticket in (epicTicketsMap[epic.id] ?? [])"
            :key="ticket.id"
            class="p-4 space-y-3 bg-[var(--bg-card)]/30 hover:bg-[var(--bg-card)]/60 transition-colors"
          >
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div class="min-w-0 flex-1 space-y-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-semibold text-sm text-[var(--text-primary)]">{{ ticket.title }}</span>
                  <span :class="statusClass(ticket.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ statusLabel(ticket.status) }}
                  </span>
                  <span :class="priorityClass(ticket.priority)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ priorityLabel(ticket.priority) }}
                  </span>
                </div>

                <div class="flex items-center gap-3 text-xs text-[var(--text-muted)] flex-wrap">
                  <span v-if="ticket.assignee" class="flex items-center gap-1 font-medium text-[var(--teal)]">
                    👤 {{ ticket.assignee.fullName || ticket.assignee.email }}
                  </span>
                  <span v-else class="text-slate-400">👤 Sin asignar</span>
                  <span v-if="ticket.dueDate">📅 Fecha: {{ ticket.dueDate.slice(0, 10) }}</span>
                </div>

                <!-- Barra de progreso de subtareas -->
                <div v-if="getSubtaskStats(ticket).total > 0" class="mt-2 max-w-sm">
                  <div class="flex items-center justify-between text-[11px] text-[var(--text-muted)] mb-1">
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
              </div>

              <!-- Botones de Acción (Similares al Builder) -->
              <div class="flex flex-wrap items-center gap-2">
                <!-- Select de asignación para Team Leader o Admin -->
                <select
                  v-if="canAssignTickets"
                  :value="ticket.assigneeId || ''"
                  @change="handleAssigneeChange(ticket, $event)"
                  class="bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1 text-xs text-[var(--text-primary)] outline-none focus:border-[var(--teal)]"
                >
                  <option value="">👤 Asignar a...</option>
                  <option v-for="u in availableAssignees" :key="u.id" :value="u.id">
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
                  @click="toggleTicketDetail(ticket.id)"
                  class="px-3 py-1 rounded-lg text-xs bg-[var(--bg-app)] text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--teal)]"
                >
                  👁 Detalle
                </button>
              </div>
            </div>

            <!-- Panel de Subtareas -->
            <div v-if="openSubtasksFor === ticket.id" class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 space-y-2 mt-2">
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
              <div class="flex gap-2 pt-1 border-t border-[var(--border-subtle)]">
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

            <!-- Panel de Detalle del Ticket -->
            <div v-if="openDetailFor === ticket.id" class="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)] p-3 text-xs space-y-1.5 mt-2">
              <p><span class="text-[var(--text-muted)]">Descripción:</span> {{ ticket.description || 'Sin descripción' }}</p>
              <p><span class="text-[var(--text-muted)]">Épica:</span> {{ epic.title }}</p>
              <p><span class="text-[var(--text-muted)]">Asignado:</span> {{ ticket.assignee ? (ticket.assignee.fullName || ticket.assignee.email) : 'Sin asignar' }}</p>
              <p><span class="text-[var(--text-muted)]">PR Link:</span> {{ ticket.prLink || '—' }}</p>
              <p><span class="text-[var(--text-muted)]">Fecha límite:</span> {{ ticket.dueDate ? ticket.dueDate.slice(0, 10) : '—' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Componente de Mis Tickets (Workbench Dashboard) -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden shadow-sm">
      <WorkbenchDashboard />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApplicationsStore } from '@/stores/applications'
import { useEpicsStore } from '@/stores/epics'
import { useTicketsStore } from '@/stores/tickets'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import { api } from '@/services/api'
import WorkbenchDashboard from '@/components/workbench/WorkbenchDashboard.vue'
import type { Epic, Subtask, Ticket, User } from '@/types'

const applicationsStore = useApplicationsStore()
const epicsStore = useEpicsStore()
const ticketsStore = useTicketsStore()
const authStore = useAuthStore()
const teamsStore = useTeamsStore()

const selectedAppId = ref<string | null>(null)
const appEpicsMap = ref<Record<string, Epic[]>>({})
const epicTicketsMap = ref<Record<string, Ticket[]>>({})

const openSubtasksFor = ref<string | null>(null)
const openDetailFor = ref<string | null>(null)
const newSubtaskTitle = ref('')
const working = ref(false)
const ticketError = ref('')
const availableAssignees = ref<User[]>([])

const userName = computed(() => authStore.user?.fullName || localStorage.getItem('userName') || 'Desarrollador')
const userRole = computed(() => authStore.user?.role || localStorage.getItem('userRole') || 'DEVELOPER')
const userEmail = computed(() => authStore.user?.email || localStorage.getItem('userEmail') || 'dev@corestream.com')

const isGroupLeader = computed(() => userRole.value === 'GROUP_LEADER')
const isAdmin = computed(() => userRole.value === 'ADMIN')
const canAssignTickets = computed(() => isGroupLeader.value || isAdmin.value)

const userTeams = computed(() => teamsStore.getUserTeams(userEmail.value))

const selectedApp = computed(() =>
  teamApplications.value.find((a) => a.id === selectedAppId.value) ?? null
)

/**
 * Filtra aplicaciones activas que corresponden al equipo del usuario actual.
 * Proyectos archivados (isActive === false) NUNCA se muestran a developers o team leaders.
 */
const teamApplications = computed(() => {
  const active = applicationsStore.applications.filter((app) => app.isActive !== false)
  const isUserAdmin = isAdmin.value
  return active.filter((app) => teamsStore.isAppAssignedToUser(app.id, userEmail.value, isUserAdmin))
})

const selectApp = async (appId: string) => {
  selectedAppId.value = selectedAppId.value === appId ? null : appId
  ticketError.value = ''
  if (selectedAppId.value) {
    await loadAppMetrics(selectedAppId.value)
  }
}

const loadAppMetrics = async (appId: string) => {
  try {
    const epics = await epicsStore.fetchByApp(appId)
    appEpicsMap.value[appId] = epics
    await Promise.all(
      epics.map(async (epic) => {
        epicTicketsMap.value[epic.id] = await ticketsStore.fetchByEpic(epic.id)
      })
    )
  } catch (err) {
    console.error(`Error cargando métricas de aplicación ${appId}:`, err)
  }
}

const loadTicketsForEpic = async (epicId: string) => {
  epicTicketsMap.value[epicId] = await ticketsStore.fetchByEpic(epicId)
}

const getAppProgress = (appId: string) => {
  const epicsList = appEpicsMap.value[appId] ?? []
  const totalEpics = epicsList.length
  let totalTickets = 0
  let completedTickets = 0
  let completedEpics = 0

  for (const epic of epicsList) {
    const tickets = epicTicketsMap.value[epic.id] ?? []
    const epicTotal = tickets.length
    const epicCompleted = tickets.filter((t) => t.status === 'DONE' || t.status === 'COMPLETED').length

    totalTickets += epicTotal
    completedTickets += epicCompleted
    if (epicTotal > 0 && epicCompleted === epicTotal) {
      completedEpics++
    }
  }

  const remainingTickets = Math.max(totalTickets - completedTickets, 0)
  const percentage = totalTickets === 0
    ? (totalEpics === 0 ? 0 : Math.round((completedEpics / totalEpics) * 100))
    : Math.round((completedTickets / totalTickets) * 100)

  return {
    totalEpics,
    completedEpics,
    totalTickets,
    completedTickets,
    remainingTickets,
    percentage
  }
}

const getEpicProgress = (epicId: string) => {
  const tickets = epicTicketsMap.value[epicId] ?? []
  const total = tickets.length
  const completed = tickets.filter((t) => t.status === 'DONE' || t.status === 'COMPLETED').length
  const remaining = Math.max(total - completed, 0)
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)

  return {
    total,
    completed,
    remaining,
    percentage,
    isComplete: total > 0 && completed === total
  }
}

const getSubtaskStats = (ticket: Ticket) => {
  const subs = ticket.subtasks ?? []
  const total = subs.length
  const completed = subs.filter((s) => s.isCompleted).length
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)
  return { total, completed, percentage }
}

const startTicket = async (ticket: Ticket) => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
    await loadTicketsForEpic(ticket.epicId)
  } catch (err: any) {
    ticketError.value = err?.response?.data?.detail || 'No se pudo iniciar el ticket.'
  } finally {
    working.value = false
  }
}

const completeTicket = async (ticket: Ticket) => {
  const prLink = window.prompt('Enlace del Pull Request para finalizar el ticket (opcional):')
  if (prLink === null) return
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.complete(ticket.id, prLink.trim())
    await loadTicketsForEpic(ticket.epicId)
  } catch (err: any) {
    ticketError.value = err?.response?.data?.detail || 'No se pudo finalizar el ticket.'
  } finally {
    working.value = false
  }
}

const toggleSubtaskPanel = (ticketId: string) => {
  openSubtasksFor.value = openSubtasksFor.value === ticketId ? null : ticketId
  newSubtaskTitle.value = ''
}

const toggleTicketDetail = (ticketId: string) => {
  openDetailFor.value = openDetailFor.value === ticketId ? null : ticketId
}

const addSubtask = async (ticket: Ticket) => {
  const title = newSubtaskTitle.value.trim()
  if (!title) return
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.createSubtask(ticket.id, title)
    newSubtaskTitle.value = ''
    await loadTicketsForEpic(ticket.epicId)
  } catch (err: any) {
    ticketError.value = err?.response?.data?.detail || 'No se pudo crear la subtarea.'
  } finally {
    working.value = false
  }
}

const toggleSubtask = async (ticket: Ticket, sub: Subtask) => {
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.updateSubtask(ticket.id, sub.id, { isCompleted: !sub.isCompleted })
    await loadTicketsForEpic(ticket.epicId)
  } catch (err: any) {
    ticketError.value = err?.response?.data?.detail || 'No se pudo actualizar la subtarea.'
  } finally {
    working.value = false
  }
}

const handleAssigneeChange = async (ticket: Ticket, event: Event) => {
  const select = event.target as HTMLSelectElement
  const assigneeId = select.value || null
  working.value = true
  ticketError.value = ''
  try {
    await api.tickets.update(ticket.id, { assigneeId } as unknown as Partial<Ticket>)
    await loadTicketsForEpic(ticket.epicId)
  } catch (err: any) {
    ticketError.value = err?.response?.data?.detail || 'No se pudo asignar el usuario al ticket.'
  } finally {
    working.value = false
  }
}

const loadUsers = async () => {
  try {
    const res: any = await api.users.list({ limit: 100 })
    availableAssignees.value = Array.isArray(res) ? res : (res?.items ?? res?.data ?? [])
  } catch (err) {
    console.error('Error cargando usuarios:', err)
  }
}

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

onMounted(async () => {
  teamsStore.loadFromStorage()
  try {
    await applicationsStore.fetchAll()
    await Promise.all(teamApplications.value.map((app) => loadAppMetrics(app.id)))
    if (canAssignTickets.value) {
      await loadUsers()
    }
  } catch (err) {
    console.error('Error cargando workbench:', err)
  }
})
</script>
