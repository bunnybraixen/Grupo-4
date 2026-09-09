<template>
  <div class="flex flex-col min-h-screen bg-[var(--bg-app)]">
    <!-- Global header -->
    <AppHeader />

    <!-- Page content -->
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Page header: title + application selector -->
      <header class="bg-[var(--bg-card)] border-b border-[var(--border-subtle)] px-6 py-5 sticky top-0 z-40">
      <div class="flex items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold text-[var(--text-primary)]">{{ t('teamAssignmentView.title') }}</h1>
          <p class="text-[var(--text-secondary)] text-sm mt-1">{{ t('teamAssignmentView.subtitle') }}</p>
        </div>
        <div class="flex items-center gap-3">
          <label class="text-sm font-medium text-[var(--text-secondary)]">{{ t('teamAssignmentView.applicationLabel') }}:</label>
          <select
            v-model="selectedAppId"
            @change="refreshData"
            class="px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--teal)]"
          >
            <option value="">{{ t('teamAssignmentView.selectOption') }}</option>
            <option v-for="app in applications" :key="app.id" :value="app.id">
              {{ app.name }}
            </option>
          </select>
        </div>
      </div>
    </header>

      <!-- Two-panel grid layout -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 flex-1 overflow-hidden">
      <!-- LEFT PANEL: Unassigned tickets -->
      <section class="bg-[var(--bg-card)] rounded-xl flex flex-col border border-[var(--border-subtle)] overflow-hidden">
        <div class="border-b border-[var(--border-subtle)] px-5 py-4 bg-[var(--bg-panel)]">
          <h2 class="text-lg font-bold text-[var(--text-primary)]">{{ t('teamAssignmentView.unassignedTickets') }}</h2>
          <p class="text-[var(--text-secondary)] text-sm mt-1">{{ filteredUnassigned.length }} {{ t('teamAssignmentView.ticketCount') }}</p>
        </div>

        <!-- Filters: Epic + Priority -->
        <div class="px-4 py-3 border-b border-[var(--border-subtle)] space-y-2">
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs font-medium text-[var(--text-muted)] mb-1">{{ t('teamAssignmentView.epicFilter') }}</label>
              <select
                v-model="epicFilter"
                class="w-full px-2 py-1 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--teal)]"
              >
                <option value="all">{{ t('teamAssignmentView.allEpics') }}</option>
                <option v-for="epic in allEpicTitles" :key="epic" :value="epic">
                  {{ epic }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-[var(--text-muted)] mb-1">{{ t('teamAssignmentView.priorityFilter') }}</label>
              <select
                v-model="priorityFilter"
                class="w-full px-2 py-1 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded text-sm text-[var(--text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--teal)]"
              >
                <option value="all">{{ t('teamAssignmentView.allPriorities') }}</option>
                <option value="LOW">{{ t('teamAssignmentView.lowPriority') }}</option>
                <option value="MEDIUM">{{ t('teamAssignmentView.mediumPriority') }}</option>
                <option value="HIGH">{{ t('teamAssignmentView.highPriority') }}</option>
                <option value="URGENT">{{ t('teamAssignmentView.urgentPriority') }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Ticket list -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div v-if="filteredUnassigned.length > 0">
            <div
              v-for="ticket in filteredUnassigned"
              :key="ticket.id"
              class="bg-[var(--bg-card)] rounded-lg p-4 border border-[var(--border-subtle)] hover:border-[var(--teal)]/50 transition-colors"
            >
              <div class="flex items-start justify-between gap-2 mb-2">
                <h3 class="font-semibold text-[var(--text-primary)] flex-1 line-clamp-2">{{ ticket.title }}</h3>
                <span :class="getPriorityBadgeClass(ticket.priority)" class="px-2 py-1 rounded text-xs font-bold whitespace-nowrap flex-shrink-0">
                  {{ getPriorityLabel(ticket.priority) }}
                </span>
              </div>

              <div v-if="ticket.epicTitle" class="text-sm text-[var(--text-secondary)] mb-1">
                📋 {{ ticket.epicTitle }}
              </div>

              <div v-if="ticket.dueDate" class="text-sm text-[var(--text-secondary)] mb-3">
                📅 {{ formatDate(ticket.dueDate) }}
              </div>

              <button
                @click="openAssignModal(ticket)"
                class="w-full px-3 py-2 bg-[var(--lime)] text-[var(--dark-gray)] font-semibold rounded-lg hover:bg-[var(--lime-90)] transition-colors text-sm"
              >
                {{ t('teamAssignmentView.assignButton') }}
              </button>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center h-full text-center py-8">
            <svg class="w-12 h-12 text-[var(--text-muted)] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-[var(--text-secondary)] font-medium">{{ t('teamAssignmentView.noUnassignedTickets') }}</p>
            <p class="text-[var(--text-muted)] text-sm mt-1">{{ t('teamAssignmentView.allDistributed') }}</p>
          </div>
        </div>
      </section>

      <!-- RIGHT PANEL: Developer workload -->
      <section class="bg-[var(--bg-card)] rounded-xl flex flex-col border border-[var(--border-subtle)] overflow-hidden">
        <div class="border-b border-[var(--border-subtle)] px-5 py-4 bg-[var(--bg-panel)]">
          <h2 class="text-lg font-bold text-[var(--text-primary)]">{{ t('teamAssignmentView.developerWorkload') }}</h2>
          <p class="text-[var(--text-secondary)] text-sm mt-1">{{ developerWorkload.length }} {{ t('teamAssignmentView.developerCount') }}</p>
        </div>

        <!-- Developer list -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div v-if="developerWorkload.length > 0">
            <div v-for="item in developerWorkload" :key="item.dev.id" class="bg-[var(--bg-card)] rounded-lg border border-[var(--border-subtle)] overflow-hidden">
              <!-- Developer header -->
              <div class="p-4">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <div class="flex items-center gap-3 flex-1 min-w-0">
                    <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm bg-gradient-to-br from-[var(--teal)] to-[var(--teal-dark)] flex-shrink-0">
                      {{ getInitials(item.dev.fullName) }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="font-semibold text-[var(--text-primary)] truncate">{{ item.dev.fullName }}</p>
                      <p class="text-xs text-[var(--text-secondary)] truncate">{{ item.dev.email }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 flex-shrink-0">
                    <span class="px-3 py-1 rounded-full text-xs font-bold" :style="{ backgroundColor: getWorkloadColor(item.tickets.length), color: item.tickets.length === 0 ? '#142730' : 'white' }">
                      {{ item.tickets.length }}
                    </span>
                    <button
                      @click="toggleExpanded(item.dev.id)"
                      class="p-1 hover:bg-[var(--bg-panel)] rounded transition-colors"
                    >
                      <svg class="w-5 h-5 text-[var(--text-muted)] transition-transform" :class="{ 'rotate-180': expandedDevIds.has(item.dev.id) }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7-7m0 0l-7 7m7-7v12" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Workload bar -->
                <div>
                  <div class="flex justify-between items-center mb-1">
                    <span class="text-xs font-medium text-[var(--text-muted)]">Carga</span>
                    <span class="text-xs font-semibold text-[var(--text-muted)]">{{ Math.round((item.tickets.length / 10) * 100) }}%</span>
                  </div>
                  <div class="h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                    <div class="h-full rounded-full transition-all" :style="{ width: `${Math.min((item.tickets.length / 10) * 100, 100)}%`, backgroundColor: getWorkloadColor(item.tickets.length) }"></div>
                  </div>
                </div>
              </div>

              <!-- Ticket list (expanded) -->
              <div v-if="expandedDevIds.has(item.dev.id) && item.tickets.length > 0" class="border-t border-[var(--border-subtle)] divide-y divide-[var(--border-subtle)]">
                <div
                  v-for="ticket in item.tickets"
                  :key="ticket.id"
                  class="p-3 flex items-center justify-between gap-2 hover:bg-[var(--bg-panel)] transition-colors"
                >
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-[var(--text-primary)] truncate">{{ ticket.title }}</p>
                    <p class="text-xs text-[var(--text-secondary)] truncate">{{ ticket.epicTitle || 'Sin épica' }}</p>
                  </div>
                  <button
                    @click="doUnassign(ticket.id)"
                    title="Desasignar"
                    class="p-1 hover:bg-[var(--priority-urg-bg)]/20 rounded transition-colors text-[var(--priority-urg-bg)] flex-shrink-0"
                  >
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
              <div v-else-if="item.tickets.length === 0" class="px-4 py-3 text-center text-[var(--text-muted)] text-sm border-t border-[var(--border-subtle)]">
                Sin tickets asignados
              </div>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center h-full text-center py-8">
            <svg class="w-12 h-12 text-[var(--text-muted)] mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-2a6 6 0 0112 0v2zm0 0h6v-2a6 6 0 00-9-5.697M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p class="text-[var(--text-secondary)] font-medium">No hay desarrolladores</p>
          </div>
        </div>
      </section>
      </div>

      <!-- Assignment modal -->
      <Teleport to="body">
      <Transition name="fade">
        <div v-if="assigningTicket" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div class="bg-[var(--bg-card)] rounded-xl shadow-2xl p-6 w-full max-w-md mx-4 border border-[var(--border-subtle)] max-h-96 overflow-y-auto">
            <h3 class="text-xl font-bold text-[var(--text-primary)] mb-2">Asignar Ticket</h3>
            <p class="text-[var(--text-secondary)] text-sm mb-4">{{ assigningTicket.title }}</p>

            <div class="space-y-2 mb-6">
              <button
                v-for="item in developerWorkload"
                :key="item.dev.id"
                @click="doAssign(item.dev.id)"
                class="w-full text-left p-3 border border-[var(--border-subtle)] rounded-lg hover:border-[var(--teal)] hover:bg-[var(--bg-panel)] transition-colors"
              >
                <div class="flex items-center justify-between gap-3">
                  <div class="flex items-center gap-3 flex-1 min-w-0">
                    <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold bg-gradient-to-br from-[var(--teal)] to-[var(--teal-dark)] flex-shrink-0">
                      {{ getInitials(item.dev.fullName) }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="font-semibold text-[var(--text-primary)] text-sm truncate">{{ item.dev.fullName }}</p>
                      <p class="text-xs text-[var(--text-secondary)]">{{ item.tickets.length }} ticket(s)</p>
                    </div>
                  </div>
                  <div class="w-12 h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden flex-shrink-0">
                    <div class="h-full rounded-full" :style="{ width: `${Math.min((item.tickets.length / 10) * 100, 100)}%`, backgroundColor: getWorkloadColor(item.tickets.length) }"></div>
                  </div>
                </div>
              </button>
            </div>

            <button
              @click="assigningTicket = null"
              class="w-full px-4 py-2 border border-[var(--border-subtle)] rounded-lg font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-panel)] transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      </Transition>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { eventBus } from '@/utils/eventBus'
import AppHeader from '@/components/layout/AppHeader.vue'
import type { Ticket } from '@/types'
import { TicketStatus } from '@/types'
import { useTeamStore } from '@/stores/team'
import { useApplicationsStore } from '@/stores/applications'
import { apiClient } from '@/services/api'

const { t } = useI18n()

const teamStore = useTeamStore()
const appsStore = useApplicationsStore()

const selectedAppId = ref<string>('')
const epicFilter = ref<string>('all')
const priorityFilter = ref<string>('all')
const expandedDevIds = ref<Set<string>>(new Set())
const assigningTicket = ref<Ticket | null>(null)
const allAppTickets = ref<Ticket[]>([])
const isLoading = ref(false)

/** Workload color per CS-035 spec */
function getWorkloadColor(count: number): string {
  if (count === 0) return '#A1A9AC'    // dark-gray-40
  if (count <= 3) return '#ADEA4B'     // lime
  if (count <= 5) return '#D6F4A5'     // lime-50
  return '#C1108B'                      // accent-warm-1
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function getPriorityBadgeClass(priority: string): string {
  const classMap: Record<string, string> = {
    LOW: 'bg-[var(--priority-low-bg)] text-[var(--priority-low-text)]',
    MEDIUM: 'bg-[var(--priority-med-bg)] text-white',
    HIGH: 'bg-[var(--priority-high-bg)] text-white',
    URGENT: 'bg-[var(--priority-urg-bg)] text-white',
  }
  return classMap[priority] || 'bg-[var(--priority-low-bg)]'
}

function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    LOW: 'Baja',
    MEDIUM: 'Media',
    HIGH: 'Alta',
    URGENT: 'Urgente',
  }
  return labels[priority] || 'Desconocida'
}

function formatDate(dateStr: string): string {
  const [y, m, d] = dateStr.split('T')[0].split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

const applications = computed(() => appsStore.applications)

const developerWorkload = computed(() =>
  teamStore.members
    .filter(m => m.role === 'DEVELOPER' || m.role === 'TEAM_LEADER')
    .map(dev => ({
      dev,
      tickets: allAppTickets.value.filter(t => t.assigneeId === dev.id && t.status !== TicketStatus.COMPLETED),
    }))
)

const filteredUnassigned = computed(() => {
  let list = teamStore.unassignedSortedByPriority
  if (epicFilter.value !== 'all') list = list.filter(t => t.epicTitle === epicFilter.value)
  if (priorityFilter.value !== 'all') list = list.filter(t => t.priority === priorityFilter.value)
  return list
})

const allEpicTitles = computed(() => [
  ...new Set(teamStore.unassignedTickets.map(t => t.epicTitle).filter(Boolean)),
])

async function refreshData() {
  if (!selectedAppId.value) return
  isLoading.value = true
  try {
    await Promise.all([
      teamStore.fetchUnassigned(selectedAppId.value).catch((e: unknown) => {
        console.error('Error fetching unassigned tickets:', e)
      }),
      apiClient.get<any>('/tickets/', { params: { application_id: selectedAppId.value } }).then(r => {
        const raw = r.data
        const items: any[] = Array.isArray(raw) ? raw : (raw?.items ?? raw?.data?.items ?? [])
        allAppTickets.value = items.map((t: any) => ({
          ...t,
          assigneeId: t.assigneeId ?? t.assignee_id,
          epicId: t.epicId ?? t.epic_id,
          epicTitle: t.epicTitle ?? t.epic_title,
          appName: t.appName ?? t.app_name,
          dueDate: t.dueDate ?? t.due_date,
          createdAt: t.createdAt ?? t.created_at,
          updatedAt: t.updatedAt ?? t.updated_at,
          timeSpentSeconds: t.timeSpentSeconds ?? t.time_spent_seconds,
        })) as Ticket[]
      }).catch((e: unknown) => {
        console.error('Error fetching app tickets:', e)
        allAppTickets.value = []
      }),
    ])
  } finally {
    isLoading.value = false
  }
}

function toggleExpanded(devId: string) {
  if (expandedDevIds.value.has(devId)) {
    expandedDevIds.value.delete(devId)
  } else {
    expandedDevIds.value.add(devId)
  }
}

function openAssignModal(ticket: Ticket) {
  assigningTicket.value = ticket
}

async function doAssign(devId: string) {
  if (!assigningTicket.value) return
  try {
    await teamStore.assignTicket(assigningTicket.value.id, devId)
    assigningTicket.value = null
    await refreshData()
  } catch (error) {
    console.error('Error assigning ticket:', error)
  }
}

async function doUnassign(ticketId: string) {
  try {
    await teamStore.unassignTicket(ticketId)
    await refreshData()
  } catch (error) {
    console.error('Error unassigning ticket:', error)
  }
}

function handleWsUpdate() {
  refreshData()
}

onMounted(async () => {
  await appsStore.fetchAll()
  if (appsStore.applications.length) {
    selectedAppId.value = appsStore.applications[0].id
  }
  try {
    await teamStore.fetchMembers()
  } catch (e: unknown) {
    console.error('Error cargando miembros del equipo:', e)
  }
  await refreshData()
  eventBus.on('ws-update', handleWsUpdate)
})

onUnmounted(() => {
  eventBus.off('ws-update', handleWsUpdate)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
