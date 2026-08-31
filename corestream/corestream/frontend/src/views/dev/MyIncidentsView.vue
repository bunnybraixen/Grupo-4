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
              {{ $t?.('incidents.myIncidents') || 'Mis Incidentes' }}
            </h1>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {{ $t?.('incidents.myIncidentsSubtitle') || 'Incidentes asignados a ti. Gestiona su progreso y resolución.' }}
            </p>
          </div>

          <!-- Resumen rápido: contadores por estado -->
          <div class="flex items-center gap-3">
            <div
              v-for="summary in statusSummary"
              :key="summary.label"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
              :class="summary.bgClass"
            >
              <span :class="['w-2 h-2 rounded-full', summary.dotClass]"></span>
              <span>{{ summary.count }}</span>
              <span class="hidden sm:inline">{{ summary.label }}</span>
            </div>
          </div>
        </div>

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
          v-else-if="store.myIncidents.length === 0"
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
          <!--
            Sección: Abiertos / Reabiertos
            Requieren atención inmediata del desarrollador.
          -->
          <IncidentStatusSection
            v-if="openIncidents.length > 0"
            :title="$t?.('incidents.sections.open') || 'Abiertos'"
            :count="openIncidents.length"
            :incidents="openIncidents"
            dot-class="bg-blue-500"
            header-class="border-blue-400"
            :default-open="true"
            @select="onSelectIncident"
            @action="onQuickAction"
          />

          <!--
            Sección: En Progreso
            Incidentes en los que el desarrollador está trabajando.
          -->
          <IncidentStatusSection
            v-if="inProgressIncidents.length > 0"
            :title="$t?.('incidents.sections.inProgress') || 'En Progreso'"
            :count="inProgressIncidents.length"
            :incidents="inProgressIncidents"
            dot-class="bg-yellow-500"
            header-class="border-yellow-400"
            :default-open="true"
            @select="onSelectIncident"
            @action="onQuickAction"
          />

          <!--
            Sección: En Revisión
            Incidentes enviados para revisión por el admin.
          -->
          <IncidentStatusSection
            v-if="underReviewIncidents.length > 0"
            :title="$t?.('incidents.sections.underReview') || 'En Revisión'"
            :count="underReviewIncidents.length"
            :incidents="underReviewIncidents"
            dot-class="bg-purple-500"
            header-class="border-purple-400"
            :default-open="true"
            @select="onSelectIncident"
            @action="onQuickAction"
          />

          <!--
            Sección: Resueltos / Cerrados
            Historial de incidentes completados (colapsada por defecto).
          -->
          <IncidentStatusSection
            v-if="resolvedIncidents.length > 0"
            :title="$t?.('incidents.sections.resolved') || 'Resueltos / Cerrados'"
            :count="resolvedIncidents.length"
            :incidents="resolvedIncidents"
            dot-class="bg-green-500"
            header-class="border-green-400"
            :default-open="false"
            @select="onSelectIncident"
            @action="onQuickAction"
          />
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
import { useIncidentsStore } from '@/stores/incidents'
import type { Incident, IncidentStatus } from '@/types/incidents'
import { IncidentStatus as StatusEnum } from '@/types/incidents'
import IncidentDetailPanel from '@/components/incidents/IncidentDetailPanel.vue'
import IncidentStatusSection from '@/components/incidents/IncidentStatusSection.vue'

// === Store ===

const store = useIncidentsStore()

// === Estado local ===

/** Incidente seleccionado para mostrar en el panel lateral */
const selectedIncident = ref<Incident | null>(null)

// === Agrupación de incidentes por estado ===

/**
 * Incidentes abiertos (OPEN + REOPENED).
 * Estos son los que necesitan atención inmediata.
 */
const openIncidents = computed(() => {
  return store.myIncidents
    .filter((i) => i.status === StatusEnum.OPEN || i.status === StatusEnum.REOPENED)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes en progreso (IN_PROGRESS).
 * Actualmente siendo trabajados por el desarrollador.
 */
const inProgressIncidents = computed(() => {
  return store.myIncidents
    .filter((i) => i.status === StatusEnum.IN_PROGRESS)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes en revisión (UNDER_REVIEW).
 * Esperando aprobación del administrador.
 */
const underReviewIncidents = computed(() => {
  return store.myIncidents
    .filter((i) => i.status === StatusEnum.UNDER_REVIEW)
    .sort((a, b) => a.priorityOrder - b.priorityOrder)
})

/**
 * Incidentes resueltos o cerrados (RESOLVED + CLOSED).
 * Historial de trabajo completado.
 */
const resolvedIncidents = computed(() => {
  return store.myIncidents
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
  }
  // Recargar incidentes del usuario
  await store.fetchMyIncidents()
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
  await store.fetchMyIncidents()
})
</script>
