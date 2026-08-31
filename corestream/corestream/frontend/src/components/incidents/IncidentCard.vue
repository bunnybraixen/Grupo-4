<!--
  ============================================================================
  IncidentCard.vue — Tarjeta de Incidente para el Tablero Kanban
  ============================================================================

  Componente que renderiza una tarjeta compacta de incidente dentro de las
  columnas del tablero Kanban. Cada tarjeta muestra información resumida:
  severidad (borde lateral coloreado), título, estado, asignado y fecha.

  Características visuales:
  - Borde izquierdo coloreado según severidad (rojo=CRITICAL, naranja=HIGH, etc.)
  - Efecto pulse en el borde si la severidad es CRITICAL
  - Fondo rojizo sutil si el incidente está vencido (isOverdue)
  - Sombra al hacer hover para indicar interactividad
  - Draggable para reordenar dentro de su columna por prioridad

  Props:
    - incident: Incident — datos completos del incidente
  Emits:
    - select(incident) — al hacer clic en la tarjeta
    - dragStart(incident) — al iniciar arrastre
    - dragEnd — al terminar arrastre
  ============================================================================
-->
<template>
  <div
    :class="[
      'relative rounded-lg border bg-white dark:bg-gray-800 p-3 cursor-pointer',
      'transition-all duration-200 hover:shadow-md hover:-translate-y-0.5',
      'border-l-4',
      severityBorderClass,
      incident.isOverdue ? 'bg-red-50/50 dark:bg-red-900/10' : '',
    ]"
    draggable="true"
    @click="$emit('select', incident)"
    @dragstart="onDragStart"
    @dragend="$emit('dragEnd')"
  >
    <!-- Fila superior: Severidad dot + Título -->
    <div class="flex items-start gap-2 mb-2">
      <!-- Indicador de severidad (punto coloreado) -->
      <span
        :class="['mt-1 w-2.5 h-2.5 rounded-full flex-shrink-0', severityDotClass]"
        :title="severityLabel"
      />

      <!-- Título del incidente (truncado si es largo) -->
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2 leading-tight flex-1">
        {{ incident.title }}
      </h4>
    </div>

    <!-- Fila de badges: categoría + estado -->
    <div class="flex items-center gap-1.5 mb-2 flex-wrap">
      <!-- Badge de categoría (mini, coloreado) -->
      <span
        :class="[
          'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium',
          categoryConfig.bgColor,
          categoryConfig.textColor,
        ]"
      >
        <span class="mr-0.5">{{ categoryConfig.icon }}</span>
        {{ categoryShortLabel }}
      </span>

      <!-- Badge de estado -->
      <span
        :class="[
          'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium',
          statusConfig.bgClass,
          statusConfig.textClass,
        ]"
      >
        {{ statusConfig.label }}
      </span>
    </div>

    <!-- Fila inferior: Asignado + Fecha + Días abierto -->
    <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
      <!-- Avatar del asignado -->
      <div class="flex items-center gap-1.5">
        <template v-if="incident.assignee">
          <!-- Avatar circular con iniciales -->
          <div
            class="w-5 h-5 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center text-[9px] font-bold text-blue-700 dark:text-blue-200"
          >
            {{ getInitials(incident.assignee.fullName || '') }}
          </div>
          <span class="truncate max-w-[80px]">
            {{ incident.assignee.fullName?.split(' ')[0] || 'Asignado' }}
          </span>
        </template>
        <template v-else>
          <!-- Indicador de sin asignar -->
          <div class="w-5 h-5 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center">
            <span class="text-[9px] text-gray-400">?</span>
          </div>
          <span class="text-gray-400 italic">{{ $t?.('incidents.unassigned') || 'Sin asignar' }}</span>
        </template>
      </div>

      <!-- Fecha límite y días abierto -->
      <div class="flex items-center gap-2">
        <!-- Días abierto -->
        <span
          v-if="incident.daysOpen !== undefined && incident.daysOpen > 0"
          class="text-gray-400"
        >
          {{ incident.daysOpen }}d
        </span>

        <!-- Fecha límite -->
        <span
          v-if="incident.dueDate"
          :class="[
            'flex items-center gap-0.5',
            incident.isOverdue ? 'text-red-500 font-medium' : 'text-gray-400',
          ]"
        >
          <!-- Icono calendario -->
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(incident.dueDate) }}
        </span>
      </div>
    </div>

    <!-- Indicador visual de vencido (banner sutil) -->
    <div
      v-if="incident.isOverdue"
      class="absolute top-0 right-0 px-1.5 py-0.5 bg-red-500 text-white text-[9px] font-bold rounded-bl-md rounded-tr-md"
    >
      {{ $t?.('incidents.overdue') || 'Vencido' }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Script de la tarjeta de incidente.
 *
 * Importa las configuraciones visuales de categoría, severidad y estado
 * desde los tipos de incidentes para mantener consistencia visual
 * en toda la aplicación.
 */
import { computed } from 'vue'
import type { Incident } from '@/types/incidents'
import {
  IncidentCategory,
  IncidentSeverity,
  CATEGORY_CONFIG,
  SEVERITY_CONFIG,
  STATUS_CONFIG,
} from '@/types/incidents'

// === Props y Emits ===

const props = defineProps<{
  /** Datos completos del incidente a renderizar */
  incident: Incident
}>()

defineEmits<{
  /** Emitido al hacer clic en la tarjeta — abre el panel de detalle */
  (e: 'select', incident: Incident): void
  /** Emitido al iniciar drag — para reordenamiento en el kanban */
  (e: 'dragStart', incident: Incident): void
  /** Emitido al finalizar drag */
  (e: 'dragEnd'): void
}>()

// === Configuraciones visuales computadas ===

/**
 * Configuración visual de la categoría del incidente.
 * Determina color del badge, icono y etiqueta.
 */
const categoryConfig = computed(() =>
  CATEGORY_CONFIG[props.incident.category] || CATEGORY_CONFIG[IncidentCategory.NON_CRITICAL_ERROR]
)

/**
 * Etiqueta corta de la categoría (primera palabra para ahorrar espacio).
 */
const categoryShortLabel = computed(() => {
  const labels: Record<string, string> = {
    [IncidentCategory.NEW_FEATURE]: 'Feature',
    [IncidentCategory.CRITICAL_ERROR]: 'Crítico',
    [IncidentCategory.NON_CRITICAL_ERROR]: 'Error',
    [IncidentCategory.USABILITY_ISSUE]: 'UX',
  }
  return labels[props.incident.category] || 'Otro'
})

/**
 * Configuración visual del estado del incidente.
 */
const statusConfig = computed(() =>
  STATUS_CONFIG[props.incident.status] || STATUS_CONFIG.OPEN
)

/**
 * Clase CSS del punto indicador de severidad.
 * CRITICAL tiene animación pulse para llamar la atención.
 */
const severityDotClass = computed(() =>
  SEVERITY_CONFIG[props.incident.severity]?.dotClass || 'bg-yellow-500'
)

/**
 * Etiqueta de severidad para el tooltip del indicador.
 */
const severityLabel = computed(() =>
  SEVERITY_CONFIG[props.incident.severity]?.label || 'Medio'
)

/**
 * Clase CSS del borde izquierdo según severidad.
 * El borde lateral es el principal indicador visual de urgencia.
 */
const severityBorderClass = computed(() => {
  const map: Record<string, string> = {
    [IncidentSeverity.CRITICAL]: 'border-l-red-500',
    [IncidentSeverity.HIGH]: 'border-l-orange-500',
    [IncidentSeverity.MEDIUM]: 'border-l-yellow-400',
    [IncidentSeverity.LOW]: 'border-l-green-400',
  }
  return map[props.incident.severity] || 'border-l-gray-300'
})

// === Funciones auxiliares ===

/**
 * Extrae las iniciales de un nombre completo para el avatar circular.
 * Ejemplo: "Carlos Mendoza" → "CM"
 */
function getInitials(name: string): string {
  return name
    .split(' ')
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
}

/**
 * Formatea una fecha ISO a formato corto legible.
 * Ejemplo: "2026-03-15" → "15 Mar"
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
  return `${date.getDate()} ${months[date.getMonth()]}`
}

/**
 * Handler del inicio de drag — establece datos de transferencia
 * para que el tablero kanban sepa qué incidente se está moviendo.
 */
function onDragStart(event: DragEvent) {
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', props.incident.id)
  }
}
</script>
