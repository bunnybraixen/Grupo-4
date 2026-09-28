```vue
<template>
  <div class="fixed top-4 right-4 z-50">
    <!-- Botón de notificaciones -->
    <button
      type="button"
      class="relative flex items-center justify-center w-11 h-11 rounded-full bg-gray-800 border border-gray-700 text-white hover:bg-gray-700 transition-colors shadow-lg"
      title="Notificaciones"
      @click="toggleNotifications"
    >
      <span class="text-xl">🔔</span>

      <!-- Contador de no leídas -->
      <span
        v-if="unreadCount > 0"
        class="absolute -top-1 -right-1 min-w-[20px] h-[20px] px-1 rounded-full bg-red-500 text-white text-xs font-bold flex items-center justify-center"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- Panel de notificaciones -->
    <div
      v-if="isOpen"
      class="absolute right-0 mt-3 w-96 max-h-[500px] overflow-hidden bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700"
    >
      <!-- Cabecera -->
      <div
        class="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700"
      >
        <div>
          <h3 class="font-semibold text-gray-900 dark:text-white">
            Notificaciones
          </h3>

          <p
            v-if="unreadCount > 0"
            class="text-xs text-gray-500 dark:text-gray-400 mt-1"
          >
            {{ unreadCount }} sin leer
          </p>
        </div>

        <button
          v-if="unreadCount > 0"
          type="button"
          class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
          @click="markAllAsRead"
        >
          Marcar todas como leídas
        </button>
      </div>

      <!-- Cargando -->
      <div
        v-if="loading"
        class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
      >
        Cargando notificaciones...
      </div>

      <!-- Sin notificaciones -->
      <div
        v-else-if="notifications.length === 0"
        class="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400"
      >
        No tienes notificaciones.
      </div>

      <!-- Lista -->
      <div
        v-else
        class="max-h-[420px] overflow-y-auto"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 transition-colors"
          :class="{
            'bg-blue-50 dark:bg-gray-700/50': !notification.isRead,
            'bg-white dark:bg-gray-800': notification.isRead
          }"
        >
          <div class="flex items-start gap-3">
            <span class="text-lg">
              🔔
            </span>

            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ notification.title }}
              </p>

              <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                {{ notification.message }}
              </p>

              <p class="mt-2 text-xs text-gray-400 dark:text-gray-500">
                {{ formatDate(notification.createdAt) }}
              </p>
            </div>

            <!-- Indicador de no leída -->
            <div class="flex flex-col items-end gap-2 shrink-0">
              <span
                v-if="!notification.isRead"
                class="w-2.5 h-2.5 rounded-full bg-red-500"
                title="No leída"
              />

              <button
                v-if="!notification.isRead"
                type="button"
                class="text-xs text-blue-600 dark:text-blue-400 hover:underline whitespace-nowrap"
                @click="markAsRead(notification.id)"
              >
                Marcar leída
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/services/api'
import type { Notification } from '@/types'

const notifications = ref<Notification[]>([])
const unreadCount = ref(0)
const isOpen = ref(false)
const loading = ref(false)

const loadNotifications = async (): Promise<void> => {
  loading.value = true

  try {
    notifications.value = await api.notifications.getNotifications()

    unreadCount.value =
      await api.notifications.getUnreadCount()
  } catch (error) {
    console.error(
      'Error cargando notificaciones:',
      error
    )
  } finally {
    loading.value = false
  }
}

const toggleNotifications = async (): Promise<void> => {
  isOpen.value = !isOpen.value

  if (isOpen.value) {
    await loadNotifications()
  }
}

const formatDate = (date: string): string => {
  return new Date(date).toLocaleString('es-CL', {
    dateStyle: 'short',
    timeStyle: 'short',
  })
}

onMounted(async () => {
  await loadNotifications()
})

const markAsRead = async (
  notificationId: string
): Promise<void> => {
  try {
    await api.notifications.markRead([
      notificationId
    ])

    const notification = notifications.value.find(
      (item) => item.id === notificationId
    )

    if (notification && !notification.isRead) {
      notification.isRead = true

      unreadCount.value = Math.max(
        0,
        unreadCount.value - 1
      )
    }
  } catch (error) {
    console.error(
      'Error marcando notificación como leída:',
      error
    )
  }
}

const markAllAsRead = async (): Promise<void> => {
  try {
    await api.notifications.markAllRead()

    notifications.value.forEach(
      (notification) => {
        notification.isRead = true
      }
    )

    unreadCount.value = 0
  } catch (error) {
    console.error(
      'Error marcando todas las notificaciones como leídas:',
      error
    )
  }
}

</script>
```
