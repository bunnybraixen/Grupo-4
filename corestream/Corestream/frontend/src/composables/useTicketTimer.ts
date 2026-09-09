/**
 * Composable useTicketTimer.ts
 *
 * Gestiona el cronómetro de un ticket de forma inteligente:
 * - Inicializa el tiempo de trabajo desde ticket.timeSpentSeconds (datos del servidor)
 * - Inicializa el tiempo de bloqueo desde ticket.blockedTimeSeconds (datos del servidor)
 * - Se resetea y reinicializa automáticamente cuando se abre un ticket diferente
 * - Responde a los cambios de estado del ticket (IN_PROGRESS / BLOCKED / COMPLETED)
 *
 * Arquitectura:
 * - `savedWorkSeconds` / `savedBlockedSeconds`: base persistida en el servidor al abrir el panel
 * - `workTimer` / `blockedTimer`: instancias de useTimer que acumulan la sesión actual
 * - `totalWorkSeconds` = savedWorkSeconds + workTimer.elapsed  (lo que se muestra en pantalla)
 * - `totalBlockedSeconds` = savedBlockedSeconds + blockedTimer.elapsed
 *
 * Uso:
 * const ticket = computed(() => props.ticket)
 * const { totalWorkSeconds, totalBlockedSeconds, isWorking, isBlocked, startWork, ... } = useTicketTimer(ticket)
 */

import { ref, computed, watch } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import type { Ticket } from '@/types'
import { useTimer } from './useTimer'

// ============================================================================
// TIPOS PÚBLICOS
// ============================================================================

export interface TicketTimerState {
  totalWorkSeconds: ComputedRef<number>
  totalBlockedSeconds: ComputedRef<number>
  workFormatted: ComputedRef<string>
  blockedFormatted: ComputedRef<string>
  isWorking: Ref<boolean>
  isBlocked: Ref<boolean>
  startWork: () => void
  pauseWork: () => void
  resumeWork: () => void
  stopWork: () => void
  startBlocked: () => void
  pauseBlocked: () => void
}

// ============================================================================
// UTILIDAD PRIVADA
// ============================================================================

function formatSeconds(total: number): string {
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

// ============================================================================
// COMPOSABLE PRINCIPAL
// ============================================================================

export function useTicketTimer(ticketRef: Ref<Ticket>): TicketTimerState {
  const workTimer = useTimer()
  const blockedTimer = useTimer()

  // Valores base del servidor al momento de abrir el panel
  const savedWorkSeconds = ref(0)
  const savedBlockedSeconds = ref(0)

  // Totales reactivos: base guardada + tiempo acumulado en la sesión actual
  const totalWorkSeconds: ComputedRef<number> = computed(
    () => savedWorkSeconds.value + Math.floor(workTimer.elapsed.value)
  )
  const totalBlockedSeconds: ComputedRef<number> = computed(
    () => savedBlockedSeconds.value + Math.floor(blockedTimer.elapsed.value)
  )

  // --------------------------------------------------------------------------
  // Sincronización de timers con el estado del ticket
  // --------------------------------------------------------------------------

  function syncTimersWithStatus(status: string): void {
    if (status === 'IN_PROGRESS') {
      if (blockedTimer.isRunning.value) blockedTimer.pause()
      if (!workTimer.isRunning.value && !workTimer.isPaused.value) workTimer.start()
      else if (workTimer.isPaused.value) workTimer.resume()
    } else if (status === 'BLOCKED' || status === 'BLOCKED_QUESTION') {
      // BLOCKED_QUESTION (pregunta del developer) cuenta como bloqueo: pausa el
      // trabajo y corre el cronómetro de bloqueo igual que un BLOCKED normal.
      if (workTimer.isRunning.value) workTimer.pause()
      if (!blockedTimer.isRunning.value && !blockedTimer.isPaused.value) blockedTimer.start()
      else if (blockedTimer.isPaused.value) blockedTimer.resume()
    } else {
      // TODO, COMPLETED, REDIRECTED
      if (workTimer.isRunning.value) workTimer.stop()
      if (blockedTimer.isRunning.value) blockedTimer.stop()
    }
  }

  // --------------------------------------------------------------------------
  // Watchers
  // --------------------------------------------------------------------------

  // Reinicializa ambos timers cuando se abre un ticket diferente
  watch(
    () => ticketRef.value.id,
    () => {
      workTimer.reset()
      blockedTimer.reset()
      savedWorkSeconds.value = ticketRef.value.timeSpentSeconds || 0
      savedBlockedSeconds.value = ticketRef.value.blockedTimeSeconds || 0
      syncTimersWithStatus(ticketRef.value.status)
    },
    { immediate: true }
  )

  // Responde a cambios de estado posteriores (sin immediate: la inicialización ya la hace el watcher de id)
  watch(() => ticketRef.value.status, syncTimersWithStatus)

  // --------------------------------------------------------------------------
  // API pública
  // --------------------------------------------------------------------------

  const startWork = (): void => {
    if (!workTimer.isRunning.value) workTimer.start()
  }

  const pauseWork = (): void => {
    if (workTimer.isRunning.value) workTimer.pause()
  }

  const resumeWork = (): void => {
    if (workTimer.isPaused.value) workTimer.resume()
    else if (!workTimer.isRunning.value) workTimer.start()
  }

  const stopWork = (): void => {
    workTimer.stop()
    blockedTimer.stop()
  }

  const startBlocked = (): void => {
    if (!blockedTimer.isRunning.value && !blockedTimer.isPaused.value) blockedTimer.start()
    else if (blockedTimer.isPaused.value) blockedTimer.resume()
  }

  const pauseBlocked = (): void => {
    if (blockedTimer.isRunning.value) blockedTimer.pause()
  }

  return {
    totalWorkSeconds,
    totalBlockedSeconds,
    workFormatted: computed(() => formatSeconds(totalWorkSeconds.value)),
    blockedFormatted: computed(() => formatSeconds(totalBlockedSeconds.value)),
    isWorking: workTimer.isRunning,
    isBlocked: blockedTimer.isRunning,
    startWork,
    pauseWork,
    resumeWork,
    stopWork,
    startBlocked,
    pauseBlocked,
  }
}
