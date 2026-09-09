<template>
  <div class="relative">
    <!-- Botón principal -->
    <button
      @click="toggleDropdown"
      :disabled="isExporting"
      class="flex items-center gap-2 bg-[#06B7B2] text-white font-semibold
             rounded-xl px-4 py-2 hover:bg-[#1FBEBA] transition-colors
             disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span v-if="isExporting" class="animate-spin">⟳</span>
      <span v-else>↓</span>
      <span>{{ isExporting ? 'Generando...' : 'Exportar' }}</span>
    </button>

    <!-- Dropdown -->
    <Transition name="fade">
      <div
        v-if="showDropdown"
        class="absolute right-0 top-full mt-1 w-52 bg-[var(--bg-card)]
               border border-[var(--border-subtle)] rounded-xl shadow-2xl z-50"
      >
        <button
          @click="handleExport('pdf')"
          class="w-full text-left px-4 py-3 text-sm text-[var(--text-primary)]
                 hover:bg-[var(--bg-panel)] rounded-t-xl transition-colors"
        >
          📄 Exportar como PDF
        </button>
        <button
          @click="handleExport('csv')"
          class="w-full text-left px-4 py-3 text-sm text-[var(--text-primary)]
                 hover:bg-[var(--bg-panel)] rounded-b-xl transition-colors
                 border-t border-[var(--border-subtle)]"
        >
          📊 Exportar como CSV
        </button>
      </div>
    </Transition>

    <!-- Toast -->
    <Transition name="slide-up">
      <div
        v-if="toast.show"
        class="fixed bottom-4 right-4 z-50 px-4 py-3 rounded-xl text-sm
               font-medium shadow-lg"
        :class="
          toast.type === 'success'
            ? 'bg-[#06B7B2] text-white'
            : 'bg-[#C1108B] text-white'
        "
      >
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { AnalyticsReport } from '@/types/analytics'
import { exportToPDF, exportToCSV } from '@/services/exportService'

const props = defineProps<{
  reportData: AnalyticsReport
  period: string
}>()

const showDropdown = ref(false)
const isExporting = ref(false)
const toast = ref({ show: false, type: 'success' as 'success' | 'error', message: '' })

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

async function handleExport(format: 'pdf' | 'csv') {
  showDropdown.value = false
  isExporting.value = true
  try {
    if (format === 'pdf') {
      await exportToPDF(props.reportData, props.period)
    } else {
      exportToCSV(props.reportData, props.period)
    }
    showToast('success', 'Archivo generado correctamente')
  } catch (e) {
    console.error('Error exportando:', e)
    showToast('error', 'Error al generar el archivo')
  } finally {
    isExporting.value = false
  }
}

function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// Cerrar dropdown al hacer click fuera
function handleClickOutside(e: MouseEvent) {
  const target = e.target as Element
  if (!target.closest('.relative')) {
    showDropdown.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
