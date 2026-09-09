<script setup lang="ts">
import { ref, reactive } from 'vue'
import { CalendarDays, X } from 'lucide-vue-next'
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
  meetingType: 'OTHER',
  scheduledAt: ''
})

const resetForm = () => {
  form.title = ''
  form.meetingType = 'OTHER'
  form.scheduledAt = ''
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
  if (!form.scheduledAt) {
    dialogStore.alert('La fecha y hora son requeridas')
    return
  }

  isSubmitting.value = true
  try {
    const dataToSubmit = {
      title: form.title.trim(),
      meeting_type: form.meetingType,
      scheduled_at: new Date(form.scheduledAt).toISOString()
    }
    await api.meetings.create(dataToSubmit)
    emit('created')
    handleClose()
    dialogStore.alert('Reunión agendada exitosamente')
  } catch (error: any) {
    console.error('Error al agendar reunión:', error)
    dialogStore.alert('Error al agendar la reunión: ' + (error.response?.data?.detail || error.message))
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
          <CalendarDays class="text-teal-600" :size="20" />
          Agendar Ceremonia
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
            Título de la Reunión <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.title"
            type="text" 
            placeholder="Ej: Sprint Planning V2"
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
            required
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Tipo de Ceremonia
          </label>
          <select 
            v-model="form.meetingType"
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all appearance-none"
          >
            <option value="DAILY">Daily Scrum</option>
            <option value="PLANNING">Sprint Planning</option>
            <option value="RETROSPECTIVE">Retrospectiva</option>
            <option value="REFINEMENT">Refinamiento</option>
            <option value="OTHER">Otra Ceremonia</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
            Fecha y Hora <span class="text-red-500">*</span>
          </label>
          <input 
            v-model="form.scheduledAt"
            type="datetime-local" 
            class="w-full px-4 py-2 bg-slate-50 dark:bg-[var(--bg-card)] border border-slate-200 dark:border-[var(--border-subtle)] rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all"
            required
          >
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
          :disabled="isSubmitting || !form.title.trim() || !form.scheduledAt"
          class="px-6 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-xl transition-all shadow-sm hover:shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ isSubmitting ? 'Agendando...' : 'Agendar Reunión' }}
        </button>
      </div>
      
    </div>
  </div>
</template>
