<!--
  ReportsView - Reportes generales del proyecto (WEB-06)

  Consulta consolidada del estado operacional del proyecto:
    - Filtros en pantalla: proyecto, desarrollador y sprint.
    - Indicadores: totales, completados, pendientes, en progreso, vencidos,
      bloqueados, redireccionados, % de avance, % de bloqueo y tiempo promedio.
    - Distribución por estado, por prioridad y cuellos de botella.
    - Exportación PDF / Excel que respeta los filtros aplicados e incluye la
      fecha de generación y el alcance del reporte.
-->
<template>
  <div class="space-y-6 p-6">
    <header class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ t('reportsPage.title') }}</h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {{ t('reportsPage.subtitle') }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          type="button"
          class="rounded-lg bg-teal-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          :disabled="!summary || isExporting"
          @click="downloadPDF"
        >
          {{ t('reportsPage.exportPdf') }}
        </button>
        <button
          type="button"
          class="rounded-lg border border-teal-600 px-4 py-2 text-sm font-medium text-teal-600 disabled:opacity-50"
          :disabled="!summary || isExporting"
          @click="downloadExcel"
        >
          {{ t('reportsPage.exportExcel') }}
        </button>
      </div>
    </header>

    <!-- ============================ FILTROS ============================ -->
    <section class="flex flex-wrap items-end gap-3 rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('reportsPage.project') }}
        <select
          v-model="selectedProjectId"
          class="min-w-56 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-teal-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="">{{ t('reportsPage.selectProject') }}</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </label>

      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('reportsPage.developer') }}
        <select
          v-model="selectedDeveloperId"
          :disabled="!developers.length"
          class="min-w-56 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-teal-500 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="">{{ t('reportsPage.allTeam') }}</option>
          <option v-for="developer in developers" :key="developer.id" :value="developer.id">
            {{ developer.fullName || developer.email }}
          </option>
        </select>
      </label>

      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('reportsPage.sprint') }}
        <select
          v-model="selectedSprintId"
          :disabled="!sprints.length"
          class="min-w-56 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-teal-500 disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="">{{ t('reportsPage.allSprints') }}</option>
          <option v-for="sprint in sprints" :key="sprint.id" :value="sprint.id">
            {{ sprint.name }}
          </option>
        </select>
      </label>
    </section>

    <p v-if="isLoading" class="text-sm text-gray-500 dark:text-gray-400">{{ t('reportsPage.loading') }}</p>
    <p v-else-if="errorMessage" class="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-500">
      {{ errorMessage }}
    </p>
    <p v-else-if="!summary" class="text-sm text-gray-500 dark:text-gray-400">
      {{ t('reportsPage.selectProjectHint') }}
    </p>

    <template v-else>
      <!-- ========================== INDICADORES ========================== -->
      <section class="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <article
          v-for="indicator in indicators"
          :key="indicator.label"
          class="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
        >
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            {{ indicator.label }}
          </p>
          <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{{ indicator.value }}</p>
        </article>
      </section>

      <!-- ===================== DISTRIBUCIONES ===================== -->
      <section class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
          <h2 class="mb-3 font-semibold text-gray-900 dark:text-white">{{ t('reportsPage.statusDistribution') }}</h2>
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-gray-500 dark:text-gray-400">
                <th class="py-1 font-medium">{{ t('reportsPage.status') }}</th>
                <th class="py-1 text-right font-medium">{{ t('reportsPage.tickets') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in statusRows" :key="row[0]" class="border-t border-gray-100 dark:border-gray-800">
                <td class="py-1.5 text-gray-800 dark:text-gray-200">{{ row[0] }}</td>
                <td class="py-1.5 text-right font-semibold text-gray-900 dark:text-white">{{ row[1] }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
          <h2 class="mb-3 font-semibold text-gray-900 dark:text-white">{{ t('reportsPage.priorityDistribution') }}</h2>
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-gray-500 dark:text-gray-400">
                <th class="py-1 font-medium">{{ t('reportsPage.priority') }}</th>
                <th class="py-1 text-right font-medium">{{ t('reportsPage.tickets') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in priorityRows" :key="row[0]" class="border-t border-gray-100 dark:border-gray-800">
                <td class="py-1.5 text-gray-800 dark:text-gray-200">{{ row[0] }}</td>
                <td class="py-1.5 text-right font-semibold text-gray-900 dark:text-white">{{ row[1] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ===================== CUELLOS DE BOTELLA ===================== -->
      <section v-if="bottleneckRows.length" class="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
        <h2 class="mb-3 font-semibold text-gray-900 dark:text-white">{{ t('reportsPage.bottlenecks') }}</h2>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-500 dark:text-gray-400">
              <th class="py-1 font-medium">{{ t('reportsPage.status') }}</th>
              <th class="py-1 text-right font-medium">{{ t('reportsPage.tickets') }}</th>
              <th class="py-1 text-right font-medium">{{ t('reportsPage.averageHours') }}</th>
              <th class="py-1 text-right font-medium">{{ t('reportsPage.maxHours') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in bottleneckRows" :key="row[0]" class="border-t border-gray-100 dark:border-gray-800">
              <td class="py-1.5 text-gray-800 dark:text-gray-200">{{ row[0] }}</td>
              <td class="py-1.5 text-right text-gray-900 dark:text-white">{{ row[1] }}</td>
              <td class="py-1.5 text-right text-gray-900 dark:text-white">{{ row[2] }}</td>
              <td class="py-1.5 text-right text-gray-900 dark:text-white">{{ row[3] }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
/**
 * ReportsView - Reporte general consolidado + exportación (WEB-06).
 *
 * Reutiliza el endpoint GET /analytics/summary/{app_id} con los mismos filtros
 * que Analíticas (assignee_id, sprint_id) para que lo exportado en PDF/Excel
 * coincida exactamente con lo que se ve en pantalla.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'
import apiClient from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import {
  exportProjectReportExcel,
  exportProjectReportPDF,
  type ProjectReportPayload,
  type ProjectReportTable
} from '@/services/projectReportExport'
import type { Application, ApplicationSummary, User } from '@/types'
import type { Sprint } from '@/types/sprint'

const authStore = useAuthStore()
const teamsStore = useTeamsStore()
const { t, locale } = useI18n()

const projects = ref<Application[]>([])
const developers = ref<User[]>([])
const sprints = ref<Sprint[]>([])
const selectedProjectId = ref('')
const selectedDeveloperId = ref('')
const selectedSprintId = ref('')
const summary = ref<ApplicationSummary | null>(null)
const isLoading = ref(false)
const isExporting = ref(false)
const errorMessage = ref('')
let summaryRequestId = 0

const statusLabel = (status: string) => t(`analyticsPage.statuses.${status === 'COMPLETED' ? 'DONE' : status}`)
const priorityLabel = (priority: string) => t(`statuses.${priority.toLowerCase()}`)
// ── Datos computados para la vista y la exportación ─────────────────────────

const indicators = computed(() => {
  const data = summary.value
  if (!data) return []
  return [
    { label: t('reportsPage.indicators.totalTickets'), value: String(data.total_tickets ?? 0) },
    { label: t('reportsPage.indicators.completed'), value: String(data.completed_tickets ?? 0) },
    { label: t('reportsPage.indicators.pending'), value: String(data.pending_tickets ?? 0) },
    { label: t('reportsPage.indicators.inProgress'), value: String(data.in_progress_tickets ?? 0) },
    { label: t('reportsPage.indicators.overdue'), value: String(data.overdue_tickets ?? 0) },
    { label: t('reportsPage.indicators.blocked'), value: String(data.blocked_tickets ?? 0) },
    { label: t('reportsPage.indicators.redirected'), value: String(data.redirected_tickets ?? 0) },
    { label: t('reportsPage.indicators.progress'), value: `${Math.round(data.completion_percentage ?? 0)}%` },
    { label: t('reportsPage.indicators.blockedPercent'), value: `${Math.round(data.blocked_percentage ?? 0)}%` },
    { label: t('reportsPage.indicators.averageTime'), value: `${data.avg_time_hours ?? data.avg_time ?? 0} h` }
  ]
})

const statusRows = computed<string[][]>(() =>
  Object.entries(summary.value?.by_status ?? {}).map(([status, count]) => [
    statusLabel(status),
    String(count)
  ])
)

const priorityRows = computed<string[][]>(() =>
  Object.entries(summary.value?.by_priority ?? {}).map(([priority, count]) => [
    priorityLabel(priority),
    String(count)
  ])
)

const bottleneckRows = computed<string[][]>(() =>
  (summary.value?.bottlenecks ?? []).map((item) => [
    statusLabel(item.status),
    String(item.ticket_count),
    String(Math.round(item.average_hours ?? 0)),
    String(Math.round(item.max_hours ?? 0))
  ])
)

const projectName = computed(
  () => projects.value.find((project) => project.id === selectedProjectId.value)?.name ?? '—'
)

const developerName = computed(() => {
  if (!selectedDeveloperId.value) return 'Todo el equipo'
  const developer = developers.value.find((item) => item.id === selectedDeveloperId.value)
  return developer?.fullName || developer?.email || '—'
})

const sprintName = computed(() => {
  if (!selectedSprintId.value) return 'Todos los sprints'
  return sprints.value.find((sprint) => sprint.id === selectedSprintId.value)?.name ?? '—'
})

// ── Carga de datos ──────────────────────────────────────────────────────────

const loadProjects = async (): Promise<void> => {
  try {
    await teamsStore.refreshFromServer()
    const response = await api.applications.list()
    const all = normalizeList<Application>(response)
    if (authStore.isAdmin) {
      projects.value = all
    } else {
      const assignedIds = new Set(
        teamsStore.getUserTeams(authStore.userEmail ?? '').flatMap((team) => team.applicationIds ?? [])
      )
      projects.value = all.filter((project) => assignedIds.has(project.id))
    }
    projects.value.sort((a, b) => a.name.localeCompare(b.name))
    selectedProjectId.value = projects.value[0]?.id ?? ''
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : t('reportsPage.projectLoadError')
  }
}

const loadProjectOptions = async (projectId: string): Promise<void> => {
  selectedDeveloperId.value = ''
  selectedSprintId.value = ''
  developers.value = []
  sprints.value = []
  if (!projectId) return

  const team = teamsStore.getTeamForApp(projectId)
  const memberEmails = new Set((team?.memberEmails ?? []).map((email) => email.trim().toLowerCase()))
  try {
    const [usersResponse, sprintResponse] = await Promise.all([
      api.users.list({ limit: 100 }),
      api.sprints.list({ applicationId: projectId })
    ])
    const allUsers = normalizeList<User>(usersResponse)
    // Mismo criterio que en Analíticas: miembros del equipo del proyecto; si no
    // tiene equipo, todos los DEVELOPER como respaldo.
    developers.value = memberEmails.size
      ? allUsers.filter((user) => memberEmails.has(user.email.trim().toLowerCase()))
      : allUsers.filter((user) => normalizeRole(String(user.role)) === 'DEVELOPER')
    sprints.value = sprintResponse
  } catch (error) {
    console.error('No se pudieron cargar desarrolladores o sprints:', error)
  }
}

const loadSummary = async (projectId: string): Promise<void> => {
  const requestId = ++summaryRequestId
  summary.value = null
  errorMessage.value = ''
  isLoading.value = true
  try {
    const response = await apiClient.get<ApplicationSummary>(`/analytics/summary/${projectId}`, {
      params: {
        assignee_id: selectedDeveloperId.value || undefined,
        sprint_id: selectedSprintId.value || undefined
      }
    })
    if (requestId === summaryRequestId) summary.value = response.data
  } catch (error) {
    if (requestId === summaryRequestId) {
      errorMessage.value = error instanceof Error ? error.message : t('reportsPage.reportLoadError')
    }
  } finally {
    if (requestId === summaryRequestId) isLoading.value = false
  }
}

// ── Exportación (mantiene los filtros en pantalla) ──────────────────────────

const buildPayload = (): ProjectReportPayload => {
  const table = (title: string, headers: string[], rows: string[][]): ProjectReportTable => ({
    title,
    headers,
    rows
  })
  return {
    scope: {
      projectName: projectName.value,
      developerName: developerName.value,
      sprintName: sprintName.value,
      generatedAt: new Date().toLocaleString(locale.value)
    },
    indicators: indicators.value,
    tables: [
      table(t('reportsPage.statusDistribution'), [t('reportsPage.status'), t('reportsPage.tickets')], statusRows.value),
      table(t('reportsPage.priorityDistribution'), [t('reportsPage.priority'), t('reportsPage.tickets')], priorityRows.value),
      table(
        t('reportsPage.bottleneckTable'),
        [t('reportsPage.status'), t('reportsPage.tickets'), t('reportsPage.averageHours'), t('reportsPage.maxHours')],
        bottleneckRows.value
      )
    ]
  }
}

const downloadPDF = (): void => {
  if (!summary.value) return
  isExporting.value = true
  try {
    exportProjectReportPDF(buildPayload())
  } finally {
    isExporting.value = false
  }
}

const downloadExcel = (): void => {
  if (!summary.value) return
  isExporting.value = true
  try {
    exportProjectReportExcel(buildPayload())
  } finally {
    isExporting.value = false
  }
}

// ── Observadores e inicialización ───────────────────────────────────────────

watch(selectedProjectId, (projectId) => {
  void loadProjectOptions(projectId)
  if (projectId) {
    void loadSummary(projectId)
  } else {
    summaryRequestId += 1
    summary.value = null
    isLoading.value = false
  }
})

watch([selectedDeveloperId, selectedSprintId], () => {
  if (selectedProjectId.value) void loadSummary(selectedProjectId.value)
})

onMounted(loadProjects)

function normalizeList<T>(response: unknown): T[] {
  const payload = (response as { data?: unknown } | null)?.data ?? response
  const items = (payload as { items?: unknown } | null)?.items ?? payload
  return Array.isArray(items) ? items as T[] : []
}

const normalizeRole = (role?: string | null) =>
  String(role ?? '').trim().toUpperCase().replace('USERROLE.', '').replace('-', '_')
</script>

