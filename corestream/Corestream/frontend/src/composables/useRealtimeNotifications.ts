/**
 * Notificaciones en tiempo real (WebSocket)
 *
 * Abre `/api/ws/notifications/{userId}?token=...` (ver backend app/main.py),
 * que reenvía lo que el backend publica en el canal Redis
 * `notifications:{userId}` — p. ej. TICKET_REDIRECTED cuando a alguien le
 * redirigen un ticket.
 *
 * Cada mensaje se re-emite como evento de ventana `corestream:realtime`, así
 * cualquier vista (campana de notificaciones, workbench) puede reaccionar sin
 * acoplarse a la conexión:
 *
 *   window.addEventListener(REALTIME_EVENT, (e) => { ... (e as CustomEvent).detail })
 *
 * Se monta una sola vez desde los layouts autenticados.
 */

import { onMounted, onUnmounted } from 'vue'

export const REALTIME_EVENT = 'corestream:realtime'

export interface RealtimeMessage {
  type: string
  ticket_id?: string
  title?: string
  message?: string
}

const MAX_RETRY_DELAY_MS = 30_000

export function useRealtimeNotifications() {
  let socket: WebSocket | null = null
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  let retryDelay = 1_000
  let stopped = false

  const connect = (): void => {
    const userId = localStorage.getItem('userId')
    const token = localStorage.getItem('accessToken')
    if (stopped || !userId || !token) return

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const url = `${protocol}://${window.location.host}/api/ws/notifications/${userId}?token=${encodeURIComponent(token)}`

    socket = new WebSocket(url)

    socket.onopen = () => {
      retryDelay = 1_000
    }

    socket.onmessage = (event: MessageEvent) => {
      try {
        const detail = JSON.parse(event.data) as RealtimeMessage
        window.dispatchEvent(new CustomEvent<RealtimeMessage>(REALTIME_EVENT, { detail }))
      } catch {
        // Mensaje que no es JSON: se ignora
      }
    }

    socket.onclose = () => {
      socket = null
      if (stopped) return
      // Reconexión con espera creciente; al reconectar se lee el token
      // vigente (el interceptor HTTP lo renueva cuando caduca).
      retryTimer = setTimeout(connect, retryDelay)
      retryDelay = Math.min(retryDelay * 2, MAX_RETRY_DELAY_MS)
    }
  }

  onMounted(connect)

  onUnmounted(() => {
    stopped = true
    if (retryTimer) clearTimeout(retryTimer)
    socket?.close()
    socket = null
  })
}
