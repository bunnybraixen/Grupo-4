<!--
  Layout para sección de administración

  Proporciona navegación sidebar y estructura común para todas las vistas admin.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950 transition-colors duration-200">
    <!-- Sidebar -->
    <aside class="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-colors duration-200">
      <nav class="flex-1 p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          {{ t('navigation.admin') }}
        </h2>
        
        <router-link
          to="/admin/builder"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.builder') }}
        </router-link>
        
        <router-link
          to="/admin/analytics"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.analytics') }}
        </router-link>

        <router-link
          to="/admin/reports"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.reports') }}
        </router-link>
        
        <router-link
          to="/admin/code-docs"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.documentation') }}
        </router-link>
        
        <router-link
          to="/admin/team"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.team') }}
        </router-link>

        <router-link
          to="/admin/support"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {{ t('navigation.support') }}
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
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import LanguageToggle from '@/components/layout/LanguageToggle.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  await router.push('/login')
}
</script>
