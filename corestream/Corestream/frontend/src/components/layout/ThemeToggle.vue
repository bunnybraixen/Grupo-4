<template>
  <button
    type="button"
    class="w-full flex items-center gap-3 rounded-lg px-4 py-2 text-left text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-cold-2)]"
    :aria-label="actionLabel"
    :aria-pressed="isDark"
    :title="actionLabel"
    @click="themeStore.toggleTheme"
  >
    <svg v-if="isDark" class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke-width="2" />
      <path stroke-linecap="round" stroke-width="2" d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" />
    </svg>
    <svg v-else class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6.5 6.5 0 0 0 8.268 8.268c.344-.215.825-.003.803.401Z" />
    </svg>
    <span>{{ isDark ? 'Modo claro' : 'Modo oscuro' }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const isDark = computed(() => themeStore.theme === 'dark')
const actionLabel = computed(() => `Cambiar a modo ${isDark.value ? 'claro' : 'oscuro'}`)
</script>