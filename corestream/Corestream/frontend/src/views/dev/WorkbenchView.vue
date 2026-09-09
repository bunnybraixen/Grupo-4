<!--
  Vista: WorkbenchView (The Workbench - Developer)
  
  Panel personal del desarrollador para ejecutar tareas.
  
  DISEÑO: Side-by-side layout
  ```
  ┌──────────────────────────────────┐
  │ AppHeader                        │
  ├──────────┬──────────────────────┤
  │ Tickets  │  Side Panel Drawer   │
  │ List     │  (40% width, Right)  │
  │          │                      │
  │ Epic 1   │  ┌────────────────┐  │
  │ - Task 1 │  │ Breadcrumbs    │  │
  │ - Task 2 │  │ Ticket Title   │  │
  │          │  │                │  │
  │ Epic 2   │  │ Description    │  │
  │ - Task 3 │  │ Subtasks List  │  │
  │          │  │                │  │
  │          │  │ ┌────────────┐ │  │
  │          │  │ │ Action Dock│ │  │
  │          │  │ │ (3 buttons)│ │  │
  │          │  │ └────────────┘ │  │
  │          │  └────────────────┘  │
  └──────────┴──────────────────────┘
  ```
  
  FEATURES:
  - Agrupamiento por épica
  - Filtros por estado (TODO, IN_PROGRESS, etc.)
  - Side panel drawer (no modal, mantiene contexto)
  - Timer display (corner right)
  - Breadcrumbs (App / Epic / Task)
  - ActionDock con 3 botones principales
  - Subtasks checklist
  - Activity log
  
  DEPENDENCIAS EXTERNAS:
  - useTicketsStore: Para obtener/actualizar tickets
  - useEpicsStore: Para contexto de épicas
  - useApplicationsStore: Para nombre de app
  - Timer service: Para contar tiempo
  - WebSocket: Para notificaciones en tiempo real
  
  NOTA: Este archivo depende de que el backend tenga:
  - GET /tickets/workbench (lista de tickets del usuario)
  - GET /tickets/by-epic/{epicId} (lista de tickets por épica)
  - GET /epics/by-app/{appId} (lista de épicas por app)
-->

<template>
  <!-- Developer Workbench Layout basado en wireframe -->
  <div class="flex flex-col h-screen bg-[var(--bg-app)]">
    <!-- Header con navegación y selector de idioma -->
    <AppHeader />

    <!-- Main layout: sidebar + content -->
    <div class="flex flex-1 overflow-hidden">
    <!-- Sidebar de aplicaciones -->
    <aside class="w-64 bg-[var(--bg-sidebar)] border-r border-[var(--border-subtle)] flex flex-col">
      <div class="p-4">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
            {{ applications.length }} {{ applications.length === 1 ? t('workbenchView.applicationSingular') : t('workbenchView.applicationPlural') }}
          </h2>
          <button
            v-if="isTeamLeaderOrAdmin"
            type="button"
            @click="openCreateAppModal"
            class="w-6 h-6 bg-[var(--lime)] text-[var(--dark-gray)] rounded flex items-center justify-center text-lg hover:opacity-90 transition-colors font-semibold"
          >+</button>
        </div>

        <!-- Opciones de ordenamiento -->
        <div class="mb-4">
          <select
            v-model="appSortBy"
            @change="sortApplications"
            class="w-full text-xs border border-[var(--border-subtle)] rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-[var(--teal)]/20 focus:border-[var(--teal)] bg-[var(--bg-panel)] text-[var(--text-primary)]"
          >
            <option value="default">{{ t('workbenchView.sortDefault') }}</option>
            <option value="pending">{{ t('workbenchView.sortPending') }}</option>
            <option value="delayed">{{ t('workbenchView.sortDelayed') }}</option>
          </select>
        </div>

        <!-- Lista de aplicaciones -->
        <div class="space-y-1">
          <button
            v-for="app in sortedApplications"
            :key="app.id"
            @click="selectApplication(app.id)"
            :class="[
              'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all',
              selectedAppId === app.id
                ? 'bg-[var(--bg-panel)] shadow-sm border border-[var(--teal)]/40'
                : 'hover:bg-[var(--bg-panel)]'
            ]"
          >
            <div
              class="h-9 w-9 shrink-0 rounded-xl flex items-center justify-center border border-[var(--border-subtle)]"
              :style="{ backgroundColor: app.color || '#06B7B2' }"
            >
              <AppIcon :icon="app.icon" :size="18" icon-class="text-white" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate text-[var(--text-primary)]">{{ app.name }}</p>
              <div class="flex items-center gap-2 text-xs">
                <span class="text-[var(--text-muted)]">{{ app.epicCount || 0 }} {{ t('workbenchView.epics') }}</span>
                <span v-if="app.pending > 0" class="px-1.5 py-0.5 bg-[var(--lime)]/10 text-[var(--lime)] rounded-full font-medium">
                  {{ app.pending }} {{ t('workbenchView.pending') }}
                </span>
                <span v-if="app.delayed > 0" class="px-1.5 py-0.5 bg-[var(--priority-urg-bg)]/10 text-[var(--priority-urg-bg)] rounded-full font-medium">
                  {{ app.delayed }} {{ t('workbenchView.delayed') }}
                </span>
              </div>
            </div>
          </button>
        </div>

        <!-- Archivadas -->
        <div class="mt-auto pt-4 border-t border-[var(--border-subtle)]">
          <button class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-[var(--text-muted)] hover:text-[var(--text-secondary)]">
            <span class="text-lg">📁</span>
            <span class="text-sm">{{ t('workbenchView.archivedApplications') }}</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-hidden">

      <!-- ============================================================ -->
      <!-- TABS: Mis Tickets / Por Épica                                -->
      <!-- ============================================================ -->
      <div class="flex-shrink-0 flex gap-0 px-6 bg-[var(--bg-card)] border-b border-[var(--border-subtle)]">
        <button
          @click="activeView = 'tickets'"
          :class="[
            'px-5 py-3.5 text-sm font-medium border-b-2 transition-colors',
            activeView === 'tickets'
              ? 'border-[var(--teal)] text-[var(--teal)]'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]',
          ]"
        >
          {{ t('workbenchView.myTickets') }}
        </button>
        <button
          @click="activeView = 'epics'"
          :class="[
            'px-5 py-3.5 text-sm font-medium border-b-2 transition-colors',
            activeView === 'epics'
              ? 'border-[var(--teal)] text-[var(--teal)]'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]',
          ]"
        >
          {{ t('workbenchView.byEpic') }}
        </button>
      </div>

      <!-- ============================================================ -->
      <!-- TAB: Mis Tickets — Dashboard con cards y filtros            -->
      <!-- ============================================================ -->
      <div v-if="activeView === 'tickets'" class="flex-1 overflow-hidden">
        <WorkbenchDashboard @ticketSelected="selectTicket" />
      </div>

      <!-- ============================================================ -->
      <!-- TAB: Por Épica — Vista original con EpicManager             -->
      <!-- ============================================================ -->
      <div v-else class="flex-1 overflow-auto">
        <!-- Header de la aplicación seleccionada -->
        <div v-if="selectedAppId" class="bg-[var(--bg-card)] border-b border-[var(--border-subtle)] px-6 py-4">
          <div class="flex items-center gap-4">
            <div
              class="h-12 w-12 shrink-0 rounded-xl flex items-center justify-center border border-[var(--border-subtle)]"
              :style="{ backgroundColor: selectedApplication?.color || '#06B7B2' }"
            >
              <AppIcon :icon="selectedApplication?.icon || 'Folder'" :size="24" icon-class="text-white" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-[var(--text-primary)]">{{ selectedApplication?.name }}</h1>
              <span class="px-2 py-1 bg-[var(--lime)]/10 text-[var(--lime)] text-xs font-medium rounded-full">{{ t('workbenchView.active') }}</span>
            </div>
          </div>
        </div>

        <!-- EpicManager para la aplicación seleccionada -->
        <div v-if="selectedAppId" class="p-6">
          <EpicManager
            :key="selectedAppId"
            :application-id="selectedAppId"
            @ticket-selected="selectTicket"
          />
        </div>

        <!-- Mensaje si no hay aplicación seleccionada -->
        <div
          v-else
          class="flex items-center justify-center h-full"
        >
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--bg-panel)] flex items-center justify-center">
              <span class="text-2xl text-[var(--text-muted)]">📱</span>
            </div>
            <h2 class="text-xl font-semibold text-[var(--text-primary)] mb-2">{{ t('workbenchView.selectApplication') }}</h2>
            <p class="text-[var(--text-secondary)] max-w-md">
              {{ t('workbenchView.selectApplicationDesc') }}
            </p>
          </div>
        </div>
      </div>

    </main>

      <!-- Ticket Panel: TicketSidePanel para TL/Admin (tiene UI de resolución), TicketPanel para Developer -->
      <TicketSidePanel
        v-if="isTeamLeaderOrAdmin && selectedTicket"
        :ticket="selectedTicket"
        :is-open="isPanelOpen"
        @close="isPanelOpen = false; selectedTicketId = null; selectedTicket = null"
        @ticket-updated="handleTicketUpdated"
      />
      <TicketPanel
        v-else
        :ticket="selectedTicket"
        :is-open="isPanelOpen"
        :developers="teamMembers"
        @close="isPanelOpen = false; selectedTicketId = null; selectedTicket = null"
        @updated="refreshTicket"
      />

      <!-- Modal: Nueva aplicación (TEAM_LEADER/ADMIN). El "+" de la barra
           lateral no tenía @click — botón muerto, nunca creó nada. Mismo
           componente que usa BuilderView (nombre, descripción, color e
           ícono) para que ambos flujos de creación queden idénticos. -->
      <ApplicationFormModal
        :open="showCreateAppModal"
        :title="t('builderView.newApplicationTitle')"
        :saving="creatingApp"
        :error="createAppError"
        :form="newAppForm"
        @close="closeCreateAppModal"
        @submit="submitCreateApp"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppIcon from '@/components/shared/AppIcon.vue'
import ApplicationFormModal from '@/components/shared/ApplicationFormModal.vue'
import WorkbenchDashboard from '@/components/workbench/WorkbenchDashboard.vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useApplicationsStore } from '@/stores/applications'
import { useTicketsStore } from '@/stores/tickets'
import { useWorkbenchTickets } from '@/composables/useWorkbenchTickets'
import type { Ticket } from '@/types'

const EpicManager = defineAsyncComponent(() =>
  import('@/components/workbench/EpicManager.vue')
)
const TicketPanel = defineAsyncComponent(() =>
  import('@/components/dev/TicketPanel.vue')
)
const TicketSidePanel = defineAsyncComponent(() =>
  import('@/components/workbench/TicketSidePanel.vue')
)

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const ticketsStore = useTicketsStore()
const applicationsStore = useApplicationsStore()

const isTeamLeaderOrAdmin = computed(() =>
  authStore.user?.role === 'TEAM_LEADER' || authStore.user?.role === 'ADMIN'
)

// Vista activa: 'tickets' muestra el dashboard de Mis Tickets, 'epics' muestra el EpicManager
const activeView = ref<'tickets' | 'epics'>('tickets')

const applications = ref<any[]>([])
const selectedAppId = ref('')
const appSortBy = ref('default')

// Modal "Nueva aplicación" (TEAM_LEADER/ADMIN)
const showCreateAppModal = ref(false)
const newAppForm = ref({ name: '', description: '', color: '#06B7B2', icon: 'Folder' })
const creatingApp = ref(false)
const createAppError = ref('')

// Ticket Panel state
const selectedTicketId = ref<string | null>(null)
const selectedTicket = ref<Ticket | null>(null)
const isPanelOpen = ref(false)
const teamMembers = ref<any[]>([])

// Get workbench tickets for calculating app counters
const { rawTickets } = useWorkbenchTickets()

// Computed para agregar contadores a aplicaciones
const applicationsWithCounters = computed(() => {
  return applications.value.map(app => {
    const appTickets = rawTickets.value.filter(t => t.epicId &&
      // Si tenemos appId en el ticket
      t.appName === app.name || t.appName === app.id
    )

    const pendingCount = appTickets.filter(t => t.status === 'TODO').length

    const overdueCount = appTickets.filter(t =>
      t.dueDate && new Date(t.dueDate) < new Date()
    ).length

    return {
      ...app,
      pending: pendingCount,
      delayed: overdueCount
    }
  })
})

// Computed para ordenar aplicaciones
const sortedApplications = computed(() => {
  const sorted = [...applicationsWithCounters.value]

  switch (appSortBy.value) {
    case 'pending':
      return sorted.sort((a, b) => (b.pending || 0) - (a.pending || 0))
    case 'delayed':
      return sorted.sort((a, b) => (b.delayed || 0) - (a.delayed || 0))
    default:
      return sorted
  }
})

// Computed para obtener la aplicación seleccionada
const selectedApplication = computed(() => {
  return applications.value.find(app => app.id === selectedAppId.value)
})

// Función para seleccionar aplicación
const selectApplication = (appId: string) => {
  selectedAppId.value = appId
}

// Función para ordenar aplicaciones (actualmente manejada por computed)
const sortApplications = () => {
  // La vista se actualiza automáticamente con el computed
}

// Seleccionar ticket y abrir panel; luego carga datos frescos (con timer_started_at de Redis)
const selectTicket = async (ticket: Ticket) => {
  selectedTicketId.value = ticket.id
  selectedTicket.value = ticket
  isPanelOpen.value = true
  try {
    const fresh = await api.tickets.getById(ticket.id)
    selectedTicket.value = fresh
  } catch {
    // no-op: ya se muestra el ticket con datos básicos
  }
}

// Refrescar ticket después de actualización
const refreshTicket = async (ticketId: string) => {
  try {
    const updated = await api.tickets.getById(ticketId)
    selectedTicket.value = updated
    const wbIndex = ticketsStore.myWorkbench.findIndex((t: any) => t.id === ticketId)
    if (wbIndex !== -1) {
      ticketsStore.myWorkbench[wbIndex] = updated
    }
  } catch (error) {
    console.error('Error al refrescar ticket:', error)
  }
}

// TicketSidePanel emite ticketUpdated con un objeto { ticketId, action, data }
// WorkbenchView necesita extraer el ID antes de llamar refreshTicket
const handleTicketUpdated = async (data: any) => {
  const id = typeof data === 'string' ? data : (data?.ticketId ?? selectedTicketId.value ?? '')
  if (id) await refreshTicket(id)
}

// Cargar aplicaciones del backend
const fetchApplications = async () => {
  try {
    const aplicaciones = await api.applications.list()
    applications.value = aplicaciones
  } catch (error) {
    console.error('Error al cargar aplicaciones:', error)
  }
}

const onAppChange = () => {
  // La lógica está manejada por el componente EpicManager
}

const openCreateAppModal = () => {
  newAppForm.value = { name: '', description: '', color: '#06B7B2', icon: 'Folder' }
  createAppError.value = ''
  showCreateAppModal.value = true
}

const closeCreateAppModal = () => {
  showCreateAppModal.value = false
}

const submitCreateApp = async () => {
  if (!newAppForm.value.name.trim()) return

  creatingApp.value = true
  createAppError.value = ''
  try {
    const created = await applicationsStore.create({ ...newAppForm.value })
    applications.value.push(created)
    selectedAppId.value = created.id
    showCreateAppModal.value = false
  } catch (error: any) {
    createAppError.value = error?.response?.data?.detail || 'Error al crear la aplicación'
  } finally {
    creatingApp.value = false
  }
}

// Abre el panel lateral para el ticketId que viene del query param de notificación
const openTicketFromQuery = async (ticketId: string | undefined) => {
  if (!ticketId) return
  try {
    const ticket = await api.tickets.getById(ticketId)
    selectedTicket.value = ticket
    selectedTicketId.value = ticket.id
    isPanelOpen.value = true
    activeView.value = 'tickets'
  } catch {
    // ticket no encontrado o sin permisos — ignorar silenciosamente
  }
  router.replace({ query: {} })
}

// Observa cambios en el query param para cuando el usuario ya está en esta vista
watch(
  () => route.query.ticketId as string | undefined,
  (ticketId) => { if (ticketId) openTicketFromQuery(ticketId) }
)

onMounted(async () => {
  fetchApplications()
  try {
    teamMembers.value = await api.tickets.getTeamMembers()
  } catch {
    // non-critical: redirection dropdown will be empty
  }
  await openTicketFromQuery(route.query.ticketId as string | undefined)
})
</script>

