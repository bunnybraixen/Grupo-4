<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Campana de Notificaciones -->
  <!-- ================================================================ -->
  <!-- Ícono de campana en header con badge de conteo no leído -->
  <!-- Click abre dropdown con lista de notificaciones -->
  <!-- Cada notificación clickeable navega al ticket relacionado -->
  <!-- ================================================================ -->

  <div class="relative">
    <!-- ================================================================ -->
    <!-- ELEMENTO: Botón de Campana -->
    <!-- ================================================================ -->
    <!-- Muestra ícono y badge con cantidad no leída -->
    <!-- ================================================================ -->
    <button
      @click="isDropdownOpen = !isDropdownOpen"
      class="relative p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
      :title="`${unreadCount} notificaciones no leídas`"
    >
      <!-- Ícono de campana -->
      <Icon icon="mdi:bell-outline" class="text-xl" />

      <!-- Badge de conteo no leído -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 w-5 h-5 bg-red-600 text-white text-xs font-bold rounded-full flex items-center justify-center"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- ================================================================ -->
    <!-- ELEMENTO: Panel Dropdown de Notificaciones -->
    <!-- ================================================================ -->
    <!-- Lista de notificaciones con scroll -->
    <!-- ================================================================ -->
    <Transition name="fade-slide">
      <div
        v-if="isDropdownOpen"
        class="absolute right-0 mt-2 w-80 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl overflow-hidden z-40"
      >
        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Encabezado -->
        <!-- ================================================================ -->
        <div class="p-3 bg-slate-750 border-b border-slate-700 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-white">Notificaciones</h3>

          <!-- Botón: Marcar todas como leídas -->
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            Marcar todas como leídas
          </button>
        </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Lista de Notificaciones -->
        <!-- ================================================================ -->
        <div class="max-h-96 overflow-y-auto">
          <!-- Estado vacío -->
          <div
            v-if="notifications.length === 0"
            class="p-8 text-center text-slate-400"
          >
            <Icon icon="mdi:bell-off-outline" class="text-3xl mx-auto mb-2 opacity-50" />
            <p class="text-sm">Sin notificaciones</p>
          </div>

          <!-- Lista de notificaciones -->
          <div v-else>
            <button
              v-for="notification in notifications"
              :key="notification.id"
              @click="handleNotificationClick(notification)"
              :class="[
                'w-full p-3 border-b border-slate-700 hover:bg-slate-700 transition-colors text-left',
                !notification.isRead ? 'bg-slate-750' : 'bg-slate-800'
              ]"
            >
              <!-- Contenedor flex principal -->
              <div class="flex items-start gap-2">
                <!-- Ícono de notificación -->
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                    getNotificationIconColor(notification.type)
                  ]"
                >
                  <Icon :icon="getNotificationIcon(notification.type)" class="text-sm" />
                </div>

                <!-- Contenido de notificación -->
                <div class="flex-1 min-w-0">
                  <!-- Título y tiempo -->
                  <div class="flex items-start justify-between gap-1 mb-1">
                    <p class="text-sm font-semibold text-white">
                      {{ notification.title }}
                    </p>

                    <!-- Indicador no leído -->
                    <span
                      v-if="!notification.isRead"
                      class="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-1"
                    />
                  </div>

                  <!-- Mensaje preview -->
                  <p class="text-xs text-slate-400 line-clamp-2">
                    {{ notification.message }}
                  </p>

                  <!-- Tiempo relativo -->
                  <p class="text-xs text-slate-500 mt-1">
                    {{ formatTime(notification.timestamp) }}
                  </p>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Overlay para cerrar dropdown al hacer click fuera -->
    <div
      v-if="isDropdownOpen"
      @click="isDropdownOpen = false"
      class="fixed inset-0 z-30"
    />
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Notification {
  id: string
  type: 'QUESTION' | 'REDIRECTED' | 'ASSIGNED' | 'STATUS_CHANGE' | 'COMMENT'
  title: string
  message: string
  timestamp: string
  isRead: boolean
  ticketId?: string
}

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Control de apertura del dropdown
const isDropdownOpen = ref(false)

// =====================================================================
// ROUTER Y STORE
// =====================================================================

// Acceso al router para navegación
const router = useRouter()

// Acceso al store de notificaciones
const notificationsStore = useNotificationsStore()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Lista de notificaciones del usuario
 * Ordenadas por timestamp descendente (más recientes primero)
 */
const notifications = computed(() => {
  return notificationsStore.notifications.sort((a, b) =>
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  )
})

/**
 * Conteo de notificaciones no leídas
 */
const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.isRead).length
})

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Retorna el ícono de Iconify según el tipo de notificación
 * @param type - Tipo de notificación
 * @returns Código del ícono de Iconify
 */
const getNotificationIcon = (type: string): string => {
  const icons: Record<string, string> = {
    QUESTION: 'mdi:help-circle',
    REDIRECTED: 'mdi:arrow-right-circle',
    ASSIGNED: 'mdi:account-check',
    STATUS_CHANGE: 'mdi:swap-horizontal',
    COMMENT: 'mdi:chat-outline'
  }
  return icons[type] || 'mdi:bell'
}

/**
 * Retorna clase de color para el ícono según tipo
 * @param type - Tipo de notificación
 * @returns String de clases Tailwind
 */
const getNotificationIconColor = (type: string): string => {
  const colors: Record<string, string> = {
    QUESTION: 'bg-amber-900 text-amber-400',
    REDIRECTED: 'bg-indigo-900 text-indigo-400',
    ASSIGNED: 'bg-blue-900 text-blue-400',
    STATUS_CHANGE: 'bg-slate-700 text-slate-300',
    COMMENT: 'bg-slate-700 text-slate-300'
  }
  return colors[type] || 'bg-slate-700 text-slate-300'
}

/**
 * Formatea timestamp a formato legible
 * @param timestamp - Fecha ISO string
 * @returns Tiempo relativo formateado
 */
const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'justo ahora'
  if (diffMins < 60) return `hace ${diffMins}m`
  if (diffHours < 24) return `hace ${diffHours}h`
  if (diffDays < 7) return `hace ${diffDays}d`

  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}`
}

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Maneja click en una notificación
 * Marca como leída y navega al ticket si existe
 * @param notification - Notificación clickeada
 */
const handleNotificationClick = (notification: Notification) => {
  // Marcar como leída
  notificationsStore.markAsRead(notification.id)

  // Cerrar dropdown
  isDropdownOpen.value = false

  // Navegar al ticket si existe
  if (notification.ticketId) {
    router.push({
      name: 'workbench',
      params: { ticketId: notification.ticketId }
    })
  }
}

/**
 * Marca todas las notificaciones como leídas
 */
const markAllAsRead = () => {
  notificationsStore.markAllAsRead()
}
</script>

<style scoped>
/* ================================================================ */
/* TRANSICIONES */
/* ================================================================ */

/* Transición para dropdown */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-4px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
