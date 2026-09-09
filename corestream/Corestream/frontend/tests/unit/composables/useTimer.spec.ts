import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useTimer } from '@/composables/useTimer'

describe('useTimer Composable', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('debe inicializar con valores por defecto', () => {
    const { elapsed, isRunning, formatted } = useTimer(0)
    expect(elapsed.value).toBe(0)
    expect(isRunning.value).toBe(false)
    expect(formatted.value).toBe('00:00:00')
  })

  it('debe formatear correctamente el tiempo según el README (3665s -> 01:01:05)', () => {
    // Simulamos un valor transcurrido
    const { formatted } = useTimer(3665) 
    expect(formatted.value).toBe('01:01:05')
  })

  it('debe gestionar correctamente la máquina de estados (Start -> Pause -> Resume)', () => {
    const { start, pause, resume, isRunning, isPaused } = useTimer(0)
    
    start()
    expect(isRunning.value).toBe(true)
    
    pause()
    expect(isPaused.value).toBe(true)
    expect(isRunning.value).toBe(false)
    
    resume()
    expect(isPaused.value).toBe(false)
    expect(isRunning.value).toBe(true)
  })

  it('debe detenerse y devolver los segundos totales', () => {
    const { start, stop, isRunning } = useTimer(10)
    start()
    
    // El método stop debe limpiar el estado y retornar el valor acumulado
    const total = stop()
    expect(total).toBeGreaterThanOrEqual(10)
    expect(isRunning.value).toBe(false)
  })
})