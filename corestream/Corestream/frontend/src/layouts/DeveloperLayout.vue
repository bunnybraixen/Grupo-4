<!--
  Layout para sección de desarrollo

  Proporciona navegación sidebar y estructura común para todas las vistas de desarrollo.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950">
    <!-- Sidebar -->
    <aside class="w-64 flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      <nav class="p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          Desarrollo
        </h2>
        
        <router-link
          to="/dev/workbench"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Workbench
        </router-link>
        
        <router-link
          to="/dev/my-incidents"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Incidentes
        </router-link>

        <router-link
          to="/dev/uploads"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Mis Cargas
        </router-link>

        <!-- Soporte operacional: visible para Dev Leader y Dev -->
        <router-link
          to="/dev/support"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Soporte
        </router-link>

        <!-- Solo visible para líderes de grupo -->
        <router-link
          v-if="isGroupLeader"
          to="/dev/team-assignment"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Asignación de Equipo
        </router-link>
      </nav>
    <!-- Cerrar sesión -->
    <div class="mt-auto p-6 border-t border-gray-200 dark:border-gray-800">
      <button
        type="button"
        class="w-full text-left px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        @click="handleLogout"
      >
        Cerrar sesión
      </button>
    </div>
    </aside>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useRealtimeNotifications } from '@/composables/useRealtimeNotifications'

const authStore = useAuthStore()
const router = useRouter()

// Conexión WebSocket de notificaciones mientras el usuario está dentro de la app
useRealtimeNotifications()

const handleLogout = async () => {
  await authStore.logout()
  await router.push({ name: 'Login' })
}
const isGroupLeader = computed(() => {
  const role = authStore.user?.role || localStorage.getItem('userRole')
  return role === 'GROUP_LEADER'
})
</script>
