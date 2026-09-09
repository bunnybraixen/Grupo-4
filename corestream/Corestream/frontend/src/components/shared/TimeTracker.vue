<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: TimeTracker -->
  <!-- ================================================================ -->
  <!-- Muestra de forma diferenciada:                                   -->
  <!--   1. Tiempo efectivo de trabajo (via TimerDisplay)               -->
  <!--   2. Tiempo total de bloqueo (solo si hay segundos > 0)          -->
  <!-- ================================================================ -->
  <div class="flex flex-col gap-1">
    <!-- Tiempo de trabajo efectivo -->
    <TimerDisplay
      :seconds="workSeconds"
      :is-running="isWorking"
      :is-paused="isBlocked"
    />

    <!-- Tiempo de bloqueo — solo visible si el ticket fue/está bloqueado -->
    <div
      v-if="blockedSeconds > 0 || isBlocked"
      class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-orange-950/40 border border-orange-800/40"
      title="Tiempo total acumulado en estado bloqueado"
    >
      <Icon
        icon="mdi:block-helper"
        class="text-sm flex-shrink-0 text-orange-500"
      />
      <span class="font-mono text-xs font-semibold text-orange-400">
        {{ formattedBlockedTime }}
      </span>
      <span class="text-xs text-orange-600/80">
        bloqueado
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import TimerDisplay from './TimerDisplay.vue'

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  workSeconds: number
  blockedSeconds: number
  isWorking: boolean
  isBlocked: boolean
}

const props = defineProps<Props>()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

const formattedBlockedTime = computed(() => {
  const h = Math.floor(props.blockedSeconds / 3600)
  const m = Math.floor((props.blockedSeconds % 3600) / 60)
  const s = props.blockedSeconds % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(h)}:${pad(m)}:${pad(s)}`
})
</script>
