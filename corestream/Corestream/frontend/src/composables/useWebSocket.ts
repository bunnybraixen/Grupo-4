/**
 * Composable useWebSocket.ts
 * 
 * Composable de WebSocket para notificaciones en tiempo real en CoreStream.
 * Conecta al servidor FastAPI a través de WebSocket y recibe eventos push.
 * Implementa reconexión automática con backoff exponencial para mayor confiabilidad.
 * 
 * Características:
 * - Conexión automática al servidor WebSocket
 * - Heartbeat cada 30 segundos para mantener la conexión viva
 * - Reconexión automática con backoff exponencial (máximo 10 intentos)
 * - Parseo de mensajes JSON y gestión de notificaciones
 * - Limpieza automática al desmontar el componente
 * 
 * Uso:
 * const { isConnected, connect, disconnect, send } = useWebSocket()
 * onMounted(() => connect('user-id-123'))
 */

import { ref, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import { useNotificationStore } from '@/stores/notifications'

/**
 * Interfaz para mensajes recibidos por WebSocket
 */
interface WebSocketMessage {
  type: 'notification' | 'update' | 'error' | 'ping' | 'pong'
  data?: any
  message?: string
  timestamp?: string
}

/**
 * Composable para gestionar conexión WebSocket
 * Proporciona métodos para conectar, enviar y recibir mensajes en tiempo real
 * 
 * @returns Objeto con propiedades y métodos para el WebSocket
 */
export function useWebSocket() {
  // =========================================================================
  // ESTADO REACTIVO - Variables para rastrear el estado de la conexión
  // =========================================================================

  /**
   * Instancia de conexión WebSocket
   * null si no está conectado, WebSocket si está activo
   */
  const socket: Ref<WebSocket | null> = ref(null)

  /**
   * Indica si la conexión WebSocket está activa
   * Se actualiza automáticamente cuando la conexión cambia de estado
   */
  const isConnected: Ref<boolean> = ref(false)

  /**
   * Número actual de intentos de reconexión
   * Se reinicia a 0 cuando la conexión es exitosa
   */
  const reconnectAttempts: Ref<number> = ref(0)

  /**
   * ID del intervalo de heartbeat
   * Se usa para cancelar el intervalo cuando se desconecta
   */
  let heartbeatIntervalId: NodeJS.Timeout | null = null

  // =========================================================================
  // CONSTANTES - Configuración de reconexión y timing
  // =========================================================================

  /**
   * Número máximo de intentos de reconexión
   * Después de alcanzar este número, la reconexión se detiene
   */
  const maxReconnectAttempts = 10

  /**
   * Retraso base en milisegundos para el backoff exponencial
   * Valor inicial: 1000ms (1 segundo)
   */
  const baseDelay = 1000

  /**
   * Retraso máximo en milisegundos para no esperar demasiado
   * Límite: 30 segundos (30000ms)
   */
  const maxDelay = 30000

  /**
   * Intervalo de heartbeat en milisegundos para mantener viva la conexión
   * Se envía un ping cada 30 segundos
   */
  const heartbeatInterval = 30000

  // =========================================================================
  // ACCESO A STORES - Pinia stores para gestionar notificaciones
  // =========================================================================

  /**
   * Store de notificaciones para guardar mensajes recibidos
   */
  const notificationStore = useNotificationStore()

  // =========================================================================
  // MÉTODOS PRIVADOS - Funciones internas para manejo de WebSocket
  // =========================================================================

  /**
   * Calcula el retraso para el siguiente intento de reconexión
   * Usa backoff exponencial: delay = baseDelay * 2^intentos
   * Capped al máximo para evitar esperas excesivas
   * 
   * @returns Retraso en milisegundos para el siguiente intento
   */
  function calculateBackoffDelay(): number {
    // Fórmula: baseDelay * 2^intentos, ejemplo: 1000 * 2^3 = 8000ms
    const exponentialDelay = baseDelay * Math.pow(2, reconnectAttempts.value)
    // Limitar al máximo de 30 segundos
    return Math.min(exponentialDelay, maxDelay)
  }

  /**
   * Inicia el intervalo de heartbeat
   * Envía un ping cada 30 segundos para mantener la conexión viva
   * Previene que el servidor cierre la conexión por inactividad
   */
  function startHeartbeat(): void {
    // Limpiar intervalo anterior si existe
    if (heartbeatIntervalId) {
      clearInterval(heartbeatIntervalId)
    }

    // Crear nuevo intervalo que envía ping periódicamente
    heartbeatIntervalId = setInterval(() => {
      if (isConnected.value && socket.value) {
        try {
          // Enviar mensaje de tipo 'ping' para heartbeat
          send({
            type: 'ping',
            timestamp: new Date().toISOString()
          })
        } catch (error) {
          console.warn('Error enviando heartbeat:', error)
        }
      }
    }, heartbeatInterval)
  }

  /**
   * Detiene el intervalo de heartbeat
   * Se llama al desconectar para liberar recursos
   */
  function stopHeartbeat(): void {
    if (heartbeatIntervalId) {
      clearInterval(heartbeatIntervalId)
      heartbeatIntervalId = null
    }
  }

  /**
   * Maneja los mensajes recibidos del servidor WebSocket
   * Valida el formato JSON y procesa según el tipo de mensaje
   * 
   * @param event - Evento de mensaje WebSocket
   */
  function handleMessage(event: MessageEvent): void {
    try {
      // Parsear el mensaje JSON recibido
      const message: WebSocketMessage = JSON.parse(event.data)

      // Procesar según el tipo de mensaje
      switch (message.type) {
        case 'notification':
          // Agregar notificación al store si es una notificación
          if (message.data) {
            notificationStore.addNotification({
              id: message.data.id || generateId(),
              title: message.data.title || 'Notificación',
              message: message.data.message || '',
              type: message.data.type || 'info',
              timestamp: message.timestamp || new Date().toISOString(),
              read: false
            })
          }
          break

        case 'update':
          // Procesar actualización de datos en tiempo real
          console.log('Actualización en tiempo real recibida:', message.data)
          // Aquí se pueden disparar eventos o acciones del store
          break

        case 'pong':
          // Respuesta a heartbeat - no hacer nada especial
          console.debug('Heartbeat pong recibido')
          break

        case 'error':
          // Mensaje de error del servidor
          console.error('Error del servidor WebSocket:', message.message)
          notificationStore.addNotification({
            id: generateId(),
            title: 'Error',
            message: message.message || 'Error del servidor',
            type: 'error',
            timestamp: message.timestamp || new Date().toISOString(),
            read: false
          })
          break

        default:
          console.warn('Tipo de mensaje desconocido:', message.type)
      }
    } catch (error) {
      console.error('Error procesando mensaje WebSocket:', error)
    }
  }

  /**
   * Maneja el evento de cierre de la conexión WebSocket
   * Intenta reconectar con backoff exponencial
   * 
   * @param event - Evento de cierre WebSocket
   */
  function handleClose(event: CloseEvent): void {
    console.log('Conexión WebSocket cerrada:', event.code, event.reason)
    isConnected.value = false
    socket.value = null

    // Detener heartbeat cuando se cierra la conexión
    stopHeartbeat()

    // Intentar reconectar si no hemos superado el máximo de intentos
    if (reconnectAttempts.value < maxReconnectAttempts) {
      const delay = calculateBackoffDelay()
      console.log(
        `Intentando reconectar en ${delay}ms (intento ${reconnectAttempts.value + 1}/${maxReconnectAttempts})`
      )

      // Incrementar contador de intentos
      reconnectAttempts.value++

      // Programar reconexión después del retraso calculado
      setTimeout(() => {
        // Obtener userId del almacenamiento local o del store de autenticación
        const userId = localStorage.getItem('userId') || ''
        if (userId) {
          connect(userId)
        }
      }, delay)
    } else {
      console.error(
        `No se pudo conectar después de ${maxReconnectAttempts} intentos`
      )
      notificationStore.addNotification({
        id: generateId(),
        title: 'Conexión perdida',
        message: 'No se pudo establecer la conexión con el servidor',
        type: 'error',
        timestamp: new Date().toISOString(),
        read: false
      })
    }
  }

  /**
   * Maneja los errores de conexión WebSocket
   * Registra el error y dispara un evento de reconexión
   * 
   * @param event - Evento de error WebSocket
   */
  function handleError(event: Event): void {
    console.error('Error de WebSocket:', event)
    notificationStore.addNotification({
      id: generateId(),
      title: 'Error de conexión',
      message: 'Hubo un error en la conexión WebSocket',
      type: 'error',
      timestamp: new Date().toISOString(),
      read: false
    })
  }

  /**
   * Genera un ID único para notificaciones
   * Usa timestamp + número aleatorio para garantizar unicidad
   * 
   * @returns ID único como string
   */
  function generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  // =========================================================================
  // MÉTODOS PÚBLICOS - API del composable
  // =========================================================================

  /**
   * Conecta al servidor WebSocket
   * Establece la conexión a ws://{host}/api/ws/notifications/{userId}
   * Configura los event listeners y reinicia el contador de intentos
   * 
   * @param userId - ID del usuario para la conexión personalizada
   */
  function connect(userId: string): void {
    try {
      // No intentar conectar si ya hay una conexión activa
      if (socket.value && isConnected.value) {
        console.warn('Ya hay una conexión WebSocket activa')
        return
      }

      // Construir URL del WebSocket usando el protocolo actual
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      const wsUrl = `${protocol}//${host}/api/ws/notifications/${userId}`

      console.log('Conectando a WebSocket:', wsUrl)

      // Crear nueva instancia de WebSocket
      socket.value = new WebSocket(wsUrl)

      // Configurar event listeners
      socket.value.addEventListener('open', () => {
        console.log('WebSocket conectado exitosamente')
        isConnected.value = true
        reconnectAttempts.value = 0 // Resetear contador de intentos
        startHeartbeat() // Iniciar heartbeat al conectar

        notificationStore.addNotification({
          id: generateId(),
          title: 'Conexión establecida',
          message: 'Conectado al servidor en tiempo real',
          type: 'success',
          timestamp: new Date().toISOString(),
          read: false
        })
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
   * Desconecta del servidor WebSocket
   * Cierra la conexión limpiamente y detiene el heartbeat
   */
  function disconnect(): void {
    try {
      // Detener heartbeat primero
      stopHeartbeat()

      // Cerrar conexión si existe
      if (socket.value) {
        socket.value.close(1000, 'Desconexión voluntaria del cliente')
        socket.value = null
      }

      isConnected.value = false
      reconnectAttempts.value = 0

      console.log('WebSocket desconectado')
    } catch (error) {
      console.error('Error al desconectar WebSocket:', error)
    }
  }

  /**
   * Envía un mensaje al servidor a través del WebSocket
   * El mensaje se serializa a JSON automáticamente
   * 
   * @param data - Objeto a enviar (se serializa a JSON)
   * @throws Error si la conexión no está activa
   */
  function send(data: any): void {
    if (!socket.value || !isConnected.value) {
      console.error('No hay conexión WebSocket activa')
      return
    }

    try {
      // Serializar data a JSON y enviar
      const message = JSON.stringify({
        ...data,
        timestamp: data.timestamp || new Date().toISOString()
      })
      socket.value.send(message)
    } catch (error) {
      console.error('Error enviando mensaje WebSocket:', error)
    }
  }

  // =========================================================================
  // LIMPIEZA - Hook de desmontaje del componente
  // =========================================================================

  /**
   * Hook de ciclo de vida: se ejecuta cuando el componente es desmontado
   * Garantiza la desconexión limpia y liberación de recursos
   */
  onUnmounted(() => {
    disconnect()
  })

  // =========================================================================
  // RETORNO DEL COMPOSABLE - API pública
  // =========================================================================

  return {
    // Propiedades reactivas
    isConnected,
    reconnectAttempts,

    // Métodos públicos
    connect,
    disconnect,
    send
  }
}
