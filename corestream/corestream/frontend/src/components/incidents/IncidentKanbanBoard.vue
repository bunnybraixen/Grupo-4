<!--
  ============================================================================
  IncidentKanbanBoard.vue — Tablero Kanban de Incidentes por Categoría
  ============================================================================

  Tablero estilo Kanban con 4 columnas, una por cada categoría de incidente:
    1. Nueva Funcionalidad (azul) — solicitudes de features nuevos
    2. Error Crítico (rojo) — bugs que bloquean el uso del sistema
    3. Error No Crítico (naranja) — bugs menores que degradan experiencia
    4. Problema de Usabilidad (púrpura) — issues de UX/UI

  Los incidentes dentro de cada columna están ordenados por priority_order
  (menor número = mayor prioridad, aparece arriba). El usuario puede
  arrastrar las tarjetas para reordenar prioridades dentro de una columna.

  Props:
    - incidents: Incident[] — todos los incidentes a mostrar
  Emits:
    - selectIncident(incident) — al hacer clic en una tarjeta
    - reorder(category, orderedIds) — al soltar una tarjeta (nuevo orden)
  ============================================================================
-->
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 h-full">
    <!--
      Iteramos sobre las 4 categorías definidas en COLUMNS.
      Cada columna es un contenedor vertical con su propio scroll.
    -->
    <div
      v-for="column in columns"
      :key="column.category"
      class="flex flex-col bg-gray-50 dark:bg-gray-800/50 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700"
    >
      <!-- ===== ENCABEZADO DE COLUMNA ===== -->
      <div
        :class="[
          'flex items-center justify-between px-4 py-3 border-b-2',
          column.borderClass,
        ]"
      >
        <div class="flex items-center gap-2">
          <!-- Icono de la categoría -->
          <span class="text-lg">{{ column.icon }}</span>

          <!-- Nombre de la categoría -->
          <h3 class="font-semibold text-sm text-gray-800 dark:text-gray-200">
            {{ column.label }}
          </h3>
        </div>

        <!-- Badge con conteo de incidentes en esta categoría -->
        <span
          :class="[
            'inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold',
            column.badgeBg,
            column.badgeText,
          ]"
        >
          {{ getColumnIncidents(column.category).length }}
        </span>
      </div>

      <!-- ===== ÁREA DE TARJETAS (scrollable) ===== -->
      <div
        :class="[
          'flex-1 overflow-y-auto p-3 space-y-2 min-h-[200px] transition-colors duration-200',
          dragOverColumn === column.category ? 'bg-blue-50/50 dark:bg-blue-900/10' : '',
        ]"
        @dragover.prevent="onDragOver($event, column.category)"
        @dragleave="onDragLeave"
        @drop="onDrop($event, column.category)"
      >
        <!--
          Tarjetas de incidentes ordenadas por priority_order.
          Cada tarjeta es draggable para reordenamiento.
        -->
        <IncidentCard
          v-for="incident in getColumnIncidents(column.category)"
          :key="incident.id"
          :incident="incident"
          @select="$emit('selectIncident', $event)"
          @drag-start="onCardDragStart(incident)"
          @drag-end="onCardDragEnd"
        />

        <!-- Estado vacío de la columna -->
        <div
          v-if="getColumnIncidents(column.category).length === 0"
          class="flex flex-col items-center justify-center py-8 text-gray-400 dark:text-gray-500"
        >
          <!-- Icono vacío -->
          <svg class="w-10 h-10 mb-2 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="text-xs text-center">
            {{ $t?.('incidents.noIncidentsInCategory') || 'No hay incidentes en esta categoría' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Script del tablero Kanban de incidentes.
 *
 * Agrupa los incidentes recibidos por categoría y los ordena por
 * priority_order dentro de cada columna. Gestiona el drag & drop
 * para reordenar las prioridades de los incidentes.
 */
import { ref, computed } from 'vue'
import type { Incident } from '@/types/incidents'
import { IncidentCategory } from '@/types/incidents'
import IncidentCard from './IncidentCard.vue'

// === Props y Emits ===

const props = defineProps<{
  /** Lista completa de incidentes a distribuir en las columnas */
  incidents: Incident[]
}>()

const emit = defineEmits<{
  /** Emitido al hacer clic en una tarjeta de incidente */
  (e: 'selectIncident', incident: Incident): void
  /**
   * Emitido al soltar una tarjeta tras reordenar.
   * @param category — categoría de la columna donde se soltó
   * @param orderedIds — nueva lista ordenada de IDs en esa columna
   */
  (e: 'reorder', category: IncidentCategory, orderedIds: string[]): void
}>()

// === Configuración de columnas ===

/**
 * Definición de las 4 columnas del Kanban.
 * Cada columna corresponde a una categoría de incidente
 * con su configuración visual propia.
 */
const columns = [
  {
    category: IncidentCategory.NEW_FEATURE,
    label: 'Nueva Funcionalidad',
    icon: '★',
    borderClass: 'border-blue-400',
    badgeBg: 'bg-blue-100 dark:bg-blue-800',
    badgeText: 'text-blue-700 dark:text-blue-200',
  },
  {
    category: IncidentCategory.CRITICAL_ERROR,
    label: 'Error Crítico',
    icon: '🐛',
    borderClass: 'border-red-500',
    badgeBg: 'bg-red-100 dark:bg-red-800',
    badgeText: 'text-red-700 dark:text-red-200',
  },
  {
    category: IncidentCategory.NON_CRITICAL_ERROR,
    label: 'Error No Crítico',
    icon: '⚠',
    borderClass: 'border-orange-400',
    badgeBg: 'bg-orange-100 dark:bg-orange-800',
    badgeText: 'text-orange-700 dark:text-orange-200',
  },
  {
    category: IncidentCategory.USABILITY_ISSUE,
    label: 'Problema de Usabilidad',
    icon: '👁',
    borderClass: 'border-purple-400',
    badgeBg: 'bg-purple-100 dark:bg-purple-800',
    badgeText: 'text-purple-700 dark:text-purple-200',
  },
]

// === Estado de Drag & Drop ===

/** Categoría de la columna sobre la que se está arrastrando */
const dragOverColumn = ref<IncidentCategory | null>(null)

/** Incidente que se está arrastrando actualmente */
const draggingIncident = ref<Incident | null>(null)

// === Computados ===

/**
 * Obtiene los incidentes de una categoría específica,
 * ordenados por priority_order (menor = más prioritario).
 */
function getColumnIncidents(category: IncidentCategory): Incident[] {
  return props.incidents
    .filter((inc) => inc.category === category)
    .sort((a, b) => (a.priorityOrder ?? 999) - (b.priorityOrder ?? 999))
}

// === Handlers de Drag & Drop ===

/**
 * Cuando una tarjeta inicia el arrastre, guardamos referencia.
 */
function onCardDragStart(incident: Incident) {
  draggingIncident.value = incident
}

/**
 * Cuando el arrastre termina (sea con drop o cancelación).
 */
function onCardDragEnd() {
  draggingIncident.value = null
  dragOverColumn.value = null
}

/**
 * Cuando un elemento se arrastra sobre una columna,
 * marcamos esa columna para feedback visual.
 */
function onDragOver(event: DragEvent, category: IncidentCategory) {
  event.preventDefault()
  dragOverColumn.value = category
}

/**
 * Cuando el cursor sale de la columna, quitamos el highlight.
 */
function onDragLeave() {
  dragOverColumn.value = null
}

/**
 * Cuando se suelta una tarjeta en una columna:
 * 1. Extraemos el ID del incidente arrastrado
 * 2. Lo insertamos al final de la columna destino
 * 3. Emitimos el nuevo orden para persistir en el backend
 */
function onDrop(event: DragEvent, targetCategory: IncidentCategory) {
  event.preventDefault()
  dragOverColumn.value = null

  const incidentId = event.dataTransfer?.getData('text/plain')
  if (!incidentId) return

  // Obtenemos los IDs actuales de la columna destino
  const currentIds = getColumnIncidents(targetCategory).map((inc) => inc.id)

  // Si el incidente ya estaba en esta columna, lo removemos para reinsertarlo
  const filteredIds = currentIds.filter((id) => id !== incidentId)

  // Lo agregamos al final (prioridad más baja dentro de esta categoría)
  filteredIds.push(incidentId)

  // Emitimos el nuevo orden para que el store/API lo persista
  emit('reorder', targetCategory, filteredIds)
}
</script>
