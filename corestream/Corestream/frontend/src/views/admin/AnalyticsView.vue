<template>
  <div class="p-8">
    <header class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Analítica de proyectos
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Métricas de tickets del proyecto seleccionado
        </p>
      </div>

      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        Proyecto
        <select
          v-model="selectedProjectId"
          :disabled="isLoadingProjects || projects.length === 0"
          class="min-w-64 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="" disabled>Selecciona un proyecto</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </label>
    </header>

    <p v-if="isLoadingProjects" class="py-8 text-center text-gray-500 dark:text-gray-400">
      Cargando proyectos...
    </p>
    <p v-else-if="projectError" role="alert" class="py-8 text-center text-red-600 dark:text-red-400">
      {{ projectError }}
    </p>
    <p v-else-if="projects.length === 0" class="py-8 text-center text-gray-500 dark:text-gray-400">
      No hay proyectos asignados a tus equipos.
    </p>
    <p v-else-if="isLoadingSummary" class="py-8 text-center text-gray-500 dark:text-gray-400">
      Cargando analítica...
    </p>
    <p v-else-if="summaryError" role="alert" class="py-8 text-center text-red-600 dark:text-red-400">
      {{ summaryError }}
    </p>
    <template v-else-if="summary">
      <MetricCards :summary="summary" />
      <TicketDistribution :summary="summary" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { api } from '@/services/api'
import MetricCards from '@/components/analytics/MetricCards.vue'
import TicketDistribution from '@/components/analytics/TicketDistribution.vue'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import type { Application, ApplicationSummary } from '@/types'

const authStore = useAuthStore()
const teamsStore = useTeamsStore()

const projects = ref<Application[]>([])
const selectedProjectId = ref('')
const summary = ref<ApplicationSummary | null>(null)
const isLoadingProjects = ref(false)
const isLoadingSummary = ref(false)
const projectError = ref('')
const summaryError = ref('')
let summaryRequestId = 0

const normalizeList = <T>(response: unknown): T[] => {
  const payload = (response as { data?: unknown } | null)?.data ?? response
  const items = (payload as { items?: unknown } | null)?.items ?? payload
  return Array.isArray(items) ? items as T[] : []
}

const loadProjects = async () => {
  isLoadingProjects.value = true
  projectError.value = ''

  try {
    const [response] = await Promise.all([
      api.applications.list(),
      teamsStore.refreshFromServer(),
    ])
    const allProjects = normalizeList<Application>(response)

    if (authStore.isAdmin) {
      projects.value = allProjects
    } else {
      const assignedProjectIds = new Set(
        teamsStore.getUserTeams(authStore.userEmail)
          .flatMap((team) => team.applicationIds)
      )
      projects.value = allProjects.filter((project) => assignedProjectIds.has(project.id))
    }

    projects.value.sort((a, b) => a.name.localeCompare(b.name))
    selectedProjectId.value = projects.value[0]?.id ?? ''
  } catch (error) {
    projectError.value = error instanceof Error ? error.message : 'No se pudieron cargar los proyectos.'
  } finally {
    isLoadingProjects.value = false
  }
}

const loadSummary = async (projectId: string) => {
  const requestId = ++summaryRequestId
  summary.value = null
  summaryError.value = ''
  isLoadingSummary.value = true

  try {
    const data = await api.analytics.getSummary(projectId)
    if (requestId === summaryRequestId) summary.value = data
  } catch (error) {
    if (requestId === summaryRequestId) {
      summaryError.value = error instanceof Error ? error.message : 'No se pudo cargar la analítica.'
    }
  } finally {
    if (requestId === summaryRequestId) isLoadingSummary.value = false
  }
}

watch(selectedProjectId, (projectId) => {
  if (projectId) {
    void loadSummary(projectId)
  } else {
    summaryRequestId += 1
    summary.value = null
    isLoadingSummary.value = false
  }
})

onMounted(loadProjects)
</script>