/**
 * Store de Notificaciones - CoreStream
 * Gestiona el sistema de notificaciones en tiempo real
 * 
 * Responsabilidades:
 * - Mantener lista de notificaciones
 * - Marcar notificaciones como leídas
 * - Obtener notificaciones desde el servidor
 * - Recibir nuevas notificaciones desde WebSocket
 * - Contar notificaciones sin leer
 */
 
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification } from '@/types'
import { NotificationType } from '@/types'
import { api } from '@/services/api'

const toNotification = (raw: any): Notification => ({
  id: raw.id,
  userId: raw.userId ?? raw.user_id ?? '',
  title: raw.title ?? '',
  message: raw.message ?? '',
  type: (raw.type ?? raw.notification_type ?? 'SYSTEM') as NotificationType,
  isRead: raw.isRead ?? raw.is_read ?? false,
  ticketId: raw.ticketId ?? raw.ticket_id ?? undefined,
  createdAt: raw.createdAt ?? raw.created_at ?? '',
  readAt: raw.readAt ?? raw.read_at ?? undefined,
})

export const useNotificationsStore = defineStore('notifications', () => {
  // ========== ESTADO REACTIVO ==========

  /**
   * Lista completa de notificaciones del usuario
   * Ordenadas por fecha descendente (más recientes primero)
   */
  const notifications = ref<Notification[]>([])

  /**
   * Contador de notificaciones sin leer
   * Se actualiza automáticamente cuando cambia el estado de lectura
   */
  const unreadCount = ref<number>(0)

  /**
   * Flag de carga durante operaciones async
   */
  const isLoading = ref(false)

  /**
   * Mensaje de error de la última operación
   */
  const error = ref<string | null>(null)

  /**
   * Página actual para paginación
   * Se usa cuando se cargan notificaciones con limit/offset
   */
  const currentPage = ref<number>(1)

  /**
   * Total de notificaciones disponibles en el servidor
   * Se usa para calcular si hay más páginas
   */
  const totalNotifications = ref<number>(0)

  /**
   * Número de notificaciones por página
   */
  const pageSize = ref<number>(20)

  // ========== GETTERS COMPUTADOS ==========

  /**
   * Retorna las notificaciones que aún no han sido leídas
   */
  const unreadNotifications = computed((): Notification[] => {
    return notifications.value.filter(n => !n.isRead)
  })

  /**
   * Retorna las 10 notificaciones más recientes
   * Útil para mostrar un resumen en el header
   */
  const recentNotifications = computed((): Notification[] => {
    return notifications.value.slice(0, 10)
  })

  /**
   * Retorna las notificaciones ordenadas por fecha (más recientes primero)
   */
  const sortedByDate = computed((): Notification[] => {
    return [...notifications.value].sort((a, b) => {
      const dateA = new Date(a.createdAt).getTime()
      const dateB = new Date(b.createdAt).getTime()
      return dateB - dateA
    })
  })

  /**
   * Retorna si hay más notificaciones para cargar
   */
  const hasMore = computed((): boolean => {
    return notifications.value.length < totalNotifications.value
  })

  /**
   * Agrupa notificaciones por fecha (hoy, ayer, esta semana, más antiguas)
   */
  const groupedByDate = computed((): Record<string, Notification[]> => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const weekAgo = new Date(today)
    weekAgo.setDate(weekAgo.getDate() - 7)

    const groups: Record<string, Notification[]> = {
      'Hoy': [],
      'Ayer': [],
      'Esta semana': [],
      'Más antiguas': [],
    }

    notifications.value.forEach(notif => {
      const date = new Date(notif.createdAt)
      const notifDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())

      if (notifDate.getTime() === today.getTime()) {
        groups['Hoy'].push(notif)
      } else if (notifDate.getTime() === yesterday.getTime()) {
        groups['Ayer'].push(notif)
      } else if (notifDate.getTime() > weekAgo.getTime()) {
        groups['Esta semana'].push(notif)
      } else {
        groups['Más antiguas'].push(notif)
      }
    })

    return groups
  })

  /**
   * Retorna notificaciones filtradas por tipo
   */
  const getNotificationsByType = (type: string): Notification[] => {
    return notifications.value.filter(n => n.type === type)
  }

  // ========== ACCIONES ==========

  /**
   * Obtiene notificaciones del servidor
   * Soporta paginación con limit y offset
   * 
   * @param page - Número de página (defecto 1)
   * @param limit - Cantidad de notificaciones por página (defecto 20)
   * @returns Promise<Notification[]>
   */
  const fetch = async (page: number = 1, limit: number = 20): Promise<Notification[]> => {
    isLoading.value = true
    error.value = null
    currentPage.value = page
    pageSize.value = limit

    try {
      const skip = (page - 1) * limit
      const response = await api.notifications.list({ skip, limit } as any)
      const rawItems: any[] = Array.isArray(response)
        ? response
        : ((response as any)?.data?.items ?? (response as any)?.items ?? (response as any)?.data ?? [])
      const items: Notification[] = rawItems.map(toNotification)
      const total: number = Array.isArray(response)
        ? response.length
        : ((response as any)?.data?.total ?? (response as any)?.total ?? rawItems.length)

      if (page === 1) {
        notifications.value = items
      } else {
        notifications.value.push(...items)
      }

      totalNotifications.value = total

      await fetchUnreadCount()

      return items
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al obtener notificaciones'
      error.value = message
      console.error('Error en fetch:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene el contador de notificaciones sin leer
   * Se ejecuta automáticamente después de marcar como leídas
   * 
   * @returns Promise<number>
   */
  const fetchUnreadCount = async (): Promise<number> => {
    try {
      const res = await api.notifications.getUnreadCount()
      const count: number = (res as any)?.data?.unread_count ?? (res as any)?.unread_count ?? (res as any)?.data?.count ?? (res as any)?.count ?? 0
      unreadCount.value = count
      return count
    } catch (err) {
      console.error('Error al obtener contador de no leídas:', err)
      throw err
    }
  }

  /**
   * Marca una o más notificaciones como leídas
   * 
   * @param ids - IDs de notificaciones a marcar como leídas
   * @returns Promise<void>
   */
  const markAsRead = async (ids: string[]): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await Promise.all(ids.map(id => api.notifications.markRead(id)))

      // Actualizar estado local
      notifications.value = notifications.value.map(notif => {
        if (ids.includes(notif.id)) {
          return { ...notif, isRead: true }
        }
        return notif
      })

      // Recalcular contador
      unreadCount.value = unreadNotifications.value.length
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al marcar como leídas'
      error.value = message
      console.error('Error en markAsRead:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Marca todas las notificaciones como leídas
   * 
   * @returns Promise<void>
   */
  const markAllAsRead = async (): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.notifications.markAllRead()

      // Actualizar todas las notificaciones locales
      notifications.value = notifications.value.map(notif => ({
        ...notif,
        isRead: true,
      }))

      unreadCount.value = 0
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al marcar todas como leídas'
      error.value = message
      console.error('Error en markAllAsRead:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Agrega una notificación a la lista
   * Se llama desde un composable de WebSocket cuando llega una notificación en tiempo real
   * 
   * La notificación se inserta al inicio de la lista (más reciente)
   * 
   * @param notification - Notificación a agregar
   */
  const addNotification = (notification: Notification): void => {
    notifications.value.unshift(notification)
    
    // Si la notificación no es leída, incrementar contador
    if (!notification.isRead) {
      unreadCount.value++
    }
  }

  /**
   * Elimina una notificación de la lista
   * 
   * @param id - ID de la notificación a eliminar
   * @returns Promise<void>
   */
  const deleteNotification = async (id: string): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.notifications.delete(id)
      
      notifications.value = notifications.value.filter(n => n.id !== id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar notificación'
      error.value = message
      console.error('Error en deleteNotification:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Elimina todas las notificaciones leídas
   * Útil para limpiar la bandeja
   * 
   * @returns Promise<void>
   */
  const deleteAllRead = async (): Promise<void> => {
    isLoading.value = true
    error.value = null

    try {
      await api.notifications.deleteAllRead()
      
      notifications.value = notifications.value.filter(n => !n.isRead)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al eliminar notificaciones leídas'
      error.value = message
      console.error('Error en deleteAllRead:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtiene una notificación específica por su ID
   * 
   * @param id - ID de la notificación
   * @returns Notification | undefined
   */
  const getNotificationById = (id: string): Notification | undefined => {
    return notifications.value.find(n => n.id === id)
  }

  /**
   * Carga la siguiente página de notificaciones
   * Se usa cuando el usuario hace scroll en la lista
   * 
   * @returns Promise<Notification[]>
   */
  const loadMore = async (): Promise<Notification[]> => {
    if (!hasMore.value) {
      return []
    }
    return fetch(currentPage.value + 1, pageSize.value)
  }

  /**
   * Limpia el estado del store (para logout)
   */
  const clear = (): void => {
    notifications.value = []
    unreadCount.value = 0
    currentPage.value = 1
    totalNotifications.value = 0
    error.value = null
  }

  return {
    // Estado
    notifications,
    unreadCount,
    isLoading,
    error,
    currentPage,
    totalNotifications,
    pageSize,
    // Getters
    unreadNotifications,
    recentNotifications,
    sortedByDate,
    hasMore,
    groupedByDate,
    getNotificationsByType,
    // Acciones
    fetch,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    addNotification,
    deleteNotification,
    deleteAllRead,
    getNotificationById,
    loadMore,
    clear,
  }
})
