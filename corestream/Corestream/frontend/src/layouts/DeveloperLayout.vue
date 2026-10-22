<!--
  Layout para sección de desarrollo

  Proporciona navegación sidebar y estructura común para todas las vistas de desarrollo.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950 transition-colors duration-200">
    <!-- Sidebar -->
    <aside class="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-colors duration-200">
      <nav class="flex-1 p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          {{ t('navigation.developer') }}
        </h2>
        
        <router-link
          to="/dev/workbench"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.workbench') }}
        </router-link>
        
        <router-link
          to="/dev/my-incidents"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.incidents') }}
        </router-link>

        <router-link
          to="/dev/uploads"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.uploads') }}
        </router-link>

        <!-- Soporte operacional: visible para Dev Leader y Dev -->
        <router-link
          to="/dev/support"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.support') }}
        </router-link>

        <!-- Solo visible para líderes de grupo -->
        <router-link
          v-if="isGroupLeader"
          to="/dev/team-assignment"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.teamAssignment') }}
        </router-link>
      </nav>
      <div class="p-6 pt-0 space-y-2">
        <LanguageToggle />
        <ThemeToggle />
        <button
          class="w-full rounded-lg px-4 py-2 text-left text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          @click="handleLogout"
        >
          {{ t('navigation.logout') }}
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
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import LanguageToggle from '@/components/layout/LanguageToggle.vue'

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()
const isGroupLeader = computed(() => {
  const role = authStore.user?.role || localStorage.getItem('userRole')
  return role === 'GROUP_LEADER'
})

async function handleLogout() {
  await authStore.logout()
  await router.push('/login')
}
</script>
