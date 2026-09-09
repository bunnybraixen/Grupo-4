<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { CheckSquare, X, User as UserIcon } from 'lucide-vue-next'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'
import type { Meeting, User } from '@/types'

const props = defineProps<{
  show: boolean
  meeting: Meeting | null
}>()

const emit = defineEmits(['close', 'updated'])

const dialogStore = useDialogStore()
const isSubmitting = ref(false)
const isLoadingUsers = ref(false)

const allUsers = ref<User[]>([])
// Map: userId -> { status, notes }
const attendanceMap = ref<Record<string, { status: string, notes: string }>>({})

const loadUsers = async () => {
  isLoadingUsers.value = true
  try {
    const data: any = await api.users.list()
    // Depending on backend response format, could be data.items, data.data.items, or an array directly
    allUsers.value = data.items || data.data?.items || (Array.isArray(data) ? data : [])
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    isLoadingUsers.value = false
  }
}

watch(() => props.meeting, async (newMeeting) => {
  if (newMeeting && props.show) {
    await loadUsers()
    
    // Initialize map with ABSENT for everyone, then override with existing
    const newMap: Record<string, { status: string, notes: string }> = {}
    allUsers.value.forEach(u => {
      newMap[u.id] = { status: 'ABSENT', notes: '' }
    })
    
    if (newMeeting.attendances) {
      newMeeting.attendances.forEach((att: any) => {
        newMap[att.userId || att.user_id] = {
          status: att.status,
          notes: att.notes || ''
        }
      })
    }
    
    attendanceMap.value = newMap
  }
}, { immediate: true })

const handleClose = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (!props.meeting) return

  isSubmitting.value = true
  try {
    // El backend registra la asistencia de un usuario por llamada
    // (POST /meetings/{meeting_id}/attendance recibe UN MeetingAttendanceCreate,
    // no una lista), así que se dispara una petición por asistente.
    const payload = Object.entries(attendanceMap.value).map(([userId, data]) => ({
      user_id: userId,
      status: data.status,
      notes: data.notes || undefined
    }))

    await Promise.all(
      payload.map(item => api.meetings.setAttendance(props.meeting!.id, item))
    )
    
    emit('updated')
    handleClose()
    dialogStore.alert('Asistencia registrada exitosamente')
  } catch (error: any) {
    console.error('Error al registrar asistencia:', error)
    dialogStore.alert('Error al registrar la asistencia: ' + (error.response?.data?.detail || error.message))
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
          <CheckSquare class="text-teal-600" :size="20" />
          Registrar Asistencia: {{ meeting.title }}
        </h3>
        <button 
          @click="handleClose"
          class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-[var(--bg-card)] rounded-xl transition-colors"
        >
          <X :size="20" />
        </button>
      </div>

      <!-- Body -->
      <div class="p-0 overflow-y-auto flex-1 bg-slate-50 dark:bg-[var(--bg-body)]">
        <div v-if="isLoadingUsers" class="flex justify-center p-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
        </div>
        
        <table v-else class="w-full text-left text-sm">
          <thead class="bg-white dark:bg-[var(--bg-panel)] sticky top-0 border-b border-slate-200 dark:border-[var(--border-subtle)] shadow-sm">
            <tr>
              <th class="px-6 py-3 font-medium text-slate-500 dark:text-[var(--text-muted)]">Miembro</th>
              <th class="px-6 py-3 font-medium text-slate-500 dark:text-[var(--text-muted)] w-48">Estado</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-[var(--border-subtle)]">
            <tr v-for="user in allUsers" :key="user.id" class="hover:bg-slate-100/50 dark:hover:bg-[var(--bg-card)]">
              <td class="px-6 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-400">
                    <UserIcon :size="16" />
                  </div>
                  <div>
                    <p class="font-medium text-slate-900 dark:text-white">{{ user.fullName }}</p>
                    <p class="text-xs text-slate-500 dark:text-[var(--text-muted)]">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-3">
                <select 
                  v-model="attendanceMap[user.id].status"
                  class="w-full px-3 py-1.5 text-sm bg-white dark:bg-[var(--bg-panel)] border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all appearance-none"
                  :class="{
                    'text-green-600 dark:text-green-400 font-medium': attendanceMap[user.id].status === 'PRESENT',
                    'text-red-600 dark:text-red-400 font-medium': attendanceMap[user.id].status === 'ABSENT',
                    'text-amber-600 dark:text-amber-400 font-medium': attendanceMap[user.id].status === 'JUSTIFIED'
                  }"
                >
                  <option value="PRESENT" class="text-slate-900 dark:text-white">Presente</option>
                  <option value="ABSENT" class="text-slate-900 dark:text-white">Ausente</option>
                  <option value="JUSTIFIED" class="text-slate-900 dark:text-white">Justificado</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-slate-100 dark:border-[var(--border-subtle)] flex items-center justify-end gap-3 bg-white dark:bg-[var(--bg-panel)]">
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
          class="px-6 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-xl transition-all shadow-sm hover:shadow-md disabled:opacity-50 flex items-center gap-2"
        >
          <div v-if="isSubmitting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          {{ isSubmitting ? 'Guardando...' : 'Guardar Asistencia' }}
        </button>
      </div>
      
    </div>
  </div>
</template>
