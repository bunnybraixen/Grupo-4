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
      class="relative p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] rounded-lg transition-colors"
      :title="t('notifications.unreadLabel', { count: unreadCount })"
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
        class="absolute right-0 mt-2 w-80 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg shadow-2xl overflow-hidden z-40"
      >
        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Encabezado -->
        <!-- ================================================================ -->
        <div class="p-3 bg-[var(--bg-panel)] border-b border-[var(--border-subtle)] flex items-center justify-between">
          <h3 class="text-sm font-semibold text-[var(--text-primary)]">{{ t('notifications.title') }}</h3>

          <!-- Botón: Marcar todas como leídas -->
          <button
            v-if="unreadCount > 0"
            @click="markAllAsRead"
            class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            {{ t('notifications.markAllRead2') }}
          </button>
        </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Lista de Notificaciones -->
        <!-- ================================================================ -->
        <div class="max-h-96 overflow-y-auto">
          <!-- Estado vacío -->
          <div
            v-if="notifications.length === 0"
            class="p-8 text-center text-[var(--text-secondary)]"
          >
            <Icon icon="mdi:bell-off-outline" class="text-3xl mx-auto mb-2 opacity-50" />
            <p class="text-sm">{{ t('notifications.noNotifications') }}</p>
          </div>

          <!-- Lista de notificaciones -->
          <div v-else>
            <button
              v-for="notification in notifications"
              :key="notification.id"
              @click="handleNotificationClick(notification)"
              :class="[
                'w-full p-3 border-b border-[var(--border-subtle)] hover:bg-[var(--bg-panel)] transition-colors text-left',
                !notification.isRead ? 'bg-[var(--bg-panel)]' : 'bg-[var(--bg-card)]'
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
                    <p class="text-sm font-semibold text-[var(--text-primary)]">
                      {{ notification.title }}
                    </p>

                    <!-- Indicador no leído -->
                    <span
                      v-if="!notification.isRead"
                      class="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-1"
                    />
                  </div>

                  <!-- Mensaje preview -->
                  <p class="text-xs text-[var(--text-secondary)] line-clamp-2">
                    {{ formatNotificationMessage(notification.message) }}
                  </p>

                  <!-- Tiempo relativo -->
                  <p class="text-xs text-[var(--text-muted)] mt-1">
                    {{ formatTime(notification.createdAt) }}
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useNotificationsStore } from '@/stores/notifications'
import { useAuthStore } from '@/stores/auth'
import type { Notification } from '@/types'
import { NotificationType } from '@/types'

const isDropdownOpen = ref(false)
const router = useRouter()
const { t } = useI18n()
const notificationsStore = useNotificationsStore()
const authStore = useAuthStore()

const notifications = computed(() =>
  [...notificationsStore.notifications].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )
)

const unreadCount = computed(() => notificationsStore.unreadCount)

const getNotificationIcon = (type: string): string => {
  const icons: Record<string, string> = {
    [NotificationType.TICKET_ASSIGNED]:   'mdi:account-check',
    [NotificationType.STATUS_CHANGED]:    'mdi:swap-horizontal',
    [NotificationType.TICKET_REDIRECTED]: 'mdi:arrow-right-circle',
    [NotificationType.TICKET_COMPLETED]:  'mdi:check-circle',
    [NotificationType.QUESTION_RAISED]:   'mdi:help-circle',
    [NotificationType.SYSTEM]:            'mdi:bell',
  }
  return icons[type] ?? 'mdi:bell'
}

const getNotificationIconColor = (type: string): string => {
  const colors: Record<string, string> = {
    [NotificationType.TICKET_ASSIGNED]:   'bg-blue-900 text-blue-400',
    [NotificationType.STATUS_CHANGED]:    'bg-slate-700 text-slate-300',
    [NotificationType.TICKET_REDIRECTED]: 'bg-indigo-900 text-indigo-400',
    [NotificationType.TICKET_COMPLETED]:  'bg-green-900 text-green-400',
    [NotificationType.QUESTION_RAISED]:   'bg-amber-900 text-amber-400',
    [NotificationType.SYSTEM]:            'bg-slate-700 text-slate-400',
  }
  return colors[type] ?? 'bg-slate-700 text-slate-300'
}

const formatTime = (isoString: string): string => {
  const date = new Date(isoString)
  const diffMs = Date.now() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return t('notifications.justNow')
  if (diffMins < 60) return t('notifications.minutesAgo', { n: diffMins })
  if (diffHours < 24) return t('notifications.hoursAgo', { n: diffHours })
  if (diffDays < 7) return t('notifications.daysAgo', { n: diffDays })

  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${day}/${month}`
}

const handleNotificationClick = (notification: Notification) => {
  notificationsStore.markAsRead([notification.id])
  isDropdownOpen.value = false
  if (notification.ticketId) {
    const role = authStore.user?.role
    const routeName = role === 'ADMIN' ? 'Builder' : 'Workbench'
    router.push({ name: routeName, query: { ticketId: notification.ticketId } })
  }
}

const markAllAsRead = () => {
  notificationsStore.markAllAsRead()
}

function formatNotificationMessage(msg: string): string {
  const replacements: Record<string, string> = {
    'IN_PROGRESS': t('statuses.inProgress'),
    'TODO': t('statuses.todo'),
    'BLOCKED': t('statuses.blocked'),
    'DONE': t('statuses.done'),
  }
  return Object.entries(replacements).reduce(
    (s, [code, label]) => s.split(code).join(label),
    msg
  )
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') isDropdownOpen.value = false
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  notificationsStore.fetch().catch(() => {})
})
onUnmounted(() => { document.removeEventListener('keydown', handleKeydown) })
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

