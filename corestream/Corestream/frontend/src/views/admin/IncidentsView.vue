<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { 
  AlertTriangle, 
  ShieldAlert, 
  CheckCircle, 
  Clock, 
  Plus,
  Server,
  User as UserIcon,
  Activity
} from 'lucide-vue-next'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { Incident } from '@/types'
import { TicketStatus } from '@/types'
import CreateIncidentModal from '@/components/dev/CreateIncidentModal.vue'
import ManageIncidentModal from '@/components/dev/ManageIncidentModal.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const authStore = useAuthStore()

const incidents = ref<Incident[]>([])
const isLoading = ref(true)
const showCreateModal = ref(false)
const showManageModal = ref(false)
const selectedIncident = ref<Incident | null>(null)

const openManageModal = (incident: Incident) => {
  selectedIncident.value = incident
  showManageModal.value = true
}

const loadIncidents = async () => {
  isLoading.value = true
  try {
    const response = await api.incidents.list({ limit: 100 })
    incidents.value = response.items || []
  } catch (error) {
    console.error('Error fetching incidents:', error)
  } finally {
    isLoading.value = false
  }
}

const activeIncidents = computed(() => {
  return incidents.value.filter(i => !i.isMitigated)
})

const pastIncidents = computed(() => {
  return incidents.value.filter(i => i.isMitigated)
})

const getSeverityColor = (severity: string) => {
  if (severity === 'P1') return 'bg-red-500 border-red-600 text-white'
  if (severity === 'P2') return 'bg-orange-500 border-orange-600 text-white'
  return 'bg-yellow-500 border-yellow-600 text-white'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadIncidents()
})
</script>

<template>
  <div class="h-full bg-slate-50 dark:bg-[var(--bg-body)]">
    <AppHeader />
    <!-- Header -->
    <header class="bg-white dark:bg-[var(--bg-panel)] border-b border-slate-200 dark:border-[var(--border-subtle)] px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-[var(--text-primary)] flex items-center gap-2">
          <ShieldAlert class="text-red-500" :size="28" />
          Centro de Incidentes
        </h1>
        <p class="text-sm text-slate-500 dark:text-[var(--text-muted)] mt-1">
          Gestión de crisis, caída de servicios y resolución de urgencias (P1, P2, P3).
        </p>
      </div>

      <div class="flex items-center gap-3">
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2 shadow-sm"
        >
          <Plus :size="18" /> Reportar Incidente
        </button>
        <button
          @click="loadIncidents"
          :disabled="isLoading"
          class="px-4 py-2 bg-slate-100 dark:bg-[var(--bg-card)] text-slate-700 dark:text-[var(--text-secondary)] font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-[var(--border-subtle)] transition-colors disabled:opacity-50"
        >
          🔄 Actualizar
        </button>
      </div>
    </header>

    <div class="p-6 overflow-y-auto" style="height: calc(100vh - 89px);">
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-red-500"></div>
      </div>

      <div v-else class="space-y-8">
        
        <!-- Active Incidents -->
        <section>
          <h2 class="text-lg font-semibold text-slate-800 dark:text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <Activity class="text-red-500" :size="20" />
            Incidentes Activos
            <span class="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs py-0.5 px-2 rounded-full font-bold">
              {{ activeIncidents.length }}
            </span>
          </h2>

          <div v-if="activeIncidents.length === 0" class="bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-900/30 rounded-xl p-8 flex flex-col items-center justify-center text-center">
            <CheckCircle class="text-green-500 mb-3" :size="48" />
            <h3 class="text-lg font-semibold text-green-800 dark:text-green-400">Todos los sistemas operativos</h3>
            <p class="text-green-600 dark:text-green-500 mt-1">No hay incidentes activos en este momento.</p>
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <div v-for="incident in activeIncidents" :key="incident.id" class="bg-white dark:bg-[var(--bg-panel)] rounded-xl border border-red-200 dark:border-red-900/50 shadow-sm overflow-hidden flex flex-col relative group">
              <div class="absolute top-0 left-0 w-1 h-full" :class="getSeverityColor(incident.severity)"></div>
              <div class="p-5 pl-6 flex-1">
                <div class="flex justify-between items-start mb-3">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold" :class="getSeverityColor(incident.severity)">
                    {{ incident.severity }}
                  </span>
                  <span class="text-xs text-slate-500 dark:text-[var(--text-muted)] flex items-center gap-1">
                    <Clock :size="12" /> {{ formatDate(incident.createdAt) }}
                  </span>
                </div>
                <h3 class="text-lg font-bold text-slate-900 dark:text-white mb-2">{{ incident.title }}</h3>
                <p class="text-sm text-slate-600 dark:text-[var(--text-secondary)] mb-4 line-clamp-2">{{ incident.description }}</p>
                
                <div class="space-y-2 mt-auto">
                  <div class="flex justify-between items-center text-xs">
                    <span class="text-slate-500 dark:text-[var(--text-muted)] flex items-center gap-1"><Server :size="14"/> Entorno</span>
                    <span class="font-medium text-slate-700 dark:text-slate-300">{{ incident.affectedEnvironment }}</span>
                  </div>
                  <div class="flex justify-between items-center text-xs">
                    <span class="text-slate-500 dark:text-[var(--text-muted)] flex items-center gap-1"><Activity :size="14"/> Estado</span>
                    <span class="font-medium text-amber-600 dark:text-amber-400">{{ incident.status }}</span>
                  </div>
                </div>
              </div>
              <div class="bg-slate-50 dark:bg-[var(--bg-card)] px-5 py-3 border-t border-slate-100 dark:border-[var(--border-subtle)] flex justify-between items-center pl-6">
                <div class="text-xs text-slate-500 dark:text-[var(--text-muted)] flex items-center gap-1">
                  <UserIcon :size="14" /> {{ incident.assignedToId ? 'Asignado' : 'Sin asignar' }}
                </div>
                <button @click="openManageModal(incident)" class="text-sm text-red-600 dark:text-red-400 font-medium hover:underline">Gestionar</button>
              </div>
            </div>
          </div>
        </section>

        <!-- Past Incidents -->
        <section v-if="pastIncidents.length > 0">
          <h2 class="text-lg font-semibold text-slate-800 dark:text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <CheckCircle class="text-green-500" :size="20" />
            Incidentes Mitigados
          </h2>
          <div class="bg-white dark:bg-[var(--bg-panel)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] overflow-hidden">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 dark:bg-[var(--bg-card)] border-b border-slate-200 dark:border-[var(--border-subtle)] text-slate-500 dark:text-[var(--text-muted)]">
                <tr>
                  <th class="px-6 py-3 font-medium">Incidente</th>
                  <th class="px-6 py-3 font-medium">Severidad</th>
                  <th class="px-6 py-3 font-medium">Entorno</th>
                  <th class="px-6 py-3 font-medium">Mitigado el</th>
                  <th class="px-6 py-3 font-medium text-right">Acciones</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-[var(--border-subtle)]">
                <tr v-for="incident in pastIncidents" :key="incident.id" class="hover:bg-slate-50 dark:hover:bg-[var(--bg-card)] transition-colors">
                  <td class="px-6 py-4">
                    <p class="font-medium text-slate-900 dark:text-white">{{ incident.title }}</p>
                    <p class="text-xs text-slate-500 dark:text-[var(--text-muted)]">{{ formatDate(incident.createdAt) }}</p>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold" :class="getSeverityColor(incident.severity)">
                      {{ incident.severity }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-slate-600 dark:text-[var(--text-secondary)]">{{ incident.affectedEnvironment }}</td>
                  <td class="px-6 py-4 text-slate-600 dark:text-[var(--text-secondary)]">{{ incident.mitigatedAt ? formatDate(incident.mitigatedAt) : 'N/A' }}</td>
                  <td class="px-6 py-4 text-right">
                    <button @click="openManageModal(incident)" class="text-teal-600 dark:text-teal-400 hover:underline">Post-mortem</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

      </div>
    </div>
    
    <CreateIncidentModal 
      :show="showCreateModal" 
      @close="showCreateModal = false" 
      @created="loadIncidents" 
    />
    
    <ManageIncidentModal 
      :show="showManageModal" 
      :incident="selectedIncident" 
      @close="showManageModal = false" 
      @updated="loadIncidents" 
    />
  </div>
</template>
