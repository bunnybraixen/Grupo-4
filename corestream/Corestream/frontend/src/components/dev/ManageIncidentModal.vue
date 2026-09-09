<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Activity, X } from 'lucide-vue-next'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'
import type { Incident } from '@/types'

const props = defineProps<{
  show: boolean
  incident: Incident | null
}>()

const emit = defineEmits(['close', 'updated'])

const dialogStore = useDialogStore()
const isSubmitting = ref(false)

const form = reactive({
  status: 'REPORTED',
  mitigationState: '',
})

watch(() => props.incident, (newInc) => {
  if (newInc) {
    form.status = newInc.status
    form.mitigationState = newInc.mitigationState || ''
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!props.incident) return

  isSubmitting.value = true
  try {
    // 1. Update status
    await api.incidents.updateStatus(props.incident.id, form.status)
    
    // 2. Update mitigation text if changed
    if (form.mitigationState !== (props.incident.mitigationState || '')) {
      await api.incidents.update(props.incident.id, {
        mitigation_state: form.mitigationState
      })
    }
    
    emit('updated')
    handleClose()
    dialogStore.alert('Incidente actualizado exitosamente')
  } catch (error: any) {
    console.error('Error al actualizar incidente:', error)
    dialogStore.alert('Error al actualizar el incidente: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show && incident" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-[var(--bg-panel)] rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-[var(--border-subtle)] flex items-center justify-between bg-slate-50/50 dark:bg-transparent">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Activity class="text-amber-500" :size="20" />
          Gestionar Incidente
        </h3>
        <button 
          @click="handleClose"
          class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-[var(--bg-card)] rounded-xl transition-colors"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto space-y-4">
        <div class="mb-2">
          <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">{{ incident.title }}</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">ID: {{ incident.id }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Estado Actual
          </label>
          <select 
            v-model="form.status"
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all appearance-none"
          >
            <option value="REPORTED">REPORTED - Recién reportado</option>
            <option value="INVESTIGATING">INVESTIGATING - En análisis</option>
            <option value="MITIGATED">MITIGATED - Contenido/Mitigado</option>
            <option value="RESOLVED">RESOLVED - Resuelto (Post-mortem listo)</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Estado de Mitigación / Notas
          </label>
          <textarea 
            v-model="form.mitigationState"
            rows="4"
            placeholder="Anota los avances, workarounds o acciones tomadas..."
            class="w-full px-4 py-3 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all resize-none"
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
          Cancelar
        </button>
        <button 
          @click="handleSubmit"
          :disabled="isSubmitting"
          class="px-6 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-xl transition-all shadow-sm hover:shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ isSubmitting ? 'Guardando...' : 'Guardar Cambios' }}
        </button>
      </div>
      
    </div>
  </div>
</template>
