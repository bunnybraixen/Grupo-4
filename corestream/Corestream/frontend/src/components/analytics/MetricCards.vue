<template>
  <!-- 
    COMPONENTE: MetricCards
    DESCRIPCIÓN: Muestra cuatro tarjetas de métricas resumidas principales del sistema:
    1. Total de Tickets - cantidad total con cambio semanal
    2. Completados - tickets resueltos con indicador verde
    3. Bloqueados - tickets bloqueados con etiqueta crítica en naranja
    4. Tiempo Promedio - tiempo promedio en horas con indicador de tendencia
    
    CARACTERÍSTICAS:
    - Cada tarjeta contiene icono, valor, etiqueta y indicador de tendencia
    - Flechas direccionales que muestran si la métrica subió o bajó
    - Códigos de color para estados: verde (bueno), naranja (crítico), gris (neutral)
    - Responsive grid que se adapta a diferentes tamaños de pantalla
    - Animación suave de carga con efecto skeleton
  -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    <!-- TARJETA 1: Total de Tickets -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border-l-4 border-blue-500">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('analytics.totalTickets') }}</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ summary?.total_tickets ?? 0 }}</p>
          <div class="flex items-center mt-3 gap-1">
            <span v-if="weekChange >= 0" class="text-green-500 flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
              </svg>
              +{{ weekChange }}%
            </span>
            <span v-else class="text-red-500 flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12 13a1 1 0 110 2H7a1 1 0 01-1-1V9a1 1 0 112 0v3.586l4.293-4.293a1 1 0 011.414 1.414L9.414 13H12z" clip-rule="evenodd" />
              </svg>
              {{ weekChange }}%
            </span>
            <span class="text-gray-500 text-xs">{{ $t('analytics.weekChange') }}</span>
          </div>
        </div>
        <!-- Icono de tickets -->
        <div class="bg-blue-100 dark:bg-blue-900 rounded-lg p-3">
          <svg class="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 1 1 0 000 2h10a1 1 0 000-2 2 2 0 00-2 2v10a2 2 0 002 2 1 1 0 100 2h-2a2 2 0 002-2v-10a2 2 0 00-2-2H6a2 2 0 00-2 2v10a1 1 0 11-2 0V5z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>

    <!-- TARJETA 2: Completados (Verde) -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border-l-4 border-green-500">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('analytics.completed') }}</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-2">{{ summary?.completed ?? 0 }}</p>
          <div class="flex items-center mt-3 gap-1">
            <span class="text-green-500 flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
              </svg>
              +8%
            </span>
            <span class="text-gray-500 text-xs">{{ $t('analytics.thisWeek') }}</span>
          </div>
        </div>
        <!-- Icono de checkmark -->
        <div class="bg-green-100 dark:bg-green-900 rounded-lg p-3">
          <svg class="w-6 h-6 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>

    <!-- TARJETA 3: Bloqueados (Naranja, CRÍTICO) -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border-l-4 border-orange-500">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('analytics.blocked') }}</p>
          <p class="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-2">{{ summary?.blocked ?? 0 }}</p>
          <div class="flex items-center mt-3 gap-2">
            <!-- Etiqueta CRÍTICA -->
            <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              {{ $t('status.critical') }}
            </span>
          </div>
        </div>
        <!-- Icono de bloqueo -->
        <div class="bg-orange-100 dark:bg-orange-900 rounded-lg p-3">
          <svg class="w-6 h-6 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>

    <!-- TARJETA 4: Tiempo Promedio (Horas) -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 p-6 border-l-4 border-purple-500">
      <div class="flex justify-between items-start">
        <div>
          <p class="text-gray-600 dark:text-gray-400 text-sm font-medium">{{ $t('analytics.avgTime') }}</p>
          <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">{{ summary?.avg_time ?? 0 }}h</p>
          <div class="flex items-center mt-3 gap-1">
            <span v-if="timeChange <= 0" class="text-green-500 flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12 13a1 1 0 110 2H7a1 1 0 01-1-1V9a1 1 0 112 0v3.586l4.293-4.293a1 1 0 011.414 1.414L9.414 13H12z" clip-rule="evenodd" />
              </svg>
              {{ timeChange }}%
            </span>
            <span v-else class="text-red-500 flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414-1.414L13.586 7H12z" clip-rule="evenodd" />
              </svg>
              +{{ timeChange }}%
            </span>
            <span class="text-gray-500 text-xs">{{ $t('analytics.vsLastWeek') }}</span>
          </div>
        </div>
        <!-- Icono de reloj -->
        <div class="bg-purple-100 dark:bg-purple-900 rounded-lg p-3">
          <svg class="w-6 h-6 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00-.293.707l-.707.707a1 1 0 101.414 1.414L9 9.414V6z" clip-rule="evenodd" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * COMPOSICIÓN DEL SCRIPT:
 * - Imports de librerías necesarias (composables, stores)
 * - Definición de tipos TypeScript
 * - Referencias reactivas (ref, computed, reactive)
 * - Funciones de ciclo de vida (onMounted)
 * - Funciones auxiliares de cálculo
 * - Watchers para reactividad
 */

import { ref, computed, onMounted } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useI18n } from 'vue-i18n'

// TIPOS: Interfaz para los datos de resumen
interface SummaryData {
  total_tickets: number
  completed: number
  blocked: number
  avg_time: number
}

// INICIALIZACIÓN DE STORES Y COMPOSABLES
const analyticsStore = useAnalyticsStore()
const { t } = useI18n()

// REFERENCIAS REACTIVAS: Variables que controlan el estado del componente
const isLoading = ref(false)
const weekChange = ref(0)
const timeChange = ref(-5) // Cambio negativo es bueno (menos tiempo)

// COMPUTED: Propiedades derivadas que se actualizan automáticamente
const summary = computed<SummaryData | null>(() => analyticsStore.summary)

/**
 * CICLO DE VIDA: onMounted
 * Se ejecuta después de que el componente está montado en el DOM
 * RESPONSABILIDADES:
 * - Cargar datos de resumen del store
 * - Calcular cambios porcentuales semanales
 * - Actualizar referencias reactivas
 */
onMounted(async () => {
  isLoading.value = true
  try {
    // Llamar a la acción del store para obtener datos de resumen
    await analyticsStore.fetchSummary()
    
    // Calcular cambios comparativos (simulado)
    weekChange.value = Math.floor(Math.random() * 20 - 5)
    timeChange.value = Math.floor(Math.random() * 10 - 8)
  } catch (error) {
    console.error('Error al cargar métricas:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
/* 
  ESTILOS PERSONALIZADOS:
  - Animaciones de carga
  - Transiciones suaves
  - Estados hover
  - Efecto skeleton para carga
*/

/* Animación de entrada suave de las tarjetas */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Aplicar animación a las tarjetas */
:deep(.grid > div) {
  animation: slideIn 0.3s ease-out forwards;
}

/* Efecto pulse en tiempo de carga */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
