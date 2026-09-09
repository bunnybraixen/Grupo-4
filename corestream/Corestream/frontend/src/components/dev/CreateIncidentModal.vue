<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ShieldAlert, X } from 'lucide-vue-next'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits(['close', 'created'])

const dialogStore = useDialogStore()
const isSubmitting = ref(false)

const form = reactive({
  title: '',
  description: '',
  severity: 'P3',
  affectedEnvironment: 'PRODUCTION',
  estimatedResolutionTimeSeconds: 3600 // 1 hr
})

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.severity = 'P3'
  form.affectedEnvironment = 'PRODUCTION'
  form.estimatedResolutionTimeSeconds = 3600
}

const handleClose = () => {
  resetForm()
  emit('close')
}

const handleSubmit = async () => {
  if (!form.title.trim()) {
    dialogStore.alert('El título es requerido')
    return
  }

  isSubmitting.value = true
  try {
    const dataToSubmit = {
      title: form.title.trim(),
      description: form.description.trim() || undefined,
      severity: form.severity,
      affected_environment: form.affectedEnvironment,
      estimated_resolution_time_seconds: form.estimatedResolutionTimeSeconds
    }
    await api.incidents.create(dataToSubmit)
    emit('created')
    handleClose()
    dialogStore.alert('Incidente reportado exitosamente')
  } catch (error: any) {
    console.error('Error al reportar incidente:', error)
    dialogStore.alert('Error al reportar el incidente: ' + (error.response?.data?.detail || error.message))
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
    <div class="bg-white dark:bg-[var(--bg-panel)] rounded-2xl shadow-xl w-full max-w-md overflow-hidden flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="px-6 py-4 border-b border-slate-100 dark:border-[var(--border-subtle)] flex items-center justify-between bg-slate-50/50 dark:bg-transparent">
        <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <ShieldAlert class="text-red-500" :size="20" />
          Reportar Nuevo Incidente
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
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Título del Incidente <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.title"
            type="text" 
            placeholder="Ej: Caída de base de datos principal"
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
            required
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Descripción Detallada
          </label>
          <textarea 
            v-model="form.description"
            rows="3"
            placeholder="Describe los síntomas, servicios afectados y posibles causas..."
            class="w-full px-4 py-3 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all resize-none"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Severidad
            </label>
            <select 
              v-model="form.severity"
              class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all appearance-none"
            >
              <option value="P1">P1 - Crítico (Sistema Caído)</option>
              <option value="P2">P2 - Alto (Falla Parcial)</option>
              <option value="P3">P3 - Medio (Degradación)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Entorno Afectado
            </label>
            <select 
              v-model="form.affectedEnvironment"
              class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all appearance-none"
            >
              <option value="PRODUCTION">Production</option>
              <option value="STAGING">Staging</option>
              <option value="DEV">Development</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Tiempo Estimado de Resolución
          </label>
          <select 
            v-model="form.estimatedResolutionTimeSeconds"
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all appearance-none"
          >
            <option :value="1800">30 Minutos</option>
            <option :value="3600">1 Hora</option>
            <option :value="7200">2 Horas</option>
            <option :value="14400">4 Horas</option>
            <option :value="28800">8 Horas</option>
            <option :value="86400">1 Día o más</option>
          </select>
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
          :disabled="isSubmitting || !form.title.trim()"
          class="px-6 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-xl transition-all shadow-sm hover:shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ isSubmitting ? 'Reportando...' : 'Reportar Incidente' }}
        </button>
      </div>
      
    </div>
  </div>
</template>
