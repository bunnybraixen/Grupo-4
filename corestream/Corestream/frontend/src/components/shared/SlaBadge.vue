<!--
  Badge de SLA del ticket (module Sprints + SLA)

  Muestra el estado del SLA calculado a nivel de TICKET:
  En plazo (ON_TRACK), Próximo a vencer (AT_RISK), Incumplido (BREACHED) o
  Cumplido (MET). El SLA no depende del Sprint: depende de la prioridad del
  ticket y de los objetivos definidos por el ADMIN.
-->
<template>
  <span
    v-if="status"
    :class="[
      'inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold whitespace-nowrap',
      stateClasses
    ]"
    :title="tooltip"
  >
    <Icon :icon="stateIcon" class="text-xs flex-shrink-0" />
    <span>{{ label }}</span>
    <span v-if="!compact && countdown" class="font-normal opacity-90">· {{ countdown }}</span>
  </span>
</template>

<script setup lang="ts">
/**
 * SlaBadge - Indicador visual del estado de SLA de un ticket.
 */
import { computed } from 'vue'
import Icon from '@/components/common/IconFallback.vue'
import type { TicketSlaStatus } from '@/types/sprint'

const props = defineProps<{
  /** Estado de SLA del ticket (lo calcula el backend en /sla/statuses) */
  status?: TicketSlaStatus | null
  /** Oculta la cuenta regresiva para tarjetas compactas */
  compact?: boolean
}>()

/** Estado global del SLA */
const state = computed(() => props.status?.state ?? 'ON_TRACK')

/** Etiqueta corta según el estado */
const label = computed(() => {
  switch (state.value) {
    case 'BREACHED':
      return 'SLA incumplido'
    case 'AT_RISK':
      return 'SLA próximo a vencer'
    case 'MET':
      return 'SLA cumplido'
    default:
      return 'SLA en plazo'
  }
})

/** Clases de color por estado (compatibles con tema claro y oscuro) */
const stateClasses = computed(() => {
  switch (state.value) {
    case 'BREACHED':
      return 'bg-red-500/15 text-red-400 border-red-500/40'
    case 'AT_RISK':
      return 'bg-amber-500/15 text-amber-400 border-amber-500/40'
    case 'MET':
      return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40'
    default:
      return 'bg-slate-500/15 text-slate-400 border-slate-500/40'
  }
})

const stateIcon = computed(() => {
  switch (state.value) {
    case 'BREACHED':
      return 'mdi:alert-octagon'
    case 'AT_RISK':
      return 'mdi:alert-circle'
    case 'MET':
      return 'mdi:check-decagram'
    default:
      return 'mdi:clock-outline'
  }
})

/** Tiempo restante formateado (o tiempo excedido si ya incumplió) */
const countdown = computed(() => {
  if (!props.status) return ''
  const minutes = props.status.minutesToNextDeadline
  if (minutes === null || minutes === undefined) {
    return props.status.isResolved ? '' : `${formatMinutes(Math.max(0, -props.status.resolutionRemainingMinutes))}`
  }
  if (minutes < 0) return `${formatMinutes(Math.abs(minutes))} excedido`
  return `${formatMinutes(minutes)} restantes`
})

/** Detalle para el tooltip: objetivo de respuesta y de resolución */
const tooltip = computed(() => {
  if (!props.status) return ''
  const lines = [
    `SLA del ticket (prioridad ${props.status.priority})`,
    `Respuesta: objetivo ${formatMinutes(props.status.responseTargetMinutes)} · ${translateState(props.status.responseState)}`,
    `Resolución: objetivo ${formatMinutes(props.status.resolutionTargetMinutes)} · ${translateState(props.status.resolutionState)}`
  ]
  if (props.status.nextDeadlineAt) {
    lines.push(`Próximo vencimiento: ${formatDateTime(props.status.nextDeadlineAt)}`)
  }
  return lines.join('\n')
})

/** Convierte minutos en texto legible (min / h / d) */
function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${Math.round(minutes)} min`
  if (minutes < 1440) {
    const hours = minutes / 60
    return `${hours.toFixed(hours < 10 ? 1 : 0)} h`
  }
  const days = minutes / 1440
  return `${days.toFixed(days < 10 ? 1 : 0)} d`
}

/** Traduce el estado de un objetivo de SLA */
function translateState(value: string): string {
  const map: Record<string, string> = {
    ON_TRACK: 'en plazo',
    AT_RISK: 'próximo a vencer',
    BREACHED: 'incumplido',
    MET: 'cumplido',
    NOT_APPLICABLE: 'sin SLA'
  }
  return map[value] ?? value
}

/** Fecha/hora local legible */
function formatDateTime(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}
</script>
