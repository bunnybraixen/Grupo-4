<!--
  IncidentKanbanBoard.vue
  ============================================================================
  Tablero Kanban de incidentes agrupados por categoría.

  IncidentsView.vue importaba este componente pero nunca se agregó al
  repositorio, así que la ruta /admin/incidents no podía cargarse y el build
  de producción fallaba.

  - Una columna por categoría (más "Sin categoría" si hace falta).
  - Dentro de cada columna los incidentes se ordenan por `priorityOrder`.
  - Arrastrar y soltar una tarjeta dentro de su columna emite `reorder`
    con la categoría y la lista de IDs en el nuevo orden.
  - Hacer clic en una tarjeta emite `select-incident`.
  ============================================================================
-->
<template>
  <div class="flex gap-4 h-full overflow-x-auto pb-2">
    <section
      v-for="column in columns"
      :key="column.key"
      class="flex flex-col w-72 flex-shrink-0 rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900"
    >
      <header class="flex items-center justify-between px-3 py-2 border-b border-slate-200 dark:border-slate-700">
        <h3 class="text-sm font-semibold text-slate-800 dark:text-white">{{ column.label }}</h3>
        <span class="rounded-full bg-slate-200 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
          {{ column.incidents.length }}
        </span>
      </header>

      <div class="flex-1 overflow-y-auto p-2 space-y-2">
        <p v-if="column.incidents.length === 0" class="py-6 text-center text-xs text-slate-400">
          Sin incidentes
        </p>

        <article
          v-for="incident in column.incidents"
          :key="incident.id"
          :draggable="column.category !== null"
          :class="[
            'cursor-pointer rounded-lg border bg-white p-3 shadow-sm transition hover:border-blue-300 dark:bg-slate-800',
            dragOverId === incident.id ? 'border-blue-500' : 'border-slate-200 dark:border-slate-700',
          ]"
          @click="emit('select-incident', incident)"
          @dragstart="onDragStart(column.key, incident.id)"
          @dragover.prevent="onDragOver(column.key, incident.id)"
          @dragleave="dragOverId = null"
          @drop.prevent="onDrop(column, incident.id)"
          @dragend="resetDrag"
        >
          <div class="flex items-start justify-between gap-2">
            <p class="text-sm font-medium text-slate-800 dark:text-white">{{ incident.title }}</p>
            <span :class="['rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase', severityClass(incident.severity)]">
              {{ incident.severity }}
            </span>
          </div>
          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ incident.status }}</p>
          <p v-if="incident.assignee?.fullName" class="mt-1 text-xs text-slate-500 dark:text-slate-400">
            👤 {{ incident.assignee.fullName }}
          </p>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Incident, IncidentCategory, IncidentSeverity } from '@/types/incidents'

const props = defineProps<{
  incidents: Incident[]
}>()

const emit = defineEmits<{
  'select-incident': [incident: Incident]
  reorder: [category: IncidentCategory, orderedIds: string[]]
}>()

interface KanbanColumn {
  key: string
  label: string
  /** null = columna "Sin categoría" (no se puede reordenar) */
  category: IncidentCategory | null
  incidents: Incident[]
}

/** Categorías en el orden en que se muestran las columnas */
const CATEGORY_LABELS: Record<IncidentCategory, string> = {
  BUG: 'Bug',
  PERFORMANCE: 'Rendimiento',
  SECURITY: 'Seguridad',
  INFRASTRUCTURE: 'Infraestructura',
  UX: 'UX',
  DATA: 'Datos',
}

const UNCATEGORIZED_KEY = 'NONE'

const byPriority = (a: Incident, b: Incident) => (a.priorityOrder ?? 0) - (b.priorityOrder ?? 0)

const columns = computed<KanbanColumn[]>(() => {
  const categories = Object.keys(CATEGORY_LABELS) as IncidentCategory[]
  const result: KanbanColumn[] = categories.map((category) => ({
    key: category,
    label: CATEGORY_LABELS[category],
    category,
    incidents: props.incidents.filter((i) => i.category === category).sort(byPriority),
  }))

  const uncategorized = props.incidents.filter((i) => !i.category).sort(byPriority)
  if (uncategorized.length > 0) {
    result.push({ key: UNCATEGORIZED_KEY, label: 'Sin categoría', category: null, incidents: uncategorized })
  }
  return result
})

const severityClass = (severity: IncidentSeverity): string => ({
  CRITICAL: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  HIGH: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
  MEDIUM: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  LOW: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300',
}[severity])

// ── Drag & drop (solo dentro de la misma columna) ──────────────────
const dragColumnKey = ref<string | null>(null)
const draggedId = ref<string | null>(null)
const dragOverId = ref<string | null>(null)

function onDragStart(columnKey: string, incidentId: string) {
  dragColumnKey.value = columnKey
  draggedId.value = incidentId
}

function onDragOver(columnKey: string, incidentId: string) {
  if (columnKey === dragColumnKey.value && incidentId !== draggedId.value) {
    dragOverId.value = incidentId
  }
}

function onDrop(column: KanbanColumn, targetId: string) {
  const sourceId = draggedId.value
  if (column.category && column.key === dragColumnKey.value && sourceId && sourceId !== targetId) {
    const ids = column.incidents.map((i) => i.id)
    const from = ids.indexOf(sourceId)
    const to = ids.indexOf(targetId)
    if (from !== -1 && to !== -1) {
      ids.splice(from, 1)
      ids.splice(to, 0, sourceId)
      emit('reorder', column.category, ids)
    }
  }
  resetDrag()
}

function resetDrag() {
  dragColumnKey.value = null
  draggedId.value = null
  dragOverId.value = null
}
</script>
