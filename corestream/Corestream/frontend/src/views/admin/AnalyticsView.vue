<template>
  <div class="p-8">
    <header class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('analyticsPage.title') }}
        </h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          {{ t('analyticsPage.subtitle') }}
        </p>
      </div>

      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('analyticsPage.project') }}
        <select
          v-model="selectedProjectId"
          :disabled="isLoadingProjects || projects.length === 0"
          class="min-w-64 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-60 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="" disabled>{{ t('analyticsPage.selectProject') }}</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </label>
      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('analyticsPage.developer') }}
        <select v-model="selectedDeveloperId" :disabled="!developers.length" class="min-w-56 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
          <option value="">{{ t('analyticsPage.allTeam') }}</option>
          <option v-for="developer in developers" :key="developer.id" :value="developer.id">
            {{ developer.fullName || developer.email }}
          </option>
        </select>
      </label>
      <label class="flex flex-col gap-1 text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ t('analyticsPage.sprint') }}
        <select v-model="selectedSprintId" :disabled="!sprints.length" class="min-w-56 rounded-lg border border-gray-300 bg-white px-3 py-2 text-gray-900 shadow-sm outline-none focus:border-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
          <option value="">{{ t('analyticsPage.allTickets') }}</option>
          <option v-for="sprint in sprints" :key="sprint.id" :value="sprint.id">
            {{ sprint.name }}
          </option>
        </select>
      </label>
    </header>

    <p v-if="isLoadingProjects" class="py-8 text-center text-gray-500 dark:text-gray-400">
      {{ t('analyticsPage.loadingProjects') }}
    </p>
    <p v-else-if="projectError" role="alert" class="py-8 text-center text-red-600 dark:text-red-400">
      {{ projectError }}
    </p>
    <p v-else-if="projects.length === 0" class="py-8 text-center text-gray-500 dark:text-gray-400">
      {{ t('analyticsPage.noProjects') }}
    </p>
    <p v-else-if="isLoadingSummary" class="py-8 text-center text-gray-500 dark:text-gray-400">
      {{ t('analyticsPage.loadingAnalytics') }}
    </p>
    <p v-else-if="summaryError" role="alert" class="py-8 text-center text-red-600 dark:text-red-400">
      {{ summaryError }}
    </p>
    <template v-else-if="summary">
      <MetricCards :summary="summary" @select-group="selectedGroup = $event" @open-builder="openBuilderFilter" />

      <section v-if="selectedSprint" class="mt-6 rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 class="font-semibold text-slate-900 dark:text-white">{{ selectedSprint.name }}</h2>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ t('analyticsPage.plannedAndActual') }}</p>
          </div>
          <p class="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{{ summary.completion_percentage }}% {{ t('analyticsPage.actual') }}</p>
        </div>
        <div class="mt-4 h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
          <div class="relative h-full bg-slate-300 dark:bg-slate-500" :style="{ width: `${plannedProgress}%` }">
            <div class="absolute inset-y-0 left-0 bg-emerald-500" :style="{ width: `${plannedProgress ? Math.min(100, selectedSprint.progress / plannedProgress * 100) : 0}%` }" />
          </div>
        </div>
        <div class="mt-2 flex justify-between text-xs text-slate-500 dark:text-slate-400">
          <span>{{ t('analyticsPage.planned') }} {{ plannedProgress }}%</span>
          <span>{{ summary.completed_tickets }}/{{ summary.total_tickets }} {{ t('analyticsPage.completedTickets') }}</span>
        </div>
      </section>

      <TicketDistribution :summary="summary" :group-filter="selectedGroup" />

      <section class="mt-6 grid gap-6 lg:grid-cols-2">
        <div class="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <div class="flex items-baseline justify-between gap-3">
            <h2 class="font-semibold text-slate-900 dark:text-white">{{ t('analyticsPage.redirectedTickets') }}</h2>
            <span class="text-sm text-amber-600 dark:text-amber-400">{{ summary.redirection_events_count ?? 0 }} {{ t('analyticsPage.events') }}</span>
          </div>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ summary.redirected_tickets ?? 0 }} {{ t('analyticsPage.currentlyRedirected') }}</p>
          <ul v-if="summary.redirection_events?.length" class="mt-4 divide-y divide-slate-100 dark:divide-slate-700">
            <li v-for="event in summary.redirection_events" :key="`${event.ticket_id}-${event.created_at}`" class="py-2 text-sm">
              <span class="font-medium text-slate-800 dark:text-slate-200">{{ event.ticket_title }}</span>
              <span class="ml-2 text-slate-500 dark:text-slate-400">{{ developerName(event.from_user_id) }} → {{ developerName(event.to_user_id) }}</span>
              <span class="ml-2 text-slate-500 dark:text-slate-400">{{ formatEventDate(event.created_at) }}</span>
            </li>
          </ul>
          <p v-else class="mt-4 text-sm text-slate-500 dark:text-slate-400">{{ t('analyticsPage.noRedirections') }}</p>
        </div>

        <div class="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <h2 class="font-semibold text-slate-900 dark:text-white">{{ t('analyticsPage.bottlenecks') }}</h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ t('analyticsPage.bottlenecksDescription') }}</p>
          <div v-if="summary.bottlenecks?.length" class="mt-4 space-y-3">
            <div v-for="item in summary.bottlenecks.slice(0, 4)" :key="item.status">
              <div class="flex justify-between gap-3 text-sm">
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ statusLabel(item.status) }}</span>
                <span class="text-slate-500 dark:text-slate-400">{{ item.ticket_count }} {{ t('reportsPage.tickets').toLowerCase() }} · {{ item.average_hours }} h {{ t('analyticsPage.average') }}</span>
              </div>
              <div class="mt-1 h-2 rounded-full bg-slate-100 dark:bg-slate-700">
                <div class="h-2 rounded-full bg-amber-500" :style="{ width: `${bottleneckWidth(item.ticket_count)}%` }" />
              </div>
            </div>
            <div class="mt-4 border-t border-slate-100 pt-3 dark:border-slate-700">
              <p class="mb-2 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">{{ t('analyticsPage.slowestTickets') }}</p>
              <button
                v-for="ticket in slowestTickets"
                :key="ticket.ticket_id"
                type="button"
                class="flex w-full items-center justify-between gap-3 rounded-md px-2 py-2 text-left text-sm hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:hover:bg-slate-700"
                @click="openBuilderFilter(ticket.status, false, ticket.ticket_id)"
              >
                <span class="min-w-0 truncate font-medium text-slate-800 dark:text-slate-200">{{ ticket.title }}</span>
                <span class="shrink-0 text-xs text-amber-600 dark:text-amber-400">{{ statusLabel(ticket.status) }} · {{ ticket.hours }} h ↗</span>
              </button>
            </div>
          </div>
          <p v-else class="mt-4 text-sm text-slate-500 dark:text-slate-400">{{ t('analyticsPage.noBottlenecks') }}</p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'
import apiClient from '@/services/api'
import MetricCards from '@/components/analytics/MetricCards.vue'
import TicketDistribution from '@/components/analytics/TicketDistribution.vue'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import type { Application, ApplicationSummary, User } from '@/types'
import type { Sprint } from '@/types/sprint'

const authStore = useAuthStore()
const teamsStore = useTeamsStore()
const router = useRouter()
const { t } = useI18n()

const projects = ref<Application[]>([])
const selectedProjectId = ref('')
const developers = ref<User[]>([])
const sprints = ref<Sprint[]>([])
const selectedDeveloperId = ref('')
const selectedSprintId = ref('')
const selectedGroup = ref<'all' | 'completed' | 'pending' | 'overdue' | 'blocked' | 'redirected'>('all')
const summary = ref<ApplicationSummary | null>(null)
const isLoadingProjects = ref(false)
const isLoadingSummary = ref(false)
const projectError = ref('')
const summaryError = ref('')
let summaryRequestId = 0
const selectedSprint = computed(() => sprints.value.find((sprint) => sprint.id === selectedSprintId.value) ?? null)
const slowestTickets = computed(() => (summary.value?.bottlenecks ?? [])
  .flatMap((item) => item.tickets ?? [])
  .sort((a, b) => b.hours - a.hours)
  .slice(0, 5))
const plannedProgress = computed(() => {
  if (!selectedSprint.value) return 0
  const start = new Date(selectedSprint.value.startDate).getTime()
  const end = new Date(selectedSprint.value.endDate).getTime()
  if (!start || !end || end <= start) return 0
  return Math.round(Math.max(0, Math.min(1, (Date.now() - start) / (end - start))) * 100)
})

const normalizeList = <T>(response: unknown): T[] => {
  const payload = (response as { data?: unknown } | null)?.data ?? response
  const items = (payload as { items?: unknown } | null)?.items ?? payload
  return Array.isArray(items) ? items as T[] : []
}

const normalizeRole = (role?: string | null) =>
  String(role ?? '').trim().toUpperCase().replace('USERROLE.', '').replace('-', '_')

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
    projectError.value = error instanceof Error ? error.message : t('analyticsPage.projectLoadError')
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
    const response = await apiClient.get<ApplicationSummary>(`/analytics/summary/${projectId}`, {
      params: {
        assignee_id: selectedDeveloperId.value || undefined,
        sprint_id: selectedSprintId.value || undefined,
      },
    })
    const data = response.data
    if (requestId === summaryRequestId) summary.value = data
  } catch (error) {
    if (requestId === summaryRequestId) {
      summaryError.value = error instanceof Error ? error.message : t('analyticsPage.analyticsLoadError')
    }
  } finally {
    if (requestId === summaryRequestId) isLoadingSummary.value = false
  }
}

const loadProjectOptions = async (projectId: string) => {
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
      api.sprints.list({ applicationId: projectId }),
    ])
    const allUsers = normalizeList<User>(usersResponse)
    const teamEmails = Array.from(memberEmails)
    // Miembros del equipo del proyecto (cualquier rol: el equipo define quién
    // trabaja en el proyecto). Si el proyecto no tiene equipo asignado, se
    // muestra todos los usuarios con rol DEVELOPER como respaldo.
    developers.value = teamEmails.length
      ? allUsers.filter((user) => memberEmails.has(user.email.trim().toLowerCase()))
      : allUsers.filter((user) => normalizeRole(String(user.role)) === 'DEVELOPER')
    sprints.value = sprintResponse
  } catch (error) {
    console.error('No se pudieron cargar desarrolladores o sprints:', error)
  }
}

const openBuilderFilter = (status: string, overdue = false, ticketId?: string) => {
  void router.push({
    path: '/admin/builder',
    query: {
      applicationId: selectedProjectId.value,
      status,
      assigneeId: selectedDeveloperId.value || undefined,
      sprintId: selectedSprintId.value || undefined,
      overdue: overdue ? 'true' : undefined,
      ticketId,
    },
  })
}

const formatEventDate = (value?: string | null) =>
  value ? new Date(value).toLocaleString() : ''

const developerName = (userId?: string | null) =>
  developers.value.find((developer) => developer.id === userId)?.fullName
    || developers.value.find((developer) => developer.id === userId)?.email
    || t('analyticsPage.user')

const statusLabel = (status: string) => t(`analyticsPage.statuses.${status}`)

const bottleneckWidth = (count: number) => {
  const max = Math.max(...(summary.value?.bottlenecks ?? []).map((item) => item.ticket_count), 1)
  return Math.max(8, count / max * 100)
}

watch([selectedProjectId, selectedDeveloperId, selectedSprintId], ([projectId]) => {
  if (projectId) {
    void loadSummary(projectId)
  } else {
    summaryRequestId += 1
    summary.value = null
    isLoadingSummary.value = false
  }
})

watch(selectedProjectId, (projectId) => void loadProjectOptions(projectId))

onMounted(loadProjects)
</script>