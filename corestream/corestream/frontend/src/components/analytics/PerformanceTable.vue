<template>
  <!-- 
    COMPONENTE: PerformanceTable
    DESCRIPCIÓN: Tabla de desempeño de desarrolladores con múltiples métricas:
    - Avatar y nombre del desarrollador (clickeable para drill-down)
    - Tickets procesados (barra verde)
    - Preguntas formuladas (color ámbar)
    - Redirecciones realizadas (color azul)
    - Tiempo promedio de resolución
    - Puntuación de eficiencia (con código de colores)
    - Índice de bloqueo y churn con indicadores de semáforo
    
    CARACTERÍSTICAS:
    - Columnas ordenables (click en encabezado)
    - Filas con hover para mejorar legibilidad
    - Drill-down: click en nombre abre detalle del desarrollador
    - Códigos de color: >=5 verde, >=3 amarillo, >=1.5 naranja, <1.5 rojo
    - Indicadores de semáforo para índices críticos
    - Barras de progreso con animación
  -->
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
    <!-- ENCABEZADO CON CONTROLES -->
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ $t('analytics.performanceTable') }}</h3>
        <div class="flex items-center gap-2">
          <!-- Selector de período (acceso rápido) -->
          <select v-model="selectedPeriod" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value="week">{{ $t('period.thisWeek') }}</option>
            <option value="month">{{ $t('period.thisMonth') }}</option>
            <option value="quarter">{{ $t('period.thisQuarter') }}</option>
            <option value="custom">{{ $t('period.custom') }}</option>
          </select>
          <!-- Rango de fechas personalizado -->
          <input
            v-model="dateFrom"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            @change="onDateChange"
          />
          <span class="text-gray-400 text-sm">—</span>
          <input
            v-model="dateTo"
            type="date"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            @change="onDateChange"
          />
        </div>
      </div>
    </div>

    <!-- TABLA DE DESEMPEÑO -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
          <tr>
            <!-- Encabezado: Desarrollador (no sorteable) -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('userName')">
              <div class="flex items-center gap-2">
                {{ $t('table.developer') }}
                <svg v-if="sortBy === 'userName'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Tickets Procesados (sorteable) -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('tickets_processed')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.ticketsProcessed') }}
                <svg v-if="sortBy === 'tickets_processed'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Preguntas -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('questions_raised')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.questions') }}
                <svg v-if="sortBy === 'questions_raised'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Redirecciones -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('redirections')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.redirects') }}
                <svg v-if="sortBy === 'redirections'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Tiempo Promedio -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('averageHoursPerTicket')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.avgTime') }}
                <svg v-if="sortBy === 'averageHoursPerTicket'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Eficiencia -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('efficiency')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.efficiency') }}
                <svg v-if="sortBy === 'efficiency'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Índice de Bloqueo -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
              {{ $t('analytics.blockingIndex') }}
            </th>

            <!-- Encabezado: Índice Churn -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">
              {{ $t('analytics.churnIndex') }}
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <!-- EMPTY STATE -->
          <tr v-if="sortedPerformance.length === 0">
            <td colspan="8" class="px-6 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
              No hay actividad registrada para esta aplicación en el período seleccionado.
            </td>
          </tr>
          <!-- FILA DE DATOS POR DESARROLLADOR -->
          <tr
            v-for="developer in sortedPerformance"
            :key="developer.userId"
            class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="selectDeveloper(developer)"
          >
            <!-- COLUMNA: Desarrollador (Iniciales + Nombre) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white text-sm font-bold border-2 border-gray-200 dark:border-gray-600">
                  {{ developer.userName.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ developer.userName }}</p>
                </div>
              </div>
            </td>

            <!-- COLUMNA: Tickets Procesados (Barra Verde) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <div class="flex-1">
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div
                      class="bg-green-500 h-2 rounded-full transition-all duration-300"
                      :style="{ width: ((developer.tickets_processed ?? 0) / 50) * 100 + '%' }"
                    ></div>
                  </div>
                </div>
                <span class="text-sm font-semibold text-gray-900 dark:text-white min-w-fit">{{ developer.tickets_processed ?? 0 }}</span>
              </div>
            </td>

            <!-- COLUMNA: Preguntas (Color Ámbar) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
                {{ developer.questions_raised ?? 0 }}
              </span>
            </td>

            <!-- COLUMNA: Redirecciones (Color Azul) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                {{ developer.redirections ?? 0 }}
              </span>
            </td>

            <!-- COLUMNA: Tiempo Promedio -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm font-medium text-gray-900 dark:text-white">{{ (developer.averageHoursPerTicket ?? 0).toFixed(1) }}h</span>
            </td>

            <!-- COLUMNA: Eficiencia (Código de colores) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="getEfficiencyClass(developer.efficiency ?? 0)"
                class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
              >
                {{ (developer.efficiency ?? 0).toFixed(2) }}
              </span>
            </td>

            <!-- COLUMNA: Índice de Bloqueo (Semáforo) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <span :class="getTrafficLightClass(developer.blocking_index ?? 0)" class="w-3 h-3 rounded-full"></span>
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ (developer.blocking_index ?? 0).toFixed(2) }}</span>
              </div>
            </td>

            <!-- COLUMNA: Índice Churn (Semáforo) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <span :class="getTrafficLightClass(developer.churn_index ?? 0)" class="w-3 h-3 rounded-full"></span>
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ (developer.churn_index ?? 0).toFixed(2) }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ESTRUCTURA DEL SCRIPT:
 * 1. Imports de librerías y dependencias
 * 2. Definición de tipos e interfaces
 * 3. Inicialización de stores y composables
 * 4. Referencias reactivas y estado
 * 5. Propiedades computadas
 * 6. Funciones de ordenamiento y utilidad
 * 7. Ciclo de vida del componente
 */

import { ref, computed, watch, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { UserPerformance } from '@/types'

const props = defineProps<{ appId: string }>()

// INICIALIZACIÓN
const analyticsStore = useAnalyticsStore()
const router = useRouter()
const { t } = useI18n()

// REFERENCIAS REACTIVAS
const selectedPeriod = ref('week')
const sortBy = ref<keyof UserPerformance>('efficiency')
const sortDesc = ref(true)

/**
 * Formatea un Date a string YYYY-MM-DD para el input type="date"
 */
function formatDate(d: Date): string {
  return d.toISOString().split('T')[0]
}

const dateFrom = ref(formatDate(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)))
const dateTo = ref(formatDate(new Date()))

/**
 * PROPIEDAD COMPUTADA: sortedPerformance
 * DESCRIPCIÓN: Ordena la lista de desempeño según los parámetros de ordenamiento
 * RETORNA: Array de desarrolladores ordenado
 */
const sortedPerformance = computed(() => {
  const data = [...(analyticsStore.performance || [])]

  return data.sort((a, b) => {
    const aVal = (a as any)[sortBy.value]
    const bVal = (b as any)[sortBy.value]
    
    // Convertir a número si es necesario
    const aNum = typeof aVal === 'number' ? aVal : 0
    const bNum = typeof bVal === 'number' ? bVal : 0
    
    return sortDesc.value ? bNum - aNum : aNum - bNum
  })
})

/**
 * FUNCIÓN: toggleSort
 * DESCRIPCIÓN: Alterna el ordenamiento de una columna
 * PARÁMETROS:
 * - field: Campo por el cual ordenar
 * COMPORTAMIENTO:
 * - Si se hace click en el mismo campo, invierte la dirección
 * - Si se hace click en otro campo, lo establece como nuevo campo de ordenamiento
 */
function toggleSort(field: keyof UserPerformance) {
  if (sortBy.value === field) {
    sortDesc.value = !sortDesc.value
  } else {
    sortBy.value = field
    sortDesc.value = true
  }
}

/**
 * FUNCIÓN: getEfficiencyClass
 * DESCRIPCIÓN: Retorna clases Tailwind según la puntuación de eficiencia (escala 0-100)
 * LÓGICA:
 * - >= 60: Verde (excelente)
 * - >= 30: Amarillo (aceptable)
 * - >= 10: Naranja (preocupante)
 * - < 10: Rojo (crítico)
 */
function getEfficiencyClass(score: number): string {
  if (score >= 60) {
    return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
  } else if (score >= 30) {
    return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
  } else if (score >= 10) {
    return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200'
  } else {
    return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
  }
}

/**
 * FUNCIÓN: getTrafficLightClass
 * DESCRIPCIÓN: Retorna clases de semáforo según valor del índice (escala 0-100)
 * LÓGICA:
 * - >= 80: Rojo (crítico)
 * - >= 50: Ámbar (precaución)
 * - < 50: Verde (bien)
 */
function getTrafficLightClass(value: number): string {
  if (value >= 80) {
    return 'bg-red-500'
  } else if (value >= 50) {
    return 'bg-amber-500'
  } else {
    return 'bg-green-500'
  }
}

/**
 * FUNCIÓN: selectDeveloper
 * DESCRIPCIÓN: Abre el drill-down para un desarrollador específico
 * PARÁMETROS:
 * - developer: Objeto del desarrollador seleccionado
 * ACCIÓN: Navega a vista de detalles del desarrollador
 */
function selectDeveloper(developer: UserPerformance) {
  router.push({ name: 'TeamManagement', query: { userId: developer.userId } })
}

/**
 * Dispara la carga de datos usando el rango de fechas actual del store
 */
async function loadPerformance(): Promise<void> {
  try {
    const fromDate = new Date(dateFrom.value)
    const toDate = new Date(dateTo.value)
    analyticsStore.setDateRange(fromDate, toDate)
    await analyticsStore.fetchPerformance(props.appId, dateFrom.value, dateTo.value)
  } catch (err) {
    console.error('Error cargando datos de desempeño:', err)
  }
}

/**
 * Cuando el usuario cambia un input de fecha manualmente, marca el período
 * como personalizado y dispara la carga
 */
function onDateChange(): void {
  selectedPeriod.value = 'custom'
  loadPerformance()
}

/**
 * Cuando el selector de período cambia, calcula las fechas correspondientes
 * y dispara la carga
 */
watch(selectedPeriod, (period) => {
  if (period === 'custom') return
  const to = new Date()
  const from = new Date()
  if (period === 'week') from.setDate(from.getDate() - 7)
  else if (period === 'month') from.setMonth(from.getMonth() - 1)
  else if (period === 'quarter') from.setMonth(from.getMonth() - 3)
  dateFrom.value = formatDate(from)
  dateTo.value = formatDate(to)
  loadPerformance()
})

/**
 * CICLO DE VIDA: onMounted
 * RESPONSABILIDADES:
 * - Cargar datos de desempeño con el período inicial (semana)
 */
onMounted(() => {
  loadPerformance()
})
</script>

<style scoped>
/* Estilos personalizados para la tabla */

/* Animación de las barras de progreso */
@keyframes fillBar {
  from {
    width: 0;
  }
}

:deep(.bg-green-500) {
  animation: fillBar 0.6s ease-out;
}
</style>
