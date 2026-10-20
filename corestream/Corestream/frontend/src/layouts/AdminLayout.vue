<!--
  Layout para sección de administración

  Proporciona navegación sidebar y estructura común para todas las vistas admin.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950">
    <!-- Sidebar -->
    <aside class="w-64 flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      <nav class="p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          Administración
        </h2>
        
        <router-link
          to="/admin/builder"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Constructor
        </router-link>
        
        <router-link
          to="/admin/analytics"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Analítica
        </router-link>

        <router-link
          to="/admin/reports"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Reportes
        </router-link>
        
        <!-- Secciones solo para ADMIN (el router rechaza al líder de grupo) -->
        <router-link
          v-if="authStore.isAdmin"
          to="/admin/code-docs"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Documentación
        </router-link>
        
        <router-link
          v-if="authStore.isAdmin"
          to="/admin/team"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Equipo
        </router-link>

        <router-link
          v-if="authStore.isAdmin"
          to="/admin/support"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Soporte
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
/**
 * AdminLayout - Componente de estructura para vistas de administración
 */
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
</script>
