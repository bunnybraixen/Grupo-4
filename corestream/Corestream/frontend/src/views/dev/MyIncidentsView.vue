<!--
  ============================================================================
  MyIncidentsView.vue — Vista de Incidentes del Desarrollador
  ============================================================================

  Vista para que los desarrolladores vean y gestionen los incidentes que
  tienen asignados. Los incidentes se agrupan por estado en secciones
  colapsables, con acciones rápidas en cada tarjeta.

  Secciones (en orden de prioridad visual):
    1. Abiertos / Reabiertos — requieren atención inmediata
    2. En Progreso — actualmente trabajando en ellos
    3. En Revisión — esperando revisión del admin
    4. Resueltos / Cerrados — completados (colapsada por defecto)

  Cada tarjeta muestra:
    - Borde lateral coloreado según severidad
    - Título, categoría, fecha límite
    - Botones de acción contextual según el estado actual
    - Indicador de vencido si aplica

  Panel lateral de detalle al seleccionar un incidente.
  ============================================================================
-->
<template>
  <div class="flex h-full overflow-hidden">
    <!-- ===== COLUMNA PRINCIPAL ===== -->
    <div
      :class="[
        'flex-1 overflow-y-auto',
        selectedIncident ? 'mr-4' : '',
      ]"
    >
      <div class="p-6">
        <!-- Encabezado -->
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
              Mis Incidentes
            </h1>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Tickets bloqueados que esperan tu respuesta.
            </p>
          </div>
        </div>

        <div class="mb-5">
          <label for="incident-search" class="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">Buscar incidente o ticket</label>
          <input
            id="incident-search"
            v-model="searchQuery"
            type="search"
            placeholder="Título, descripción o proyecto..."
            class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
          />
        </div>

        <p v-if="actionError" class="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {{ actionError }}
        </p>

        <!-- Estado de carga -->
        <div v-if="store.isLoading" class="flex items-center justify-center py-20">
          <div class="flex flex-col items-center gap-3">
            <div class="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ $t?.('incidents.loading') || 'Cargando incidentes...' }}
            </p>
          </div>
        </div>

        <!-- Estado vacío: sin incidentes asignados -->
        <div
          v-else-if="blockedTickets.length === 0 && redirectedTickets.length === 0"
          class="flex flex-col items-center justify-center py-20 text-gray-400 dark:text-gray-500"
        >
          <svg class="w-16 h-16 mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-lg font-medium">
            {{ $t?.('incidents.noAssigned') || 'No tienes incidentes asignados' }}
          </p>
          <p class="text-sm mt-1">
            {{ $t?.('incidents.noAssignedHint') || 'Los incidentes aparecerán aquí cuando te sean asignados.' }}
          </p>
        </div>

        <!-- ===== SECCIONES POR ESTADO ===== -->
        <div v-else class="space-y-6">
          <p v-if="!searchedIncidents.length && !blockedTickets.length && !redirectedTickets.length" class="py-10 text-center text-sm text-gray-500 dark:text-gray-400">
            No hay incidentes ni tickets que coincidan con la búsqueda.
          </p>
          <!--
            Sección: Abiertos / Reabiertos
            Requieren atención inmediata del desarrollador.
          -->
          <section v-if="redirectedTickets.length" class="rounded-xl border-2 border-amber-400 bg-amber-50 p-4 dark:border-amber-700 dark:bg-amber-950/20">
            <h2 class="mb-3 text-base font-semibold text-amber-900 dark:text-amber-200">Redirecciones pendientes de respuesta</h2>
            <div class="space-y-2">
              <article v-for="ticket in redirectedTickets" :key="ticket.id" class="rounded-lg border border-amber-200 bg-white p-3 dark:border-amber-900 dark:bg-slate-900">
                <button type="button" class="text-left" @click="router.push({ name: 'Workbench' })">
                  <span class="block font-medium text-gray-900 dark:text-white">{{ ticket.title }}</span>
                  <span class="mt-1 block text-xs text-gray-500 dark:text-gray-400">{{ ticket.appName || ticket.epicTitle || 'Ticket redirigido' }}</span>
                </button>
                <div class="mt-3 flex gap-2">
                  <button type="button" :disabled="ticketActionLoading" class="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50" @click="answerRedirect(ticket.id, true)">Aceptar</button>
                  <button type="button" :disabled="ticketActionLoading" class="rounded-md border border-amber-500 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-200 disabled:opacity-50" @click="answerRedirect(ticket.id, false)">Rechazar</button>
                </div>
              </article>
            </div>
          </section>

          <section v-if="blockedTickets.length" class="rounded-xl border border-red-200 bg-white p-4 dark:border-red-900 dark:bg-slate-900">
            <h2 class="mb-3 text-base font-semibold text-gray-900 dark:text-white">Tickets bloqueados</h2>
            <div class="space-y-3">
              <article
                v-for="ticket in blockedTickets"
                :key="ticket.id"
                class="rounded-lg border border-gray-200 p-3 dark:border-slate-700"
              >
                <p class="font-medium text-gray-900 dark:text-white">{{ ticket.title }}</p>
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ ticket.appName || ticket.epicTitle || 'Ticket bloqueado' }}</p>
                <p v-if="ticket.description" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ ticket.description }}</p>
                <div class="mt-3 flex flex-wrap gap-2">
                  <input
                    v-model="resolutionDrafts[ticket.id]"
                    maxlength="500"
                    placeholder="Respuesta o resolución (mínimo 10 caracteres)"
                    class="min-w-[240px] flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs text-gray-900 outline-none focus:border-blue-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
                  />
                  <button
                    type="button"
                    :disabled="ticketActionLoading || (resolutionDrafts[ticket.id] || '').trim().length < 10"
                    class="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-50"
                    @click="resolveTicketBlock(ticket.id)"
                  >
                    Resolver y reanudar
                  </button>
                </div>
              </article>
            </div>
          </section>

          <!-- Secciones por estado removidas: la vista muestra solo tickets bloqueados -->

          <!--
            Sección: En Progreso
            Incidentes en los que el desarrollador está trabajando.
          -->

          <!--
            Sección: En Revisión
            Incidentes enviados para revisión por el admin.
          -->

          <!--
            Sección: Resueltos / Cerrados
            Historial de incidentes completados (colapsada por defecto).
          -->
        </div>
      </div>
    </div>

    <!-- ===== PANEL DE DETALLE LATERAL ===== -->
    <transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 translate-x-8"
      enter-to-class="opacity-100 translate-x-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-x-0"
      leave-to-class="opacity-0 translate-x-8"
    >
      <div
        v-if="selectedIncident"
        class="w-[420px] flex-shrink-0 overflow-hidden"
      >
        <IncidentDetailPanel
          :incident="selectedIncident"
          @close="selectedIncident = null"
          @update-status="onUpdateStatus"
          @resolve="onResolveIncident"
          @add-comment="onAddComment"
        />
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
/**
 * Script de la vista de incidentes del desarrollador.
 *
 * Agrupa los incidentes asignados al usuario por estado,
 * permitiendo acciones rápidas directas en cada tarjeta
 * y un panel de detalle para información completa.
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useIncidentsStore } from '@/stores/incidents'
import { useAuthStore } from '@/stores/auth'
import { useApplicationsStore } from '@/stores/applications'
import { useTeamsStore } from '@/stores/teams'
import { api } from '@/services/api'
import apiClient from '@/services/api'
import type { Ticket } from '@/types'
import type { Incident, IncidentStatus } from '@/types/incidents'
import { IncidentStatus as StatusEnum } from '@/types/incidents'
import IncidentDetailPanel from '@/components/incidents/IncidentDetailPanel.vue'
import IncidentStatusSection from '@/components/incidents/IncidentStatusSection.vue'

// === Store ===

const store = useIncidentsStore()
const authStore = useAuthStore()
const applicationsStore = useApplicationsStore()
const teamsStore = useTeamsStore()
const route = useRoute()
const router = useRouter()
const isTeamLeader = computed(() => authStore.isTeamLeader || authStore.isAdmin)
const searchQuery = ref('')
const workbenchTickets = ref<Ticket[]>([])
const teamBlockedTickets = ref<Ticket[]>([])
const ticketActionLoading = ref(false)
const actionError = ref('')

const matchesSearch = (value: string | undefined): boolean =>
  !searchQuery.value.trim() || (value ?? '').toLowerCase().includes(searchQuery.value.trim().toLowerCase())

const searchedIncidents = computed(() => store.myIncidents.filter((incident) =>
  matchesSearch(`${incident.title} ${incident.description ?? ''} ${incident.applicationName ?? ''}`)
))
const searchedTickets = computed(() => {
  const base = isTeamLeader.value
    ? [...workbenchTickets.value, ...teamBlockedTickets.value]
    : workbenchTickets.value
  const seen = new Set<string>()
  const merged = base.filter((ticket) => {
    if (seen.has(ticket.id)) return false
    seen.add(ticket.id)
    return true
  })
  return merged.filter((ticket) =>
    matchesSearch(`${ticket.title} ${ticket.description ?? ''} ${ticket.appName ?? ''} ${ticket.epicTitle ?? ''}`)
  )
})
const blockedTickets = computed(() => searchedTickets.value.filter((ticket) =>
  ['BLOCKED', 'BLOCKED_QUESTION'].includes(String(ticket.status))
))
const redirectedTickets = computed(() => searchedTickets.value.filter((ticket) => String(ticket.status) === 'REDIRECTED'))

const unwrapList = (response: any): any[] => {
  let node = response?.data ?? response
  if (node && typeof node === 'object' && 'data' in node) node = (node as any).data
  if (Array.isArray(node)) return node
  if (Array.isArray(node?.items)) return node.items
  if (Array.isArray(node?.data)) return node.data
  return []
}

const refreshWorkbenchTickets = async (): Promise<void> => {
  try {
    const response: any = await api.tickets.getMyWorkbench()
    workbenchTickets.value = unwrapList(response)
  } catch (error) {
    console.error('No se pudieron cargar los tickets bloqueados/redirigidos:', error)
    workbenchTickets.value = []
  }
}

/**
 * Team Leader: trae TODOS los bloqueados de los proyectos de su equipo,
 * sin importar a quién estén asignados. El workbench solo trae los propios,
 * por eso el ticket 12 (de dev@corestream) no le aparecía al líder.
 */
const refreshTeamBlockedTickets = async (): Promise<void> => {
  teamBlockedTickets.value = []
  if (!isTeamLeader.value) return
  try {
    teamsStore.loadFromStorage()
    const email = authStore.user?.email || localStorage.getItem('userEmail') || ''
    const appIds = new Set<string>()
    for (const team of teamsStore.getUserTeams(email)) {
      for (const appId of team.applicationIds ?? []) appIds.add(String(appId))
    }
    // Admin sin equipo: recorre todas las apps cargadas.
    if (appIds.size === 0 && authStore.isAdmin) {
      try { await applicationsStore.fetchAll() } catch { /* sigue con lo que haya */ }
      for (const app of applicationsStore.applications ?? []) appIds.add(String((app as any).id))
    }
    const collected: Ticket[] = []
    for (const appId of appIds) {
      let epics: any[] = []
      try { epics = unwrapList(await api.epics.listByApplication(appId)) } catch { continue }
      for (const epic of epics) {
        let tickets: any[] = []
        try { tickets = unwrapList(await api.tickets.listByEpic(String((epic as any).id))) } catch { continue }
        for (const t of tickets) {
          if (['BLOCKED', 'BLOCKED_QUESTION'].includes(String((t as any).status))) collected.push(t as Ticket)
        }
      }
    }
    teamBlockedTickets.value = collected
  } catch (error) {
    console.error('No se pudieron cargar los bloqueados del equipo:', error)
    teamBlockedTickets.value = []
  }
}

const answerRedirect = async (ticketId: string, accept: boolean): Promise<void> => {
  ticketActionLoading.value = true
  actionError.value = ''
  try {
    const action = accept ? 'accept-redirect' : 'reject-redirect'
    await apiClient.post(`/tickets/${ticketId}/${action}`)
    await Promise.all([refreshWorkbenchTickets(), refreshTeamBlockedTickets()])
  } catch (error: any) {
    console.error('Error actualizando redirección:', error?.response?.status, error?.response?.data || error)
    actionError.value = error?.response?.data?.detail || error?.message || 'No se pudo actualizar la redirección.'
  } finally {
    ticketActionLoading.value = false
  }
}

const resolutionDrafts = ref<Record<string, string>>({})

/**
 * Resuelve el bloqueo del ticket con el mismo flujo que el Builder/Workbench:
 * POST /tickets/{id}/resolve-question con la redacción escrita por el usuario.
 */
const resolveTicketBlock = async (ticketId: string): Promise<void> => {
  const resolution = (resolutionDrafts.value[ticketId] || '').trim()
  if (resolution.length < 10) return
  ticketActionLoading.value = true
  actionError.value = ''
  try {
    await apiClient.post(`/tickets/${ticketId}/resolve-question`, { resolution })
    delete resolutionDrafts.value[ticketId]
    await Promise.all([refreshWorkbenchTickets(), refreshTeamBlockedTickets()])
  } catch (error: any) {
    const data = error?.response?.data
    actionError.value =
      data?.detail ||
      data?.error ||
      `HTTP ${error?.response?.status ?? '?'}: ${error?.message ?? 'error desconocido'}`
    console.error('Error resolviendo bloqueo:', error?.response?.status, data || error)
  } finally {
    ticketActionLoading.value = false
  }
}

// === Estado local ===

/** Incidente seleccionado para mostrar en el panel lateral */
const selectedIncident = ref<Incident | null>(null)

// === Agrupación de incidentes por estado ===

/**
 * Incidentes abiertos (OPEN + REOPENED).
 * Estos son los que necesitan atención inmediata.
 */
const openIncidents = computed(() => {
  return searchedIncidents.value
    .filter((i) => i.status === StatusEnum.OPEN || i.status === StatusEnum.REOPENED)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes en progreso (IN_PROGRESS).
 * Actualmente siendo trabajados por el desarrollador.
 */
const inProgressIncidents = computed(() => {
  return searchedIncidents.value
    .filter((i) => i.status === StatusEnum.IN_PROGRESS)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes en revisión (UNDER_REVIEW).
 * Esperando aprobación del administrador.
 */
const underReviewIncidents = computed(() => {
  return searchedIncidents.value
    .filter((i) => i.status === StatusEnum.UNDER_REVIEW)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes resueltos o cerrados (RESOLVED + CLOSED).
 * Historial de trabajo completado.
 */
const resolvedIncidents = computed(() => {
  return searchedIncidents.value
    .filter((i) => i.status === StatusEnum.RESOLVED || i.status === StatusEnum.CLOSED)
    .sort((a, b) => {
      // Ordenar por fecha de resolución, más recientes primero
      const dateA = a.resolvedAt || a.updatedAt
      const dateB = b.resolvedAt || b.updatedAt
      return new Date(dateB).getTime() - new Date(dateA).getTime()
    })
})

/**
 * Resumen de contadores por estado para los badges superiores.
 */
const statusSummary = computed(() => [
  {
    label: 'Abiertos',
    count: openIncidents.value.length,
    bgClass: 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300',
    dotClass: 'bg-blue-500',
  },
  {
    label: 'En Progreso',
    count: inProgressIncidents.value.length,
    bgClass: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300',
    dotClass: 'bg-yellow-500',
  },
  {
    label: 'En Revisión',
    count: underReviewIncidents.value.length,
    bgClass: 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300',
    dotClass: 'bg-purple-500',
  },
  {
    label: 'Resueltos',
    count: resolvedIncidents.value.length,
    bgClass: 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300',
    dotClass: 'bg-green-500',
  },
])

// === Handlers ===

/**
 * Selecciona un incidente para ver sus detalles en el panel lateral.
 */
function onSelectIncident(incident: Incident) {
  selectedIncident.value = incident
}

/**
 * Ejecuta una acción rápida sobre un incidente desde los botones inline.
 * Las acciones disponibles dependen del estado actual del incidente:
 *   - OPEN/REOPENED → start (cambiar a IN_PROGRESS)
 *   - IN_PROGRESS → review (enviar a revisión)
 *   - UNDER_REVIEW → (sin acción rápida del dev, espera admin)
 *   - RESOLVED → reopen (si se encontró un nuevo problema)
 */
async function onQuickAction(incidentId: string, action: string) {
  actionError.value = ''
  try {
    switch (action) {
      case 'start':
        await store.start(incidentId)
        break
      case 'review':
        await store.review(incidentId)
        break
      case 'reopen':
        await store.reopen(incidentId)
        break
      case 'resolve': {
        const notes = window.prompt('Notas de resolución:')?.trim()
        if (!notes) return
        await store.resolve(incidentId, notes)
        break
      }
    }
    await store.fetchMyIncidents()
  } catch (error: any) {
    const data = error?.response?.data
    actionError.value =
      data?.detail ||
      data?.error ||
      `HTTP ${error?.response?.status ?? '?'}: ${error?.message ?? 'error desconocido'}`
    console.error('Error en acción de incidente:', error?.response?.status, data || error)
  }
}

/**
 * Handler para cambiar estado desde el panel de detalle.
 */
async function onUpdateStatus(incidentId: string, newStatus: IncidentStatus) {
  await store.update(incidentId, { status: newStatus })
  await store.fetchMyIncidents()
}

/**
 * Handler para resolver un incidente con notas.
 */
async function onResolveIncident(incidentId: string, notes: string, version?: string) {
  await store.resolve(incidentId, notes, version)
  await store.fetchMyIncidents()
}

/**
 * Handler para añadir un comentario.
 */
async function onAddComment(incidentId: string, content: string) {
  await store.addComment(incidentId, content)
}

// === Lifecycle ===

/**
 * Al montar la vista, carga los incidentes asignados al usuario actual.
 */
onMounted(async () => {
  searchQuery.value = String(route.query.search ?? '')
  await store.fetchMyIncidents()
  await Promise.all([refreshWorkbenchTickets(), refreshTeamBlockedTickets()])
  const incidentId = String(route.query.incident ?? '')
  if (incidentId) {
    selectedIncident.value = store.myIncidents.find((incident) => incident.id === incidentId) ?? null
    if (selectedIncident.value) {
      await new Promise((resolve) => requestAnimationFrame(() => resolve(undefined)))
      document.getElementById(`incident-${incidentId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
})
</script>