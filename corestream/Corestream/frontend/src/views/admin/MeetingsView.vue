<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  CalendarDays, 
  Users, 
  Clock, 
  Plus, 
  FileText,
  CheckSquare
} from 'lucide-vue-next'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Meeting } from '@/types'
import CreateMeetingModal from '@/components/dev/CreateMeetingModal.vue'
import MeetingAttendanceModal from '@/components/dev/MeetingAttendanceModal.vue'
import MeetingSummaryModal from '@/components/dev/MeetingSummaryModal.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const authStore = useAuthStore()
const meetings = ref<Meeting[]>([])
const isLoading = ref(true)

const showCreateModal = ref(false)
const showAttendanceModal = ref(false)
const showSummaryModal = ref(false)
const selectedMeeting = ref<Meeting | null>(null)

const openAttendance = (meeting: Meeting) => {
  selectedMeeting.value = meeting
  showAttendanceModal.value = true
}

const openSummary = (meeting: Meeting) => {
  selectedMeeting.value = meeting
  showSummaryModal.value = true
}

const canCreate = computed(() => {
  return authStore.user?.role === 'ADMIN' || authStore.user?.role === 'TEAM_LEADER'
})

const loadMeetings = async () => {
  isLoading.value = true
  try {
    const data = await api.meetings.list({ limit: 100 })
    meetings.value = data || []
  } catch (error) {
    console.error('Error fetching meetings:', error)
  } finally {
    isLoading.value = false
  }
}

const upcomingMeetings = computed(() => {
  const now = new Date()
  return meetings.value
    .filter(m => new Date(m.scheduledAt) >= now)
    .sort((a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime())
})

const pastMeetings = computed(() => {
  const now = new Date()
  return meetings.value
    .filter(m => new Date(m.scheduledAt) < now)
    .sort((a, b) => new Date(b.scheduledAt).getTime() - new Date(a.scheduledAt).getTime())
})

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('es', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getMeetingTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'DAILY': 'Daily Scrum',
    'PLANNING': 'Sprint Planning',
    'RETROSPECTIVE': 'Retrospectiva',
    'REFINEMENT': 'Refinamiento',
    'OTHER': 'Otra Ceremonia'
  }
  return labels[type] || type
}

const getMeetingTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'DAILY': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 border-blue-200 dark:border-blue-800',
    'PLANNING': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 border-purple-200 dark:border-purple-800',
    'RETROSPECTIVE': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 border-amber-200 dark:border-amber-800',
    'REFINEMENT': 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-300 border-teal-200 dark:border-teal-800',
    'OTHER': 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700'
  }
  return colors[type] || colors['OTHER']
}

onMounted(() => {
  loadMeetings()
})
</script>

<template>
  <div class="h-full bg-slate-50 dark:bg-[var(--bg-body)]">
    <AppHeader />
    <!-- Header -->
    <header class="bg-white dark:bg-[var(--bg-panel)] border-b border-slate-200 dark:border-[var(--border-subtle)] px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-[var(--text-primary)] flex items-center gap-2">
          <CalendarDays class="text-teal-600 dark:text-teal-400" :size="28" />
          Calendario de Reuniones
        </h1>
        <p class="text-sm text-slate-500 dark:text-[var(--text-muted)] mt-1">
          Agenda de ceremonias, registro de asistencia y actas.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <button
          v-if="canCreate"
          @click="showCreateModal = true"
          class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 shadow-sm"
        >
          <Plus :size="18" /> Agendar Ceremonia
        </button>
        <button
          @click="loadMeetings"
          :disabled="isLoading"
          class="px-4 py-2 bg-slate-100 dark:bg-[var(--bg-card)] text-slate-700 dark:text-[var(--text-secondary)] font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-[var(--border-subtle)] transition-colors disabled:opacity-50"
        >
          🔄 Actualizar
        </button>
      </div>
    </header>

    <div class="p-6 overflow-y-auto" style="height: calc(100vh - 89px);">
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-teal-500"></div>
      </div>

      <div v-else class="max-w-6xl mx-auto space-y-8">
        
        <!-- Próximas Reuniones -->
        <section>
          <h2 class="text-lg font-semibold text-slate-800 dark:text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Clock class="text-teal-500" :size="20" />
            Próximas Reuniones
          </h2>

          <div v-if="upcomingMeetings.length === 0" class="bg-white dark:bg-[var(--bg-panel)] border border-dashed border-slate-300 dark:border-[var(--border-subtle)] rounded-xl p-8 flex flex-col items-center justify-center text-center">
            <CalendarDays class="text-slate-400 dark:text-slate-600 mb-3" :size="48" />
            <h3 class="text-lg font-semibold text-slate-700 dark:text-slate-300">Agenda Libre</h3>
            <p class="text-slate-500 dark:text-[var(--text-muted)] mt-1">No hay ceremonias programadas próximamente.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="meeting in upcomingMeetings" :key="meeting.id" class="bg-white dark:bg-[var(--bg-panel)] rounded-xl border border-slate-200 dark:border-[var(--border-subtle)] shadow-sm hover:shadow-md transition-shadow p-5 flex flex-col">
              <div class="flex justify-between items-start mb-3">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border" :class="getMeetingTypeColor(meeting.meetingType)">
                  {{ getMeetingTypeLabel(meeting.meetingType) }}
                </span>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1 bg-slate-100 dark:bg-[var(--bg-card)] px-2 py-1 rounded-md">
                  <Clock :size="14" /> {{ meeting.durationMinutes }} min
                </span>
              </div>
              
              <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1">{{ meeting.title }}</h3>
              <p class="text-teal-600 dark:text-teal-400 font-medium mb-4">{{ formatDateTime(meeting.scheduledAt) }}</p>
              
              <div class="mt-auto pt-4 border-t border-slate-100 dark:border-[var(--border-subtle)] flex gap-2">
                <button @click="openAttendance(meeting)" class="flex-1 bg-slate-100 dark:bg-[var(--bg-card)] hover:bg-slate-200 dark:hover:bg-slate-700/50 text-slate-700 dark:text-slate-300 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1.5">
                  <CheckSquare :size="16" /> Asistencia
                </button>
                <button @click="openSummary(meeting)" class="flex-1 bg-teal-50 dark:bg-teal-900/10 hover:bg-teal-100 dark:hover:bg-teal-900/30 text-teal-700 dark:text-teal-400 border border-teal-200 dark:border-teal-800/50 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1.5">
                  <FileText :size="16" /> Ver Acta
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Historial -->
        <section v-if="pastMeetings.length > 0">
          <h2 class="text-lg font-semibold text-slate-800 dark:text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <CheckSquare class="text-slate-500" :size="20" />
            Historial de Reuniones
          </h2>
          
          <div class="bg-white dark:bg-[var(--bg-panel)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] overflow-hidden">
            <ul class="divide-y divide-slate-100 dark:divide-[var(--border-subtle)]">
              <li v-for="meeting in pastMeetings" :key="meeting.id" class="p-4 hover:bg-slate-50 dark:hover:bg-[var(--bg-card)] transition-colors flex items-center justify-between gap-4">
                <div class="flex items-center gap-4">
                  <div class="hidden sm:flex flex-col items-center justify-center w-14 h-14 bg-slate-100 dark:bg-[var(--bg-card)] rounded-lg text-slate-500 dark:text-slate-400">
                    <span class="text-lg font-bold leading-none">{{ new Date(meeting.scheduledAt).getDate() }}</span>
                    <span class="text-xs uppercase">{{ new Date(meeting.scheduledAt).toLocaleString('es', { month: 'short' }) }}</span>
                  </div>
                  <div>
                    <h4 class="font-semibold text-slate-900 dark:text-white">{{ meeting.title }}</h4>
                    <div class="flex items-center gap-3 text-sm text-slate-500 dark:text-[var(--text-muted)] mt-1">
                      <span class="flex items-center gap-1"><Clock :size="14"/> {{ new Date(meeting.scheduledAt).toLocaleString('es', { hour: '2-digit', minute: '2-digit' }) }} ({{ meeting.durationMinutes }}m)</span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border" :class="getMeetingTypeColor(meeting.meetingType)">
                        {{ getMeetingTypeLabel(meeting.meetingType) }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="flex items-center gap-2">
                  <div class="text-sm text-slate-500 dark:text-[var(--text-muted)] hidden md:flex items-center gap-1 mr-4">
                    <Users :size="16" /> {{ meeting.attendances?.length || 0 }} asistencias
                  </div>
                  <button @click="openAttendance(meeting)" class="px-3 py-1.5 text-sm font-medium text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-[var(--bg-card)] rounded-md hover:bg-slate-200 dark:hover:bg-slate-700/50 transition-colors">
                    Asistencia
                  </button>
                  <button @click="openSummary(meeting)" class="px-3 py-1.5 text-sm font-medium text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-900/10 rounded-md hover:bg-teal-100 dark:hover:bg-teal-900/30 transition-colors">
                    Acta
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </section>

      </div>
    </div>

    <CreateMeetingModal 
      :show="showCreateModal" 
      @close="showCreateModal = false" 
      @created="loadMeetings" 
    />

    <MeetingAttendanceModal 
      :show="showAttendanceModal" 
      :meeting="selectedMeeting" 
      @close="showAttendanceModal = false" 
      @updated="loadMeetings" 
    />

    <MeetingSummaryModal 
      :show="showSummaryModal" 
      :meeting="selectedMeeting" 
      @close="showSummaryModal = false" 
      @updated="loadMeetings" 
    />
  </div>
</template>
