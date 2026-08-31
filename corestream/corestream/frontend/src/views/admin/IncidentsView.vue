<!--
  ============================================================================
  IncidentsView.vue — Vista Principal de Gestión de Incidentes (Admin)
  ============================================================================

  Vista completa para que el Administrador gestione incidentes de todas las
  aplicaciones. Incluye:

    1. Tarjetas de resumen (KPIs): Total Abiertos, Errores Críticos,
       En Progreso, Resueltos este mes, Vencidos
    2. Barra de filtros: búsqueda, severidad (chips), estado, asignado,
       aplicación, botón "Nuevo Incidente"
    3. Tablero Kanban agrupado por categoría (4 columnas)
    4. Panel lateral de detalle del incidente seleccionado
    5. Modal de creación de nuevo incidente

  Integra los componentes:
    - IncidentKanbanBoard (tablero principal)
    - IncidentDetailPanel (panel lateral derecho)
    - CreateIncidentModal (modal de creación)

  Usa el store de incidentes para toda la gestión de estado.
  ============================================================================
-->
<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- ===== ENCABEZADO + KPIs ===== -->
    <div class="flex-shrink-0 px-6 pt-6 pb-4">
      <!-- Título y botón de nuevo incidente -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
            {{ $t?.('incidents.title') || 'Gestión de Incidentes' }}
          </h1>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ $t?.('incidents.subtitle') || 'Administra, prioriza y da seguimiento a los incidentes de tus proyectos' }}
          </p>
        </div>

        <!-- Botón para crear nuevo incidente -->
        <button
          @click="showCreateModal = true"
          class="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
        >
          <!-- Icono + -->
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          {{ $t?.('incidents.newIncident') || 'Nuevo Incidente' }}
        </button>
      </div>

      <!-- ===== TARJETAS DE MÉTRICAS (KPIs) ===== -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
        <!-- KPI: Total Abiertos -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
                {{ $t?.('incidents.kpi.totalOpen') || 'Total Abiertos' }}
              </p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">
                {{ store.openCount }}
              </p>
            </div>
          </div>
        </div>

        <!-- KPI: Errores Críticos -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
                {{ $t?.('incidents.kpi.critical') || 'Errores Críticos' }}
              </p>
              <p class="text-xl font-bold text-red-600 dark:text-red-400">
                {{ store.criticalIncidents.length }}
              </p>
            </div>
          </div>
        </div>

        <!-- KPI: En Progreso -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-yellow-100 dark:bg-yellow-900/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
                {{ $t?.('incidents.kpi.inProgress') || 'En Progreso' }}
              </p>
              <p class="text-xl font-bold text-yellow-600 dark:text-yellow-400">
                {{ inProgressCount }}
              </p>
            </div>
          </div>
        </div>

        <!-- KPI: Resueltos -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
                {{ $t?.('incidents.kpi.resolved') || 'Resueltos' }}
              </p>
              <p class="text-xl font-bold text-green-600 dark:text-green-400">
                {{ resolvedCount }}
              </p>
            </div>
          </div>
        </div>

        <!-- KPI: Vencidos -->
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">
                {{ $t?.('incidents.kpi.overdue') || 'Vencidos' }}
              </p>
              <p class="text-xl font-bold text-orange-600 dark:text-orange-400">
                {{ store.overdueIncidents.length }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== BARRA DE FILTROS ===== -->
      <div class="flex flex-wrap items-center gap-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-4 py-3">
        <!-- Buscador de texto -->
        <div class="relative flex-1 min-w-[200px]">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t?.('incidents.searchPlaceholder') || 'Buscar incidentes...'"
            class="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:text-white placeholder-gray-400"
            @input="onSearchChange"
          />
        </div>

        <!-- Separador vertical -->
        <div class="hidden md:block w-px h-8 bg-gray-200 dark:bg-gray-600"></div>

        <!-- Chips de severidad -->
        <div class="flex items-center gap-1.5">
          <span class="text-xs text-gray-500 dark:text-gray-400 mr-1">
            {{ $t?.('incidents.severity') || 'Severidad' }}:
          </span>
          <button
            v-for="sev in severityOptions"
            :key="sev.value"
            @click="toggleSeverityFilter(sev.value)"
            :class="[
              'px-2.5 py-1 rounded-full text-xs font-medium transition-all',
              activeSeverity === sev.value
                ? sev.activeClass
                : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
            ]"
          >
            {{ sev.label }}
          </button>
        </div>

        <!-- Separador vertical -->
        <div class="hidden md:block w-px h-8 bg-gray-200 dark:bg-gray-600"></div>

        <!-- Selector de estado -->
        <select
          v-model="activeStatus"
          @change="onStatusChange"
          class="px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg dark:text-white focus:ring-2 focus:ring-blue-500"
        >
          <option value="">{{ $t?.('incidents.allStatuses') || 'Todos los estados' }}</option>
          <option value="OPEN">{{ $t?.('incidents.status.open') || 'Abierto' }}</option>
          <option value="IN_PROGRESS">{{ $t?.('incidents.status.inProgress') || 'En Progreso' }}</option>
          <option value="UNDER_REVIEW">{{ $t?.('incidents.status.underReview') || 'En Revisión' }}</option>
          <option value="RESOLVED">{{ $t?.('incidents.status.resolved') || 'Resuelto' }}</option>
          <option value="CLOSED">{{ $t?.('incidents.status.closed') || 'Cerrado' }}</option>
          <option value="REOPENED">{{ $t?.('incidents.status.reopened') || 'Reabierto' }}</option>
        </select>

        <!-- Botón limpiar filtros (visible si hay filtros activos) -->
        <button
          v-if="hasActiveFilters"
          @click="clearAllFilters"
          class="px-3 py-2 text-xs text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 transition-colors"
        >
          {{ $t?.('incidents.clearFilters') || 'Limpiar filtros' }}
        </button>
      </div>
    </div>

    <!-- ===== CONTENIDO PRINCIPAL: KANBAN + PANEL DETALLE ===== -->
    <div class="flex-1 flex overflow-hidden px-6 pb-6">
      <!--
        Tablero Kanban (ocupa el espacio disponible).
        Si hay un incidente seleccionado, el tablero se comprime
        para dar espacio al panel de detalle.
      -->
      <div
        :class="[
          'flex-1 overflow-auto transition-all duration-300',
          store.selectedIncident ? 'mr-4' : '',
        ]"
      >
        <!-- Estado de carga -->
        <div v-if="store.isLoading" class="flex items-center justify-center h-full">
          <div class="flex flex-col items-center gap-3">
            <div class="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            <p class="text-sm text-gray-500 dark:text-gray-400">
              {{ $t?.('incidents.loading') || 'Cargando incidentes...' }}
            </p>
          </div>
        </div>

        <!-- Tablero Kanban -->
        <IncidentKanbanBoard
          v-else
          :incidents="store.filteredIncidents"
          @select-incident="onSelectIncident"
          @reorder="onReorderIncidents"
        />
      </div>

      <!--
        Panel de detalle del incidente seleccionado.
        Se muestra como panel lateral deslizante desde la derecha.
        Ancho fijo de 420px con animación de entrada/salida.
      -->
      <transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-8"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-8"
      >
        <div
          v-if="store.selectedIncident"
          class="w-[420px] flex-shrink-0 overflow-hidden"
        >
          <IncidentDetailPanel
            :incident="store.selectedIncident"
            @close="store.selectIncident(null)"
            @update-status="onUpdateStatus"
            @assign="onAssignIncident"
            @resolve="onResolveIncident"
            @add-comment="onAddComment"
          />
        </div>
      </transition>
    </div>

    <!-- ===== MODAL DE CREACIÓN ===== -->
    <CreateIncidentModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @created="onIncidentCreated"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * Script de la vista principal de incidentes del Administrador.
 *
 * Orquesta todos los componentes del módulo de incidentes:
 * - Carga datos al montar el componente
 * - Gestiona filtros y búsqueda con debounce
 * - Delega operaciones CRUD al store de Pinia
 * - Coordina la comunicación entre Kanban, panel detalle y modal
 */
import { ref, computed, onMounted } from 'vue'
import { useIncidentsStore } from '@/stores/incidents'
import type { Incident, IncidentCategory, IncidentSeverity, IncidentStatus } from '@/types/incidents'
import { IncidentStatus as StatusEnum } from '@/types/incidents'
import IncidentKanbanBoard from '@/components/incidents/IncidentKanbanBoard.vue'
import IncidentDetailPanel from '@/components/incidents/IncidentDetailPanel.vue'
import CreateIncidentModal from '@/components/incidents/CreateIncidentModal.vue'

// === Store ===

/** Store de Pinia para gestionar el estado global de incidentes */
const store = useIncidentsStore()

// === Estado local de la vista ===

/** Controla la visibilidad del modal de creación de incidentes */
const showCreateModal = ref(false)

/** Texto de búsqueda en el campo de filtro */
const searchQuery = ref('')

/** Severidad activa para el filtro por chips */
const activeSeverity = ref<IncidentSeverity | ''>('')

/** Estado activo para el filtro por select */
const activeStatus = ref<IncidentStatus | ''>('')

/** Timer para debounce en la búsqueda por texto */
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

// === Opciones de filtro ===

/**
 * Configuración de los chips de severidad.
 * Cada chip tiene su valor, etiqueta y clase CSS cuando está activo.
 */
const severityOptions: Array<{
  value: IncidentSeverity
  label: string
  activeClass: string
}> = [
  {
    value: 'CRITICAL' as IncidentSeverity,
    label: 'Crítico',
    activeClass: 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300 ring-1 ring-red-300 dark:ring-red-700',
  },
  {
    value: 'HIGH' as IncidentSeverity,
    label: 'Alto',
    activeClass: 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300 ring-1 ring-orange-300 dark:ring-orange-700',
  },
  {
    value: 'MEDIUM' as IncidentSeverity,
    label: 'Medio',
    activeClass: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300 ring-1 ring-yellow-300 dark:ring-yellow-700',
  },
  {
    value: 'LOW' as IncidentSeverity,
    label: 'Bajo',
    activeClass: 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300 ring-1 ring-green-300 dark:ring-green-700',
  },
]

// === Computados ===

/**
 * Conteo de incidentes en estado IN_PROGRESS.
 * Incluye tanto IN_PROGRESS como REOPENED para reflejar trabajo activo.
 */
const inProgressCount = computed(() => {
  return store.incidents.filter(
    (i) => i.status === StatusEnum.IN_PROGRESS || i.status === StatusEnum.REOPENED
  ).length
})

/**
 * Conteo de incidentes resueltos.
 * Incluye RESOLVED y CLOSED.
 */
const resolvedCount = computed(() => {
  return store.incidents.filter(
    (i) => i.status === StatusEnum.RESOLVED || i.status === StatusEnum.CLOSED
  ).length
})

/**
 * Indica si hay filtros activos.
 * Se usa para mostrar/ocultar el botón de limpiar filtros.
 */
const hasActiveFilters = computed(() => {
  return (
    searchQuery.value !== '' ||
    activeSeverity.value !== '' ||
    activeStatus.value !== ''
  )
})

// === Handlers de filtros ===

/**
 * Handler de cambio en el campo de búsqueda.
 * Aplica debounce de 300ms para evitar llamadas excesivas al store.
 */
function onSearchChange() {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    store.setFilters({ search: searchQuery.value || undefined })
  }, 300)
}

/**
 * Alterna el filtro de severidad.
 * Si se hace clic en el chip activo, se desactiva.
 * Si se hace clic en otro chip, se activa ese y desactiva el anterior.
 */
function toggleSeverityFilter(severity: IncidentSeverity) {
  if (activeSeverity.value === severity) {
    activeSeverity.value = ''
    store.clearFilter('severity')
  } else {
    activeSeverity.value = severity
    store.setFilters({ severity })
  }
}

/**
 * Handler de cambio en el selector de estado.
 * Actualiza el filtro de estado en el store.
 */
function onStatusChange() {
  if (activeStatus.value) {
    store.setFilters({ status: activeStatus.value as IncidentStatus })
  } else {
    store.clearFilter('status')
  }
}

/**
 * Limpia todos los filtros activos y restablece la vista.
 */
function clearAllFilters() {
  searchQuery.value = ''
  activeSeverity.value = ''
  activeStatus.value = ''
  store.clearFilters()
}

// === Handlers de interacción ===

/**
 * Handler al seleccionar un incidente en el tablero Kanban.
 * Establece el incidente seleccionado en el store para abrir el panel de detalle.
 */
function onSelectIncident(incident: Incident) {
  store.selectIncident(incident)
}

/**
 * Handler al reordenar incidentes dentro de una columna del Kanban.
 * Emite los nuevos órdenes de prioridad al store para persistir.
 * @param category — Categoría de la columna donde se reordenó
 * @param orderedIds — Lista ordenada de IDs de incidentes
 */
async function onReorderIncidents(category: IncidentCategory, orderedIds: string[]) {
  // Actualizar el priority_order de cada incidente según su posición
  for (let i = 0; i < orderedIds.length; i++) {
    await store.changePriority(orderedIds[i], i + 1)
  }
}

/**
 * Handler al cambiar el estado de un incidente desde el panel de detalle.
 * Delega la actualización al store correspondiente.
 */
async function onUpdateStatus(incidentId: string, newStatus: IncidentStatus) {
  await store.update(incidentId, { status: newStatus })
}

/**
 * Handler al asignar un incidente a un desarrollador.
 */
async function onAssignIncident(incidentId: string, userId: string) {
  await store.assign(incidentId, userId)
}

/**
 * Handler al resolver un incidente con notas y versión.
 */
async function onResolveIncident(incidentId: string, notes: string, version?: string) {
  await store.resolve(incidentId, notes, version)
}

/**
 * Handler al añadir un comentario a un incidente.
 */
async function onAddComment(incidentId: string, content: string) {
  await store.addComment(incidentId, content)
}

/**
 * Handler al crear un nuevo incidente exitosamente.
 * Cierra el modal y recarga los datos del tablero.
 */
function onIncidentCreated() {
  showCreateModal.value = false
  // Recargar incidentes para reflejar el nuevo
  store.fetchAll()
}

// === Lifecycle ===

/**
 * Al montar la vista:
 * 1. Carga todos los incidentes del servidor
 * 2. Carga las estadísticas del dashboard
 */
onMounted(async () => {
  await Promise.all([
    store.fetchAll(),
    store.fetchDashboard(),
  ])
})
</script>
