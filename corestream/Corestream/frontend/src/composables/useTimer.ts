/**
 * Composable useTimer.ts
 * 
 * Composable de cronómetro reactivo para tracking de tiempo en tickets de CoreStream.
 * Utiliza requestAnimationFrame para actualizaciones suaves sin bloquear el UI principal.
 * Soporta pausa (cuando un ticket está bloqueado) y reanudación de la cuenta.
 * 
 * Características:
 * - Precisión basada en timestamp del sistema
 * - Pausable para tickets bloqueados
 * - Formato automático a "HH:MM:SS"
 * - Uso de requestAnimationFrame para mejor rendimiento
 * - Acumulación de tiempo durante pausas
 * - Limpieza automática al desmontar
 * 
 * Uso:
 * const { elapsed, formatted, start, pause, resume, stop } = useTimer()
 * start() // Comenzar a contar
 * pause() // Pausar cuando se bloquea
 * resume() // Reanudar cuando se desbloquea
 * const totalSeconds = stop() // Obtener total al terminar
 */

import { ref, computed, onUnmounted } from 'vue'
import type { Ref, ComputedRef } from 'vue'

/**
 * Composable de cronómetro para tracking de tiempo
 * Proporciona control completo sobre el tiempo transcurrido
 * 
 * @param initialSeconds - Segundos iniciales (por defecto 0)
 * @returns Objeto con propiedades y métodos del cronómetro
 */
export function useTimer(initialSeconds: number = 0) {
  // =========================================================================
  // ESTADO REACTIVO - Variables para rastrear el estado del cronómetro
  // =========================================================================

  /**
   * Tiempo total transcurrido en segundos
   * Se actualiza continuamente durante la ejecución
   * Se acumula durante pausas y se restaura al reanudar
   */
  const elapsed: Ref<number> = ref(initialSeconds)

  /**
   * Indica si el cronómetro está activamente contando
   * true = contando, false = detenido
   */
  const isRunning: Ref<boolean> = ref(false)

  /**
   * Indica si el cronómetro está en pausa
   * true = pausado (tiempo acumulado pero no contando), false = normal
   */
  const isPaused: Ref<boolean> = ref(false)

  // =========================================================================
  // VARIABLES PRIVADAS - Estado interno del cronómetro
  // =========================================================================

  /**
   * Timestamp (en milisegundos) cuando se inició la ejecución actual
   * Se usa para calcular el delta de tiempo en cada frame
   */
  let startTimestamp: number = 0

  /**
   * Tiempo acumulado en segundos
   * Se mantiene entre pausas y reanudaciones
   * Se suma al tiempo actual para obtener el total
   */
  let accumulatedTime: number = initialSeconds

  /**
   * ID del requestAnimationFrame
   * Se guarda para poder cancelar la animación en cleanup
   */
  let animationFrameId: number | null = null

  // =========================================================================
  // CONSTANTES - Configuración del cronómetro
  // =========================================================================

  /**
   * Conversión de milisegundos a segundos
   * Usado para convertir timestamps a segundos decimales
   */
  const MS_TO_SECONDS = 1000

  // =========================================================================
  // PROPIEDADES COMPUTADAS - Valores derivados del tiempo
  // =========================================================================

  /**
   * Tiempo formateado como string "HH:MM:SS"
   * Se calcula reactivamente basado en elapsed
   * 
   * @returns String con formato "HH:MM:SS" (ej: "01:23:45")
   */
  const formatted: ComputedRef<string> = computed(() => {
    // Redondear el tiempo total a segundos enteros
    const totalSeconds = Math.floor(elapsed.value)

    // Calcular horas, minutos y segundos
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    // Formatear con padding de ceros (ej: 01, 09, 00)
    const paddedHours = String(hours).padStart(2, '0')
    const paddedMinutes = String(minutes).padStart(2, '0')
    const paddedSeconds = String(seconds).padStart(2, '0')

    return `${paddedHours}:${paddedMinutes}:${paddedSeconds}`
  })

  // =========================================================================
  // MÉTODOS PRIVADOS - Funciones internas del cronómetro
  // =========================================================================

  /**
   * Función tick del cronómetro usando requestAnimationFrame
   * Se llama automáticamente en cada frame (aprox 60fps)
   * Calcula el delta de tiempo desde el último frame y actualiza elapsed
   * 
   * @param timestamp - Timestamp en milisegundos proporcionado por rAF
   */
  function tick(timestamp: number): void {
    // Si no es la primera ejecución, calcular delta
    if (startTimestamp !== 0) {
      // Delta de tiempo en milisegundos desde el último frame
      const deltaMs = timestamp - startTimestamp

      // Convertir a segundos y sumar al tiempo total
      const deltaSeconds = deltaMs / MS_TO_SECONDS
      elapsed.value = accumulatedTime + deltaSeconds
    }

    // Actualizar timestamp para el siguiente frame
    startTimestamp = timestamp

    // Solicitar siguiente frame si sigue corriendo
    if (isRunning.value) {
      animationFrameId = requestAnimationFrame(tick)
    }
  }

  // =========================================================================
  // MÉTODOS PÚBLICOS - API del cronómetro
  // =========================================================================

  /**
   * Inicia el cronómetro desde el tiempo acumulado
   * Si ya estaba en pausa, continúa desde donde se pausó
   * Si estaba detenido, comienza desde 0 (a menos que haya tiempo acumulado)
   */
  function start(): void {
    // Solo iniciar si no está ya corriendo
    if (isRunning.value) {
      console.warn('El cronómetro ya está en ejecución')
      return
    }

    // Marcar como ejecutándose
    isRunning.value = true
    isPaused.value = false

    // Resetear timestamp para la primera ejecución
    startTimestamp = 0

    // Solicitar el primer frame de animación
    animationFrameId = requestAnimationFrame(tick)

    console.log('Cronómetro iniciado')
  }

  /**
   * Pausa el cronómetro
   * Guarda el tiempo acumulado y detiene la ejecución
   * El tiempo se puede reanudar llamando a resume()
   * Útil cuando un ticket se bloquea o se suspende
   */
  function pause(): void {
    // Solo pausar si está en ejecución
    if (!isRunning.value) {
      console.warn('El cronómetro no está en ejecución')
      return
    }

    // Guardar tiempo acumulado actual (antes de pausar)
    accumulatedTime = elapsed.value

    // Cancelar la animación en progreso
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }

    // Marcar como pausado
    isRunning.value = false
    isPaused.value = true

    console.log(`Cronómetro pausado en ${formatted.value}`)
  }

  /**
   * Reanuda el cronómetro desde donde fue pausado
   * Restaura la ejecución sin perder el tiempo acumulado
   * Útil cuando un ticket que estaba bloqueado se desbloquea
   */
  function resume(): void {
    // Solo reanudar si está pausado
    if (!isPaused.value) {
      console.warn('El cronómetro no está pausado')
      return
    }

    // Reanudar la ejecución desde el tiempo guardado
    start()

    console.log(`Cronómetro reanudado desde ${formatted.value}`)
  }

  /**
   * Detiene el cronómetro y retorna el tiempo total acumulado
   * Cancela la animación y reinicia el estado
   * El tiempo se pierde a menos que se guarde el valor retornado
   * 
   * @returns Número de segundos totales transcurridos
   */
  function stop(): number {
    // Detener la ejecución
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }

    // Resetear estado
    isRunning.value = false
    isPaused.value = false

    // Guardar valor final
    const finalTime = elapsed.value

    // Resetear para siguiente uso
    startTimestamp = 0
    accumulatedTime = 0
    elapsed.value = 0

    console.log(`Cronómetro detenido. Tiempo total: ${formatted.value}`)

    // Retornar tiempo final en segundos
    return finalTime
  }

  /**
   * Reinicia el cronómetro a cero
   * Detiene la ejecución si está en marcha y resetea todo el estado
   * Útil para limpiar y permitir una nueva medición
   */
  function reset(): void {
    // Detener si está corriendo
    if (isRunning.value) {
      stop()
    }

    // Cancelar animación si existe
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }

    // Resetear completamente
    elapsed.value = 0
    isRunning.value = false
    isPaused.value = false
    startTimestamp = 0
    accumulatedTime = 0

    console.log('Cronómetro reiniciado')
  }

  // =========================================================================
  // LIMPIEZA - Hook de desmontaje del componente
  // =========================================================================

  /**
   * Hook de ciclo de vida: se ejecuta cuando el componente es desmontado
   * Garantiza la limpieza de recursos (cancelar animaciones)
   * Evita memory leaks y comportamientos inesperados
   */
  onUnmounted(() => {
    // Detener el cronómetro si está en ejecución
    if (isRunning.value) {
      stop()
    }

    // Cancelar requestAnimationFrame si existe
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId)
      animationFrameId = null
    }

    console.log('Cronómetro desmontado y limpiado')
  })

  // =========================================================================
  // RETORNO DEL COMPOSABLE - API pública
  // =========================================================================

  return {
    // Propiedades reactivas
    elapsed,        // Tiempo en segundos (decimal)
    isRunning,      // true = ejecutando, false = detenido
    isPaused,       // true = pausado, false = normal
    formatted,      // String formateado "HH:MM:SS"

    // Métodos públicos para control
    start,    // Inicia o reanuda desde pausa
    pause,    // Pausa el tiempo actual
    resume,   // Continúa desde pausa
    stop,     // Detiene y retorna tiempo total
    reset     // Reinicia a cero
  }
}
