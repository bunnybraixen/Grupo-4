<!--
  Layout para sección de administración

  Proporciona navegación sidebar y estructura común para todas las vistas admin.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950 transition-colors duration-200">

    <!-- Overlay móvil -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-30 bg-black/50 md:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-40 w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col transition-transform duration-200',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'md:relative md:translate-x-0 md:flex'
      ]"
    >
      <!-- Botón cerrar en móvil -->
      <button
        class="absolute top-4 right-4 p-1 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 md:hidden"
        @click="sidebarOpen = false"
        aria-label="Cerrar menú"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>

      <nav class="flex-1 p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          {{ t('navigation.admin') }}
        </h2>

        <router-link
          to="/admin/builder"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
        >
          {{ t('navigation.builder') }}
        </router-link>

        <router-link
          to="/admin/analytics"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
        >
          {{ t('navigation.analytics') }}
        </router-link>

        <router-link
          to="/admin/reports"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
        >
          {{ t('navigation.reports') }}
        </router-link>

        <router-link
          to="/admin/code-docs"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
        >
          {{ t('navigation.documentation') }}
        </router-link>

        <router-link
          to="/admin/team"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
        >
          {{ t('navigation.team') }}
        </router-link>

        <router-link
          to="/admin/support"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = false"
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
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Topbar móvil -->
      <header class="md:hidden flex items-center gap-3 px-4 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shrink-0">
        <button
          class="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          @click="sidebarOpen = true"
          aria-label="Abrir menú"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <span class="font-semibold text-gray-900 dark:text-white text-sm">{{ t('navigation.admin') }}</span>
      </header>

      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import LanguageToggle from '@/components/layout/LanguageToggle.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const sidebarOpen = ref(false)

async function handleLogout() {
  await authStore.logout()
  await router.push('/login')
}
</script>
