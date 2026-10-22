<template>
  <button
    type="button"
    class="w-full flex items-center justify-between rounded-lg px-4 py-2 text-left text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200 focus-visible:outline-none"
    :title="nextLocaleLabel"
    @click="toggleLanguage"
  >
    <div class="flex items-center gap-3">
      <span class="text-base" aria-hidden="true">{{ currentLocale === 'es' ? '🇪🇸' : '🇬🇧' }}</span>
      <span class="text-sm font-medium">{{ currentLocale === 'es' ? 'Español' : 'English' }}</span>
    </div>
    <span class="text-xs text-gray-400 dark:text-gray-500 uppercase font-mono">{{ currentLocale }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLocale, type SupportedLocale } from '@/i18n'

const { locale } = useI18n()

const currentLocale = computed(() => locale.value)
const nextLocaleLabel = computed(() =>
  currentLocale.value === 'es' ? 'Switch to English' : 'Cambiar a Español'
)

function toggleLanguage() {
  const next: SupportedLocale = currentLocale.value === 'es' ? 'en' : 'es'
  locale.value = next
  setLocale(next)
}
</script>

