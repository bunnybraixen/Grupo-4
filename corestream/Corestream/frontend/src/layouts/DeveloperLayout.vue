<!--
  Layout para sección de desarrollo

  Proporciona navegación sidebar y estructura común para todas las vistas de desarrollo.
-->
<template>
  <div class="flex h-screen bg-[var(--bg-app)] overflow-hidden">
    <!-- Overlay para móvil -->
    <div v-if="isSidebarOpen" @click="toggleSidebar" class="fixed inset-0 bg-black/50 z-40 md:hidden"></div>

    <!-- Sidebar -->
    <aside 
      id="dev-sidebar"
      :class="[
      'bg-[var(--bg-sidebar)] border-r border-[var(--border-subtle)] z-50 fixed md:relative h-full transition-transform duration-300 w-64',
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
    ]"
    aria-label="Navegación principal de desarrollo"
    >
      <nav class="p-6 space-y-4">
        <h2 class="font-bold text-lg text-[var(--text-primary)] mb-6">
          {{ t('nav.development') }}
        </h2>

        <router-link
          to="/dev/workbench"
          class="block px-4 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]"
          active-class="bg-[var(--bg-panel)] text-[var(--teal)] font-bold shadow-sm"
        >
          {{ t('nav.workbench') }}
        </router-link>

        <router-link
          to="/dev/uploads"
          class="block px-4 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]"
          active-class="bg-[var(--bg-panel)] text-[var(--teal)] font-bold shadow-sm"
        >
          {{ t('nav.myUploads') }}
        </router-link>

        <!-- Solo visible para líderes de equipo -->
        <router-link
          v-if="authStore.isTeamLeader"
          to="/dev/team-assignment"
          class="block px-4 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]"
          active-class="bg-[var(--bg-panel)] text-[var(--teal)] font-bold shadow-sm"
        >
          {{ t('nav.teamAssignment') }}
        </router-link>

        <router-link
          to="/dev/support"
          class="block px-4 py-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-panel)]"
          active-class="bg-[var(--bg-panel)] text-[var(--teal)] font-bold shadow-sm"
        >
          {{ t('nav.support') }}
        </router-link>

      </nav>
    </aside>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * DeveloperLayout - Componente de estructura para vistas de desarrollo
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores'
import { eventBus } from '@/utils/eventBus'

const authStore = useAuthStore()
const { t } = useI18n()

const isSidebarOpen = ref(false)
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

// El botón hamburguesa vive en AppHeader (cada vista de desarrollo lo renderiza),
// así que el toggle del sidebar de este layout se coordina por eventBus.
onMounted(() => eventBus.on('toggle-sidebar', toggleSidebar))
onUnmounted(() => eventBus.off('toggle-sidebar', toggleSidebar))
</script>
