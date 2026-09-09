<script setup lang="ts">
import { ref, watch } from 'vue'
import { FileText, X } from 'lucide-vue-next'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'
import type { Meeting } from '@/types'

const props = defineProps<{
  show: boolean
  meeting: Meeting | null
}>()

const emit = defineEmits(['close', 'updated'])

const dialogStore = useDialogStore()
const isSubmitting = ref(false)
const summaryText = ref('')

watch(() => props.meeting, (newMeeting) => {
  if (newMeeting) {
    summaryText.value = newMeeting.summaryMarkdown || ''
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!props.meeting) return

  isSubmitting.value = true
  try {
    await api.meetings.updateSummary(props.meeting.id, summaryText.value.trim())
    emit('updated')
    handleClose()
    dialogStore.alert('Acta guardada exitosamente')
  } catch (error: any) {
    console.error('Error al guardar acta:', error)
    dialogStore.alert('Error al guardar el acta: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show && meeting" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-[var(--bg-panel)] rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-[var(--border-subtle)] flex items-center justify-between bg-slate-50/50 dark:bg-transparent">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <FileText class="text-teal-600" :size="20" />
          Acta / Resumen: {{ meeting.title }}
        </h3>
        <button 
          @click="handleClose"
          class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-[var(--bg-card)] rounded-xl transition-colors"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto space-y-4 flex-1">
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5 flex justify-between">
            <span>Contenido (Markdown)</span>
            <span class="text-xs text-slate-400 font-normal">Soporta formato Markdown</span>
          </label>
          <textarea 
            v-model="summaryText"
            rows="12"
            placeholder="Escribe el resumen, acuerdos y notas de la reunión..."
            class="w-full px-4 py-3 font-mono text-sm bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all resize-y"
          ></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-slate-100 dark:border-[var(--border-subtle)] flex items-center justify-end gap-3 bg-slate-50/50 dark:bg-transparent">
        <button 
          @click="handleClose"
          :disabled="isSubmitting"
          class="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[var(--bg-card)] rounded-xl transition-colors disabled:opacity-50"
        >
          Cerrar sin guardar
        </button>
        <button 
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="px-6 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-xl transition-all shadow-sm hover:shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ isSubmitting ? 'Guardando...' : 'Guardar Acta' }}
        </button>
      </div>
      
    </div>
  </div>
</template>
