/**
 * Composable useWebSocket.ts
 *
 * Composable de WebSocket para notificaciones en tiempo real en CoreStream.
 * Conecta al servidor FastAPI a través de WebSocket y recibe eventos push.
 * Implementa reconexión automática con backoff exponencial para mayor confiabilidad.
 *
 * DISEÑO — estado a nivel de módulo, no por llamada:
 * Antes, socket/isConnected/reconnectAttempts vivían DENTRO de useWebSocket(),
 * así que cada llamada creaba su propia conexión aislada sin relación con las
 * demás. Nada en la app llamaba nunca a connect() (solo ActionDock.vue
 * importaba el composable sin usarlo), así que ese defecto nunca se notó.
 * Ahora que stores/auth.ts sí llama a connect()/disconnect() en login/logout,
 * hace falta un singleton real: el estado vive a nivel de módulo, y cada
 * useWebSocket() devuelve referencias a la MISMA conexión.
 *
 * Por el mismo motivo se quitó el onUnmounted() que traía antes: solo
 * funciona si el composable se invoca dentro del setup() de un componente,
 * y aquí se invoca desde un store de Pinia. El ciclo de vida de la conexión
 * lo decide quien la abrió (login) y quien la cierra (logout), no el
 * montaje de un componente cualquiera.
 *
 * Autenticación del handshake (plan 3.2):
 * connect(userId) primero cambia el access token actual por un ticket de un
 * solo uso (POST /auth/ws-ticket) y lo manda como ?ticket=... — no el JWT
 * directamente, que quedaría escrito en los logs de acceso de cualquier
 * proxy delante de la app durante toda su vida útil.
 *
 * Uso:
 * const { isConnected, connect, disconnect, send } = useWebSocket()
 * await connect('user-id-123')
 */

import { ref } from 'vue'
import type { Ref } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import { NotificationType } from '@/types'
import { eventBus } from '@/utils/eventBus'
import api from '@/services/api'

interface WebSocketMessage {
  type: 'notification' | 'update' | 'error' | 'ping' | 'pong' | 'connected'
  data?: any
  message?: string
  timestamp?: string
}

// =========================================================================
// ESTADO A NIVEL DE MÓDULO — compartido por todas las llamadas a useWebSocket()
// =========================================================================

const socket: Ref<WebSocket | null> = ref(null)
const isConnected: Ref<boolean> = ref(false)
const reconnectAttempts: Ref<number> = ref(0)
let heartbeatIntervalId: ReturnType<typeof setInterval> | null = null

/** Usuario de la conexión actual, para poder reconectar sin que el caller lo repita. */
let currentUserId: string | null = null

/** Evita reconexiones simultáneas si handleClose se disparase más de una vez. */
let reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null

const maxReconnectAttempts = 10
const baseDelay = 1000
const maxDelay = 30000
const heartbeatInterval = 30000

function calculateBackoffDelay(): number {
  const exponentialDelay = baseDelay * Math.pow(2, reconnectAttempts.value)
  return Math.min(exponentialDelay, maxDelay)
}

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

function startHeartbeat(): void {
  if (heartbeatIntervalId) {
    clearInterval(heartbeatIntervalId)
  }

  heartbeatIntervalId = setInterval(() => {
    if (isConnected.value && socket.value) {
      try {
        send({ type: 'ping', timestamp: new Date().toISOString() })
      } catch (error) {
        console.warn('Error enviando heartbeat:', error)
      }
    }
  }, heartbeatInterval)
}

function stopHeartbeat(): void {
  if (heartbeatIntervalId) {
    clearInterval(heartbeatIntervalId)
    heartbeatIntervalId = null
  }
}

function handleMessage(event: MessageEvent): void {
  const notificationStore = useNotificationsStore()

  try {
    const message: WebSocketMessage = JSON.parse(event.data)

    switch (message.type) {
      case 'notification':
        if (message.data) {
          if (message.data.id && message.data.created_at !== undefined) {
            notificationStore.addNotification({
              id: message.data.id,
              userId: '',
              title: message.data.title ?? '',
              message: message.data.message ?? '',
              type: (message.data.type as NotificationType) ?? NotificationType.SYSTEM,
              isRead: message.data.is_read ?? false,
              ticketId: message.data.ticket_id ?? undefined,
              createdAt: message.data.created_at ?? message.timestamp ?? new Date().toISOString(),
            })
          } else {
            const eventType = message.data.eventType || message.data.type
            if (eventType === 'TIMER_SYNC') {
              eventBus.emit('timer-sync', message.data)
            } else {
              notificationStore.addNotification({
                id: message.data.id || generateId(),
                userId: '',
                title: message.data.title || 'Notificación',
                message: message.data.message || '',
                type: (message.data.type as NotificationType) || NotificationType.SYSTEM,
                isRead: false,
                ticketId: message.data.ticketId || message.data.ticket_id || undefined,
                createdAt: message.timestamp || new Date().toISOString(),
              })
            }
          }
        }
        break

      case 'update':
        eventBus.emit('ws-update', message.data)
        break

      case 'ping':
        try {
          send({ type: 'pong' })
        } catch {
          /* ignorar errores de envío del pong */
        }
        break

      case 'pong':
        break

      case 'connected':
        break

      case 'error':
        console.error('Error del servidor WebSocket:', message.message)
        notificationStore.addNotification({
          userId: '',
          id: generateId(),
          title: 'Error',
          message: message.message || 'Error del servidor',
          type: NotificationType.SYSTEM,
          createdAt: message.timestamp || new Date().toISOString(),
          isRead: false
        })
        break

      default:
        console.warn('Tipo de mensaje desconocido:', message.type)
    }
  } catch (error) {
    console.error('Error procesando mensaje WebSocket:', error)
  }
}

function handleClose(event: CloseEvent): void {
  isConnected.value = false
  socket.value = null
  stopHeartbeat()

  // Cierre intencional (disconnect()): no reconectar.
  if (event.code === 1000) return

  if (!currentUserId) return

  if (reconnectAttempts.value < maxReconnectAttempts) {
    const delay = calculateBackoffDelay()
    reconnectAttempts.value++

    if (reconnectTimeoutId) clearTimeout(reconnectTimeoutId)
    reconnectTimeoutId = setTimeout(() => {
      if (currentUserId) {
        connect(currentUserId)
      }
    }, delay)
  } else {
    console.error(`No se pudo conectar después de ${maxReconnectAttempts} intentos`)
    useNotificationsStore().addNotification({
      userId: '',
      id: generateId(),
      title: 'Conexión perdida',
      message: 'No se pudo establecer la conexión con el servidor',
      type: NotificationType.SYSTEM,
      createdAt: new Date().toISOString(),
      isRead: false
    })
  }
}

function handleError(event: Event): void {
  console.error('Error de WebSocket:', event)
  useNotificationsStore().addNotification({
    userId: '',
    id: generateId(),
    title: 'Error de conexión',
    message: 'Hubo un error en la conexión WebSocket',
    type: NotificationType.SYSTEM,
    createdAt: new Date().toISOString(),
    isRead: false
  })
}

/**
 * Conecta al servidor WebSocket para `userId`.
 *
 * Cambia el access token actual por un ticket de un solo uso (15s de vida)
 * y lo manda como ?ticket=... — nunca el JWT en claro.
 */
async function connect(userId: string): Promise<void> {
  if (socket.value && isConnected.value) {
    console.warn('Ya hay una conexión WebSocket activa')
    return
  }

  currentUserId = userId

  try {
    const ticket = await api.auth.getWsTicket()

    // Mismo origen que la página, no una URL de backend aparte: /api ya se
    // llama por ruta relativa (ver services/api.ts) porque nginx en
    // producción enruta /api al backend dentro del MISMO dominio — no hay
    // subdominio de API separado. VITE_BACKEND_URL nunca se pasaba como
    // build-arg del Docker de producción, así que esto siempre caía al
    // default "localhost:8000" ahí — jamás conectaba fuera de un dev local
    // sin Docker. En dev con Docker, el proxy de Vite ya reenvía /api
    // (incluido el upgrade de WebSocket, ver vite.config.ts) desde el mismo
    // origen, así que esto funciona igual en ambos casos.
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/ws/${userId}?ticket=${encodeURIComponent(ticket)}`

    socket.value = new WebSocket(wsUrl)

    socket.value.addEventListener('open', () => {
      isConnected.value = true
      reconnectAttempts.value = 0
      startHeartbeat()
    })

    socket.value.addEventListener('message', handleMessage)
    socket.value.addEventListener('close', handleClose)
    socket.value.addEventListener('error', handleError)
  } catch (error) {
    console.error('Error al conectar WebSocket:', error)
    isConnected.value = false
  }
}

/**
 * Desconecta del servidor WebSocket. code=1000 le indica a handleClose que
 * es un cierre intencional y no debe disparar reconexión.
 */
function disconnect(): void {
  try {
    currentUserId = null
    if (reconnectTimeoutId) {
      clearTimeout(reconnectTimeoutId)
      reconnectTimeoutId = null
    }
    stopHeartbeat()

    if (socket.value) {
      socket.value.close(1000, 'Desconexión voluntaria del cliente')
      socket.value = null
    }

    isConnected.value = false
    reconnectAttempts.value = 0
  } catch (error) {
    console.error('Error al desconectar WebSocket:', error)
  }
}

function send(data: any): void {
  if (!socket.value || !isConnected.value) {
    console.error('No hay conexión WebSocket activa')
    return
  }

  try {
    const message = JSON.stringify({
      ...data,
      timestamp: data.timestamp || new Date().toISOString()
    })
    socket.value.send(message)
  } catch (error) {
    console.error('Error enviando mensaje WebSocket:', error)
  }
}

/**
 * Composable para gestionar la conexión WebSocket (singleton a nivel de
 * módulo, ver nota de diseño arriba).
 */
export function useWebSocket() {
  return {
    isConnected,
    reconnectAttempts,
    connect,
    disconnect,
    send
  }
}
