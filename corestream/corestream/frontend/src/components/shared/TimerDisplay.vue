<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Mostrador de Timer -->
  <!-- ================================================================ -->
  <!-- Muestra tiempo transcurrido en formato HH:MM:SS -->
  <!-- Estados visuales: ejecutándose, pausado/bloqueado -->
  <!-- Ícono de reloj y tooltip informativo -->
  <!-- ================================================================ -->

  <div
    class="flex items-center gap-2 px-3 py-2 rounded-lg"
    :class="[
      'transition-colors duration-200',
      isPaused
        ? 'bg-orange-900 bg-opacity-30 border border-orange-700'
        : 'bg-slate-700 border border-slate-600'
    ]"
    :title="getTooltip"
  >
    <!-- Ícono de reloj -->
    <Icon
      icon="mdi:clock-outline"
      :class="[
        'text-lg flex-shrink-0',
        isPaused ? 'text-orange-400 animate-pulse' : 'text-slate-400'
      ]"
    />

    <!-- Mostrador de tiempo HH:MM:SS -->
    <span
      :class="[
        'font-mono text-sm font-semibold',
        isPaused
          ? 'text-orange-300'
          : isRunning
            ? 'text-white'
            : 'text-slate-400'
      ]"
    >
      {{ formattedTime }}
    </span>

    <!-- Indicador visual de estado (punto pulsante) -->
    <span
      v-if="isRunning"
      class="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse flex-shrink-0"
    />
    <span
      v-else-if="isPaused"
      class="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse flex-shrink-0"
    />
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { computed } from 'vue'
import { Icon } from '@iconify/vue'

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  // Tiempo en segundos
  seconds: number
  // Indica si el timer está corriendo
  isRunning: boolean
  // Indica si el timer está pausado (bloqueado)
  isPaused: boolean
}

const props = defineProps<Props>()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Formatea los segundos a formato HH:MM:SS
 * Ejemplo: 3661 segundos = 01:01:01
 */
const formattedTime = computed(() => {
  const hours = Math.floor(props.seconds / 3600)
  const minutes = Math.floor((props.seconds % 3600) / 60)
  const secs = props.seconds % 60

  const formatNumber = (n: number): string => String(n).padStart(2, '0')

  return `${formatNumber(hours)}:${formatNumber(minutes)}:${formatNumber(secs)}`
})

/**
 * Genera tooltip con estado del timer
 * Muestra información sobre si está ejecutándose, pausado o bloqueado
 */
const getTooltip = computed(() => {
  if (props.isPaused) {
    return 'Pausado por bloqueo - Tiempo no se incrementa'
  } else if (props.isRunning) {
    return 'Tiempo de ejecución - Se está contando'
  } else {
    return 'Timer pausado - Esperando inicio'
  }
})

// =====================================================================
// NOTAS
// =====================================================================

/**
 * Este componente es un visualizador pasivo de tiempo.
 * El contador real se maneja en componentes padre con el composable useTimer.
 * 
 * Props esperados:
 * - seconds: número de segundos transcurridos
 * - isRunning: booleano indicando si cuenta activamente
 * - isPaused: booleano indicando si está pausado por bloqueo
 * 
 * Cambios visuales según estado:
 * 1. EJECUTÁNDOSE: texto blanco, punto verde pulsante
 * 2. PAUSADO/BLOQUEADO: texto naranja, punto naranja pulsante
 * 3. PARADO: texto gris, sin punto
 */
</script>

<style scoped>
/* El componente usa Tailwind CSS para todos los estilos */
/* No se requieren estilos personalizados adicionales */
</style>
