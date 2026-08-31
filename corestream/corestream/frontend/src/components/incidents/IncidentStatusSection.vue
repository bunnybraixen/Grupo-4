<!--
  ============================================================================
  IncidentStatusSection.vue — Sección Colapsable de Incidentes por Estado
  ============================================================================

  Componente reutilizable que muestra una sección colapsable con una lista
  de incidentes agrupados por estado. Utilizado en MyIncidentsView para
  mostrar incidentes en secciones como "Abiertos", "En Progreso", etc.

  Características:
    - Encabezado con punto de color, título, conteo y botón colapsar
    - Lista de tarjetas de incidente con información resumida
    - Botones de acción rápida contextuales según el estado
    - Indicador de vencido en incidentes con fecha límite pasada
    - Animación suave al expandir/colapsar

  Props:
    - title: string — nombre de la sección
    - count: number — cantidad de incidentes
    - incidents: Incident[] — lista de incidentes a mostrar
    - dotClass: string — clase CSS para el punto de color
    - headerClass: string — clase CSS para el borde del encabezado
    - defaultOpen: boolean — si la sección inicia expandida
  Emits:
    - select(incident) — al hacer clic en una tarjeta
    - action(incidentId, actionName) — al ejecutar una acción rápida
  ============================================================================
-->
<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
    <!-- ===== ENCABEZADO DE SECCIÓN ===== -->
    <button
      @click="isOpen = !isOpen"
      :class="[
        'w-full flex items-center justify-between px-4 py-3 border-l-4 transition-colors',
        'hover:bg-gray-50 dark:hover:bg-gray-700/50',
        headerClass,
      ]"
    >
      <div class="flex items-center gap-2.5">
        <!-- Punto de color indicador del estado -->
        <span :class="['w-2.5 h-2.5 rounded-full', dotClass]"></span>

        <!-- Título de la sección -->
        <h3 class="text-sm font-semibold text-gray-800 dark:text-gray-200">
          {{ title }}
        </h3>

        <!-- Badge de conteo -->
        <span class="inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-bold bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
          {{ count }}
        </span>
      </div>

      <!-- Icono chevron (rota al expandir) -->
      <svg
        :class="[
          'w-4 h-4 text-gray-400 transition-transform duration-200',
          isOpen ? 'rotate-180' : '',
        ]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- ===== LISTA DE INCIDENTES (colapsable) ===== -->
    <div
      v-show="isOpen"
      class="divide-y divide-gray-100 dark:divide-gray-700"
    >
      <div
        v-for="incident in incidents"
        :key="incident.id"
        class="flex items-center gap-4 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/30 cursor-pointer transition-colors"
        @click="$emit('select', incident)"
      >
        <!-- Indicador de severidad (borde izquierdo coloreado) -->
        <div
          :class="[
            'w-1 h-12 rounded-full flex-shrink-0',
            severityColorClass(incident.severity),
          ]"
        ></div>

        <!-- Información del incidente -->
        <div class="flex-1 min-w-0">
          <!-- Título -->
          <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
            {{ incident.title }}
          </h4>

          <!-- Metadatos: categoría + aplicación + fecha -->
          <div class="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
            <!-- Badge de categoría -->
            <span :class="['px-1.5 py-0.5 rounded text-[10px] font-medium', categoryBadgeClass(incident.category)]">
              {{ categoryLabel(incident.category) }}
            </span>

            <!-- Nombre de aplicación -->
            <span v-if="incident.applicationName" class="truncate max-w-[120px]">
              {{ incident.applicationName }}
            </span>

            <!-- Separador -->
            <span v-if="incident.dueDate">·</span>

            <!-- Fecha límite -->
            <span
              v-if="incident.dueDate"
              :class="[incident.isOverdue ? 'text-red-500 font-medium' : '']"
            >
              {{ formatDate(incident.dueDate) }}
            </span>

            <!-- Indicador vencido -->
            <span
              v-if="incident.isOverdue"
              class="px-1.5 py-0.5 bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400 rounded text-[10px] font-bold"
            >
              {{ $t?.('incidents.overdue') || 'Vencido' }}
            </span>
          </div>
        </div>

        <!-- Días abierto -->
        <div
          v-if="incident.daysOpen && incident.daysOpen > 0"
          class="flex-shrink-0 text-xs text-gray-400 dark:text-gray-500"
        >
          {{ incident.daysOpen }}d
        </div>

        <!-- Botones de acción rápida (dependen del estado) -->
        <div class="flex-shrink-0 flex items-center gap-1.5" @click.stop>
          <!-- Acción: Iniciar (para OPEN/REOPENED) -->
          <button
            v-if="incident.status === 'OPEN' || incident.status === 'REOPENED'"
            @click="$emit('action', incident.id, 'start')"
            class="px-2.5 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-md transition-colors"
            :title="$t?.('incidents.actions.start') || 'Iniciar'"
          >
            {{ $t?.('incidents.actions.start') || 'Iniciar' }}
          </button>

          <!-- Acción: Enviar a Revisión (para IN_PROGRESS) -->
          <button
            v-if="incident.status === 'IN_PROGRESS'"
            @click="$emit('action', incident.id, 'review')"
            class="px-2.5 py-1 text-xs font-medium text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30 hover:bg-purple-100 dark:hover:bg-purple-900/50 rounded-md transition-colors"
            :title="$t?.('incidents.actions.sendToReview') || 'Enviar a Revisión'"
          >
            {{ $t?.('incidents.actions.sendToReview') || 'A Revisión' }}
          </button>

          <!-- Acción: Reabrir (para RESOLVED) -->
          <button
            v-if="incident.status === 'RESOLVED'"
            @click="$emit('action', incident.id, 'reopen')"
            class="px-2.5 py-1 text-xs font-medium text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/30 hover:bg-orange-100 dark:hover:bg-orange-900/50 rounded-md transition-colors"
            :title="$t?.('incidents.actions.reopen') || 'Reabrir'"
          >
            {{ $t?.('incidents.actions.reopen') || 'Reabrir' }}
          </button>

          <!-- Estado: En Revisión (badge informativo) -->
          <span
            v-if="incident.status === 'UNDER_REVIEW'"
            class="px-2.5 py-1 text-xs font-medium text-purple-500 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-md"
          >
            {{ $t?.('incidents.status.underReview') || 'En Revisión' }}
          </span>
        </div>
      </div>

      <!-- Estado vacío dentro de la sección -->
      <div
        v-if="incidents.length === 0"
        class="px-4 py-6 text-center text-sm text-gray-400 dark:text-gray-500"
      >
        {{ $t?.('incidents.noIncidentsInSection') || 'No hay incidentes en esta sección' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Script de la sección colapsable de incidentes.
 *
 * Componente presentacional que recibe una lista de incidentes
 * y los muestra con formato consistente. Emite eventos hacia
 * el padre para manejar selección y acciones.
 */
import { ref } from 'vue'
import type { Incident, IncidentCategory, IncidentSeverity } from '@/types/incidents'

// === Props y Emits ===

const props = defineProps<{
  /** Título de la sección (ej: "Abiertos") */
  title: string
  /** Conteo de incidentes en la sección */
  count: number
  /** Lista de incidentes a mostrar */
  incidents: Incident[]
  /** Clase CSS del punto indicador de color */
  dotClass: string
  /** Clase CSS del borde izquierdo del encabezado */
  headerClass: string
  /** Si la sección empieza expandida */
  defaultOpen: boolean
}>()

defineEmits<{
  /** Emitido al hacer clic en un incidente — abre panel de detalle */
  (e: 'select', incident: Incident): void
  /** Emitido al ejecutar una acción rápida en un incidente */
  (e: 'action', incidentId: string, actionName: string): void
}>()

// === Estado local ===

/** Controla si la sección está expandida o colapsada */
const isOpen = ref(props.defaultOpen)

// === Funciones auxiliares ===

/**
 * Retorna la clase CSS del color de severidad para el borde lateral.
 */
function severityColorClass(severity: IncidentSeverity): string {
  const map: Record<string, string> = {
    CRITICAL: 'bg-red-500',
    HIGH: 'bg-orange-500',
    MEDIUM: 'bg-yellow-400',
    LOW: 'bg-green-400',
  }
  return map[severity] || 'bg-gray-300'
}

/**
 * Retorna las clases CSS para el badge de categoría.
 */
function categoryBadgeClass(category: IncidentCategory): string {
  const map: Record<string, string> = {
    NEW_FEATURE: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    CRITICAL_ERROR: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
    NON_CRITICAL_ERROR: 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300',
    USABILITY_ISSUE: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  }
  return map[category] || 'bg-gray-100 text-gray-700'
}

/**
 * Retorna la etiqueta corta de una categoría.
 */
function categoryLabel(category: IncidentCategory): string {
  const map: Record<string, string> = {
    NEW_FEATURE: 'Feature',
    CRITICAL_ERROR: 'Crítico',
    NON_CRITICAL_ERROR: 'Error',
    USABILITY_ISSUE: 'UX',
  }
  return map[category] || 'Otro'
}

/**
 * Formatea una fecha ISO a formato corto.
 * Ejemplo: "2026-03-15" → "15 Mar"
 */
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
  return `${date.getDate()} ${months[date.getMonth()]}`
}
</script>
