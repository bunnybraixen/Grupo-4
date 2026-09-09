<template>
  <!-- 
    COMPONENTE: Heatmap
    DESCRIPCIÓN: Visualización en forma de matriz de calor para analizar actividad de desarrolladores:
    - Eje X: Días de la semana (Lunes a Domingo)
    - Eje Y: Nombres de desarrolladores
    - Intensidad de color: Cantidad de tickets cerrados
    - Escala de color: Blanco (menos) a Verde profundo (más)
    - Tooltips en hover mostrando cantidad exacta de tickets
    - Totales de filas y columnas
    - Análisis de patrón al pie
    
    CARACTERÍSTICAS:
    - Grid interactivo con colores dinámicos
    - Tooltips informativos al pasar el mouse
    - Detección automática de patrones (ej: "Actividad baja los viernes")
    - Totales por desarrollador y por día
    - Escala de colores suave y gradual
  -->
  <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6 mb-8">
    <!-- Encabezado del Mapa de Calor -->
    <div class="mb-6">
      <h3 class="text-xl font-bold text-[var(--text-primary)] mb-2">{{ t('analytics.heatmap') || t('analyticsView.weeklyActivity') }}</h3>
      <p class="text-sm text-[var(--text-secondary)]">{{ t('analytics.heatmapDescription') || 'Visualización de tickets completados por día de la semana.' }}</p>
    </div>

    <!-- Contenedor con Scroll -->
    <div class="overflow-x-auto mb-6">
      <table class="w-full border-collapse">
        <thead>
          <tr>
            <th class="w-40 h-10 border border-[var(--border-subtle)] bg-[var(--bg-panel)]"></th>
            <!-- Columnas de los días de la semana (Eje X) -->
            <th 
              v-for="(day, index) in daysOfWeek"
              :key="index"
              class="w-20 h-10 border border-[var(--border-subtle)] bg-[var(--bg-panel)] text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider"
            >
              {{ day }}
            </th>
            <!-- Columna para el Total por fila (Desarrollador) -->
            <th class="w-16 h-10 border border-[var(--border-subtle)] bg-[var(--teal)]/10 text-xs font-semibold text-[var(--teal)] uppercase tracking-wider">
              {{ t('analytics.total') || 'Total' }}
            </th>
          </tr>
        </thead>

        <tbody>
          <!-- Filas dinámicas de Desarrolladores (Eje Y) -->
          <tr v-for="(developer, devIndex) in heatmapDevelopers" :key="devIndex">
            <td class="px-3 py-2 border border-[var(--border-subtle)] bg-[var(--bg-panel)] font-medium text-sm text-[var(--text-primary)] whitespace-nowrap">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-[var(--teal)] flex items-center justify-center text-white text-xs font-bold">
                  {{ developer.avatarInitials }}
                </div>
                <span class="truncate" :title="developer.name">{{ developer.name }}</span>
              </div>
            </td>

            <!-- Celdas de la Matriz -->
            <td 
              v-for="dayIndex in Array.from({ length: 7 }, (_, i) => i)"
              :key="dayIndex"
              class="w-20 h-16 border border-[var(--border-subtle)] p-2 relative group cursor-pointer transition-all duration-200"
              :style="{ backgroundColor: getHeatmapColor(heatmapMatrix[devIndex]?.[dayIndex] || 0) }"
            >
              <div class="text-center h-full flex items-center justify-center">
                <span class="text-sm font-semibold" :class="getTextColorClass(heatmapMatrix[devIndex]?.[dayIndex] || 0)">
                  {{ heatmapMatrix[devIndex]?.[dayIndex] || 0 }}
                </span>
              </div>

              <!-- Tooltip flotante nativo en Hover -->
              <div class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap z-10 pointer-events-none">
                {{ heatmapMatrix[devIndex]?.[dayIndex] || 0 }} {{ t('analytics.ticketsClosedShort') || 'tickets' }}
                <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900"></div>
              </div>
            </td>

            <!-- Total Acumulado Horizontal por Desarrollador -->
            <td class="px-3 py-2 border border-[var(--border-subtle)] bg-[var(--teal)]/10 font-bold text-sm text-[var(--teal)] text-center">
              {{ getRowTotal(devIndex) }}
            </td>
          </tr>

          <!-- Fila final de Totales Diarios Verticales (Eje X global) -->
          <tr>
            <td class="px-3 py-2 border border-[var(--border-subtle)] bg-blue-500/10 font-semibold text-sm text-blue-600 dark:text-blue-400">
              {{ t('analytics.daily') || 'Diario' }}
                </td>
            <td 
              v-for="dayIndex in Array.from({ length: 7 }, (_, i) => i)"
              :key="'total-' + dayIndex"
              class="px-3 py-2 border border-[var(--border-subtle)] bg-blue-500/10 font-bold text-sm text-blue-600 dark:text-blue-400 text-center"
            >
              {{ getColumnTotal(dayIndex) }}
            </td>
            <!-- Gran Total Absoluto del proyecto seleccionado -->
            <td class="px-3 py-2 border border-[var(--border-subtle)] bg-[var(--teal)]/20 font-bold text-sm text-[var(--teal)] text-center">
              {{ getTotalAll() }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paneles Inferiores -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="p-4 bg-[var(--bg-panel)] rounded-lg border border-[var(--border-subtle)]">
        <p class="text-xs font-semibold text-[var(--text-secondary)] mb-3">{{ t('analytics.colorScale') || 'Escala de Actividad' }}:</p>
        <div class="flex items-center gap-4 flex-wrap">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded border border-[var(--border-subtle)] bg-transparent"></div>
            <span class="text-xs text-[var(--text-secondary)]">{{ t('analytics.low') || 'Nula/Baja' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded border border-gray-300" style="background-color: #c8e6c9"></div>
            <span class="text-xs text-[var(--text-secondary)]">{{ t('analytics.medium') || 'Media' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded border border-gray-300" style="background-color: #4caf50"></div>
            <span class="text-xs text-[var(--text-secondary)]">{{ t('analytics.high') || 'Alta' }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded border border-gray-300" style="background-color: #1b5e20"></div>
            <span class="text-xs text-[var(--text-secondary)]">{{ t('analytics.veryHigh') || 'Muy Alta' }}</span>
          </div>
        </div>
      </div>

      <div class="p-4 bg-blue-500/10 rounded-lg border-l-4 border-blue-500">
        <div class="flex gap-3">
          <span class="text-xl mt-0.5">💡</span>
          <div>
            <p class="text-sm font-bold text-blue-700 dark:text-blue-400 mb-1">{{ t('analytics.insight') || 'Análisis de Patrón' }}</p>
            <p class="text-sm text-blue-600 dark:text-blue-300">{{ patternInsight }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ESTRUCTURA DEL SCRIPT PARA COMPONENTE HEATMAP:
 * 1. Imports necesarios
 * 2. Tipos e interfaces
 * 3. Inicialización de composables y stores
 * 4. Datos reactivos
 * 5. Propiedades computadas
 * 6. Funciones auxiliares de cálculo
 * 7. Funciones de colorización
 * 8. Ciclo de vida
 */

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAnalyticsStore } from '@/stores/analytics'

const { t } = useI18n()
const analyticsStore = useAnalyticsStore()

// Días de la semana dinámicos según el idioma activo
const daysOfWeek = computed(() => [
  t('analyticsView.dayMon') || 'Lun', t('analyticsView.dayTue') || 'Mar', t('analyticsView.dayWed') || 'Mié',
  t('analyticsView.dayThu') || 'Jue', t('analyticsView.dayFri') || 'Vie', t('analyticsView.daySat') || 'Sáb',
  t('analyticsView.daySun') || 'Dom',
])

// Lista de desarrolladores formateada con nombres e iniciales para los avatares
const heatmapDevelopers = computed<{name: string, avatarInitials: string}[]>(() => {
  const raw = (analyticsStore.heatmapData || []) as any
  const devArray = Array.isArray(raw) ? raw : (raw.developers || raw.heatmap?.developers || [])
  
  return devArray.map((dev: any) => ({
    name: dev.name || t('analyticsView.unknownDev') || 'Desconocido',
    avatarInitials: getInitials(dev.name || 'Usuario')
  }))
})

// Matriz bidimensional reactiva protegida contra arreglos vacíos o nulos
const heatmapMatrix = computed<number[][]>(() => {
  const raw = (analyticsStore.heatmapData || []) as any
  const devArray = Array.isArray(raw) ? raw : (raw.developers || raw.heatmap?.developers || [])
  
  return devArray.map((dev: any) => {
    const rawValues = dev.data || dev.values || [0, 0, 0, 0, 0, 0, 0]
    return rawValues.map(Number)
  })
})

/**
 * Determina el color cromático de la celda según los tickets cerrados.
 * Retorna transparente si no hay actividad, o tonos verdes según la densidad.
 */
function getHeatmapColor(value: number): string {
  if (value === 0) return 'transparent'
  if (value < 5) return '#c8e6c9'
  if (value < 15) return '#4caf50'
  return '#1b5e20'
}

/**
 * Controla el contraste del texto para asegurar accesibilidad.
 * Texto claro para fondos oscuros y viceversa.
 */
function getTextColorClass(value: number): string {
  if (value === 0 || value < 5) return 'text-[var(--text-primary)]'
  return 'text-white'
}

/**
 * Suma los tickets de una fila completa para obtener el total semanal de un desarrollador.
 */
function getRowTotal(rowIndex: number): number {
  if (!heatmapMatrix.value[rowIndex]) return 0
  return heatmapMatrix.value[rowIndex].reduce((sum, val) => sum + val, 0)
}

/**
 * Suma las celdas verticalmente para saber el rendimiento global del equipo en un día.
 */
function getColumnTotal(colIndex: number): number {
  if (heatmapMatrix.value.length === 0) return 0
  return heatmapMatrix.value.reduce((sum, row) => sum + (row[colIndex] || 0), 0)
}

/**
 * Suma absolutamente todas las celdas de la matriz para calcular el total general de la aplicación.
 */
function getTotalAll(): number {
  return heatmapMatrix.value.reduce((total, row) => total + row.reduce((sum, val) => sum + val, 0), 0)
}

/**
 * Evalúa matemáticamente el día con menor rendimiento del equipo e inyecta la métrica en el insight.
 */
const patternInsight = computed<string>(() => {
  if (heatmapMatrix.value.length === 0) {
    return t('analytics.noDataPattern') || 'Sin datos suficientes para detectar patrones.'
  }

  const dailyTotals = Array.from({ length: 7 }, (_, i) => getColumnTotal(i))
  const minDayIndex = dailyTotals.indexOf(Math.min(...dailyTotals))
  const dayName = daysOfWeek.value[minDayIndex]
  
  return (t('analytics.lowActivityPattern') || 'El día con menor actividad históricamente es el ') + dayName + '.'
})

/**
 * Divide cadenas de texto y extrae las dos primeras letras iniciales del desarrollador.
 */
const getInitials = (name: string): string => {
  return name.split(' ').filter(p => p.length > 0).map(p => p).join('').toUpperCase().slice(0, 2) || 'U'
}
</script>

<style scoped>
:deep(table td) { transition: background-color 0.3s ease; }
:deep(table td.group:hover) {
  transform: scale(1.05);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 10;
}
</style>