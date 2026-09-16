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
        <div class="flex gap-2">
          <!-- Selector de período -->
          <select v-model="selectedPeriod" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
            <option value="week">{{ $t('period.thisWeek') }}</option>
            <option value="month">{{ $t('period.thisMonth') }}</option>
            <option value="quarter">{{ $t('period.thisQuarter') }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- TABLA DE DESEMPEÑO -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
          <tr>
            <!-- Encabezado: Desarrollador (no sorteable) -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('name')">
              <div class="flex items-center gap-2">
                {{ $t('table.developer') }}
                <svg v-if="sortBy === 'name'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Tickets Procesados (sorteable) -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('tickets')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.ticketsProcessed') }}
                <svg v-if="sortBy === 'tickets'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Preguntas -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('questions')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.questions') }}
                <svg v-if="sortBy === 'questions'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Redirecciones -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('redirects')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.redirects') }}
                <svg v-if="sortBy === 'redirects'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
            </th>

            <!-- Encabezado: Tiempo Promedio -->
            <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600" @click="toggleSort('avgTime')">
              <div class="flex items-center gap-2">
                {{ $t('analytics.avgTime') }}
                <svg v-if="sortBy === 'avgTime'" class="w-4 h-4" :class="{ 'rotate-180': sortDesc }" fill="currentColor" viewBox="0 0 20 20">
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
          <!-- FILA DE DATOS POR DESARROLLADOR -->
          <tr 
            v-for="developer in sortedPerformance" 
            :key="developer.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="selectDeveloper(developer)"
          >
            <!-- COLUMNA: Desarrollador (Avatar + Nombre) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-3">
                <!-- Avatar del desarrollador -->
                <img 
                  :src="developer.avatar" 
                  :alt="developer.name"
                  class="w-10 h-10 rounded-full object-cover border-2 border-gray-200 dark:border-gray-600"
                />
                <!-- Nombre (clickeable) -->
                <div>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ developer.name }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ developer.specialization }}</p>
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
                      :style="{ width: (developer.tickets_processed / 50) * 100 + '%' }"
                    ></div>
                  </div>
                </div>
                <span class="text-sm font-semibold text-gray-900 dark:text-white min-w-fit">{{ developer.tickets_processed }}</span>
              </div>
            </td>

            <!-- COLUMNA: Preguntas (Color Ámbar) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
                {{ developer.questions }}
              </span>
            </td>

            <!-- COLUMNA: Redirecciones (Color Azul) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                {{ developer.redirects }}
              </span>
            </td>

            <!-- COLUMNA: Tiempo Promedio -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="text-sm font-medium text-gray-900 dark:text-white">{{ developer.avg_time }}h</span>
            </td>

            <!-- COLUMNA: Eficiencia (Código de colores) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span 
                :class="getEfficiencyClass(developer.efficiency_score)"
                class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold"
              >
                {{ developer.efficiency_score.toFixed(2) }}
              </span>
            </td>

            <!-- COLUMNA: Índice de Bloqueo (Semáforo) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <span :class="getTrafficLightClass(developer.blocking_index)" class="w-3 h-3 rounded-full"></span>
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ developer.blocking_index.toFixed(2) }}</span>
              </div>
            </td>

            <!-- COLUMNA: Índice Churn (Semáforo) -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-2">
                <span :class="getTrafficLightClass(developer.churn_index)" class="w-3 h-3 rounded-full"></span>
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ developer.churn_index.toFixed(2) }}</span>
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

import { ref, computed, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

// TIPOS: Interfaz para datos de desarrollador
interface DeveloperPerformance {
  id: string
  name: string
  avatar: string
  specialization: string
  tickets_processed: number
  questions: number
  redirects: number
  avg_time: number
  efficiency_score: number
  blocking_index: number
  churn_index: number
}

// INICIALIZACIÓN
const analyticsStore = useAnalyticsStore()
const router = useRouter()
const { t } = useI18n()

// REFERENCIAS REACTIVAS
const selectedPeriod = ref('week')
const sortBy = ref<keyof DeveloperPerformance>('efficiency_score')
const sortDesc = ref(true)

/**
 * PROPIEDAD COMPUTADA: sortedPerformance
 * DESCRIPCIÓN: Ordena la lista de desempeño según los parámetros de ordenamiento
 * RETORNA: Array de desarrolladores ordenado
 */
const sortedPerformance = computed<DeveloperPerformance[]>(() => {
  const data = [...(analyticsStore.performanceData || [])]
  
  return data.sort((a, b) => {
    const aVal = a[sortBy.value]
    const bVal = b[sortBy.value]
    
    // Convertir a número si es necesario
    const aNum = typeof aVal === 'number' ? aVal : 0
    const bNum = typeof bVal === 'number' ? bNum : 0
    
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
function toggleSort(field: keyof DeveloperPerformance) {
  if (sortBy.value === field) {
    sortDesc.value = !sortDesc.value
  } else {
    sortBy.value = field
    sortDesc.value = true
  }
}

/**
 * FUNCIÓN: getEfficiencyClass
 * DESCRIPCIÓN: Retorna clases Tailwind según la puntuación de eficiencia
 * LÓGICA:
 * - >= 5.0: Verde (excelente)
 * - >= 3.0: Amarillo (bueno)
 * - >= 1.5: Naranja (aceptable)
 * - < 1.5: Rojo (crítico)
 */
function getEfficiencyClass(score: number): string {
  if (score >= 5) {
    return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
  } else if (score >= 3) {
    return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
  } else if (score >= 1.5) {
    return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200'
  } else {
    return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
  }
}

/**
 * FUNCIÓN: getTrafficLightClass
 * DESCRIPCIÓN: Retorna clases de semáforo según valor del índice
 * LÓGICA:
 * - >= 0.8: Rojo (crítico)
 * - >= 0.5: Ámbar (precaución)
 * - < 0.5: Verde (bien)
 */
function getTrafficLightClass(value: number): string {
  if (value >= 0.8) {
    return 'bg-red-500'
  } else if (value >= 0.5) {
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
function selectDeveloper(developer: DeveloperPerformance) {
  router.push({ name: 'DeveloperDetail', params: { id: developer.id } })
}

/**
 * CICLO DE VIDA: onMounted
 * RESPONSABILIDADES:
 * - Cargar datos de desempeño desde el store
 */
onMounted(async () => {
  try {
    await analyticsStore.fetchPerformance()
  } catch (error) {
    console.error('Error cargando datos de desempeño:', error)
  }
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
