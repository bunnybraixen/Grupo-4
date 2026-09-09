<template>
  <div class="flex flex-col min-h-screen bg-[var(--bg-app)]">
    <!-- Header -->
    <AppHeader />

    <!-- Main content -->
    <div class="p-8 flex-1 overflow-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-4xl font-bold text-[var(--text-primary)] mb-2">
        📊 {{ t('analyticsView.title') }}
      </h1>
      <p class="text-[var(--text-secondary)]">
        {{ t('analyticsView.subtitle') }}
      </p>
    </div>

    <!-- Date Range Selector -->
    <div class="mb-6 flex gap-2 items-center bg-[var(--bg-card)] p-4 rounded-xl shadow-sm border border-[var(--border-subtle)]">
      <!-- Filtros scrollables -->
      <div class="flex gap-4 items-center flex-1 overflow-x-auto min-w-0">
        <label class="text-sm font-medium text-[var(--text-secondary)] flex-shrink-0">{{ t('analyticsView.applicationLabel') }}:</label>
        <select
          v-model="selectedLocalAppId"
          @change="handleAppChange"
          class="px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-panel)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] focus:ring-2 focus:ring-[var(--teal)]/20 min-w-[200px]"
        >
          <option value="" disabled v-if="applicationsStore.applications.length === 0">{{ t('analyticsView.loadingApps') }}</option>
          <option value="">— Todas las aplicaciones —</option>
          <option v-for="app in applicationsStore.applications" :key="app.id" :value="app.id">
            {{ app.name }}
          </option>
        </select>

        <label class="ml-4 text-sm font-medium text-[var(--text-secondary)] flex-shrink-0">{{ t('analyticsView.periodLabel') }}:</label>
        <select
          v-model="selectedPeriod"
          class="px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-panel)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] focus:ring-2 focus:ring-[var(--teal)]/20"
        >
          <option value="week">{{ t('analyticsView.thisWeek') }}</option>
          <option value="month">{{ t('analyticsView.thisMonth') }}</option>
          <option value="quarter">{{ t('analyticsView.thisQuarter') }}</option>
          <option value="year">{{ t('analyticsView.thisYear') }}</option>
        </select>

        <button
          @click="refreshAnalytics"
          :disabled="isLoading || !selectedLocalAppId"
          class="flex-shrink-0 px-4 py-2 bg-[var(--lime)] text-[var(--dark-gray)] font-semibold rounded-lg hover:bg-[var(--lime-90)] transition-colors disabled:opacity-50"
        >
          {{ t('analyticsView.refresh') }}
        </button>
      </div>

      <!-- ExportButton fuera del contenedor overflow para que el dropdown sea visible -->
      <div class="flex-shrink-0 relative">
        <ExportButton
          v-if="selectedLocalAppId"
          :report-data="reportData"
          :period="selectedPeriod"
        />
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Team Efficiency (CS-027) -->
      <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--text-secondary)]">{{ t('analyticsView.teamEfficiency') }}</h3>
          <span class="text-2xl">⚡</span>
        </div>
        <div class="flex items-center gap-2 mb-2">
          <div class="text-4xl font-bold text-[var(--teal)]">{{ teamEfficiency }}%</div>
          <span class="w-3 h-3 rounded-full inline-block" :class="efficiencyTrafficLight(teamEfficiency)"></span>
        </div>
        <p class="text-xs text-[var(--text-muted)]">{{ t('analyticsView.completedOnTime') }}</p>
        <div class="mt-4 w-full bg-[var(--bg-panel)] rounded-full h-2">
          <div class="bg-[var(--teal)] rounded-full h-2" :style="{ width: teamEfficiency + '%' }"></div>
        </div>
      </div>

      <!-- Blocking Index (CS-027) -->
      <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--text-secondary)]">{{ t('analyticsView.blockingIndex') }}</h3>
          <span class="text-2xl">🔒</span>
        </div>
        <div class="flex items-center gap-2 mb-2">
          <div class="text-4xl font-bold text-amber-600">{{ blockingIndex }}%</div>
          <span class="w-3 h-3 rounded-full inline-block" :class="blockingTrafficLight(blockingIndex)"></span>
        </div>
        <p class="text-xs text-[var(--text-muted)]">{{ t('analyticsView.blockedTickets') }}</p>
        <div class="mt-4 w-full bg-[var(--bg-panel)] rounded-full h-2">
          <div class="bg-amber-600 rounded-full h-2" :style="{ width: blockingIndex + '%' }"></div>
        </div>
      </div>

      <!-- Redirection Index (CS-027) -->
      <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-[var(--text-secondary)]">{{ t('analyticsView.redirectionIndex') }}</h3>
          <span class="text-2xl">🔀</span>
        </div>
        <div class="flex items-center gap-2 mb-2">
          <div class="text-4xl font-bold text-blue-600">{{ redirectionIndex }}%</div>
          <span class="w-3 h-3 rounded-full inline-block" :class="rotationTrafficLight(redirectionIndex)"></span>
        </div>
        <p class="text-xs text-[var(--text-muted)]">{{ t('analyticsView.redirectedTickets') }}</p>
        <div class="mt-4 w-full bg-[var(--bg-panel)] rounded-full h-2">
          <div class="bg-blue-600 rounded-full h-2" :style="{ width: redirectionIndex + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Tickets de Soporte (siempre visible, no depende de la app seleccionada) -->
    <div class="mb-8 bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-subtle)] p-6">
      <div class="flex items-center justify-between mb-5">
        <h3 class="text-base font-semibold text-[var(--text-primary)]">
          🐛 {{ t('analyticsView.supportTicketsTitle') || 'Tickets de Soporte' }}
        </h3>
        <span class="text-xs text-[var(--text-muted)]">
          {{ supportTotal }} {{ t('analyticsView.supportTotalSuffix') || 'en total' }}
        </span>
      </div>

      <div v-if="supportSummary" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Por estado -->
        <div>
          <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
            {{ t('analyticsView.supportByStatus') || 'Por estado' }}
          </p>
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_status.REPORTED ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]">
                {{ t('supportTicketsView.statusReported') || 'Reportado' }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_status.INVESTIGATING ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--status-progress-bg)] text-[var(--status-progress-text)]">
                {{ t('supportTicketsView.statusInvestigating') || 'En Investigación' }}
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_status.RESOLVED ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--status-done-bg)] text-[var(--status-done-text)]">
                {{ t('supportTicketsView.statusResolved') || 'Resuelto' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Por severidad (solo bugs activos: REPORTED + INVESTIGATING) -->
        <div>
          <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
            {{ t('analyticsView.supportBySeverity') || 'Por severidad (bugs activos)' }}
          </p>
          <div class="flex flex-col gap-2">
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_severity.CRITICAL ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--priority-urg-bg)] text-[var(--priority-urg-text)]">🔴 {{ t('supportTicketsView.severityTextCritical') || 'Crítica' }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_severity.HIGH ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--priority-high-bg)] text-[var(--priority-high-text)]">🟠 {{ t('supportTicketsView.severityTextHigh') || 'Alta' }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_severity.MEDIUM ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--priority-med-bg)] text-[var(--priority-med-text)]">🟡 {{ t('supportTicketsView.severityTextMedium') || 'Media' }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-semibold text-[var(--text-primary)] w-6 text-right">{{ supportSummary.by_severity.LOW ?? 0 }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium bg-[var(--priority-low-bg)] text-[var(--priority-low-text)]">🟢 {{ t('supportTicketsView.severityTextLow') || 'Baja' }}</span>
            </div>
          </div>
        </div>

        <!-- Tiempo promedio de resolución -->
        <div class="flex flex-col justify-center">
          <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3">
            {{ t('analyticsView.supportAvgResolution') || 'Tiempo prom. de resolución' }}
          </p>
          <div class="flex items-baseline gap-2">
            <span class="text-4xl font-bold text-[var(--teal)]">{{ supportSummary.avg_resolution_time_hours }}</span>
            <span class="text-sm text-[var(--text-secondary)]">{{ t('analyticsView.hoursSuffix') || 'horas' }}</span>
          </div>
        </div>
      </div>

      <div v-else class="text-sm text-[var(--text-muted)] text-center py-4">
        {{ t('analyticsView.supportNoData') || 'No hay datos de tickets de soporte.' }}
      </div>
    </div>

    <!-- Hint when no app is selected -->
    <div v-if="!selectedLocalAppId" class="mb-8 p-8 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] text-center">
      <p class="text-[var(--text-secondary)] text-sm">Selecciona una aplicación del selector para ver los datos analíticos.</p>
    </div>

    <!-- Performance Table (CS-031) -->
    <div class="mb-8">
      <PerformanceTable v-if="selectedLocalAppId" :appId="selectedLocalAppId" />
    </div>

    <!-- Burndown Chart (CS-030)-->
    <div class="mb-8">
      <BurndownChart :appId="selectedLocalAppId" v-if="selectedLocalAppId" />
    </div>

    <!-- Weekly Activity Heatmap (CS-029) -->
    <div class="mb-8">
      <Heatmap v-if="selectedLocalAppId" />
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useApplicationsStore } from '@/stores/applications'
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import ExportButton from '@/components/analytics/ExportButton.vue'
import Heatmap from '@/components/analytics/Heatmap.vue'
import BurndownChart from '@/components/analytics/BurndownChart.vue'
import PerformanceTable from '@/components/analytics/PerformanceTable.vue'
import type { AnalyticsReport } from '@/types/analytics'

const { t } = useI18n()

const analyticsStore = useAnalyticsStore()
const applicationsStore = useApplicationsStore()

// ========== STATE ==========
const isLoading = ref(false)
const selectedPeriod = ref<'week' | 'month' | 'quarter' | 'year'>('month')
const selectedLocalAppId = ref('')

// KPI Metrics (CS-031) - Índices calculados desde datos de performance por usuario
const teamEfficiency = computed(() => {
  const perf = analyticsStore.performance
  if (!perf?.length) return 0
  return Math.round(perf.reduce((s, p) => s + (p.efficiency ?? 0), 0) / perf.length)
})

const blockingIndex = computed(() => {
  const perf = analyticsStore.performance
  if (!perf?.length) return 0
  return Math.round(perf.reduce((s, p) => s + (p.blocking_index ?? 0), 0) / perf.length)
})

const redirectionIndex = computed(() => {
  const perf = analyticsStore.performance
  if (!perf?.length) return 0
  return Math.round(perf.reduce((s, p) => s + (p.churn_index ?? 0), 0) / perf.length)
})

// Resumen de tickets de soporte (global, independiente de la app seleccionada)
const supportSummary = computed(() => analyticsStore.supportSummary)
const supportTotal = computed(() => {
  const s = analyticsStore.supportSummary
  if (!s) return 0
  return Object.values(s.by_status).reduce((sum, n) => sum + n, 0)
})

function efficiencyTrafficLight(val: number): string {
  if (val >= 60) return 'bg-green-500'
  if (val >= 30) return 'bg-amber-500'
  return 'bg-red-500'
}
function blockingTrafficLight(val: number): string {
  if (val < 20) return 'bg-green-500'
  if (val <= 40) return 'bg-amber-500'
  return 'bg-red-500'
}
function rotationTrafficLight(val: number): string {
  if (val < 20) return 'bg-green-500'
  if (val <= 40) return 'bg-amber-500'
  return 'bg-red-500'
}

// Report Data for Export (PASO 5)
const reportData = computed<AnalyticsReport>(() => ({
  teamKPIs: {
    efficiencyIndex: teamEfficiency.value,
    blockRate: blockingIndex.value,
    redirectRate: redirectionIndex.value,
  },
  developers: analyticsStore.sortedPerformance.map((dev) => ({
    ...dev,
    avatarInitials: getInitials(dev.userName),
    processedTickets: dev.completedTickets,
    editedTickets: 0,
    questionsRaised: 0,
    redirections: 0,
    avgTimeMinutes: dev.averageHoursPerTicket ? dev.averageHoursPerTicket * 60 : 0,
  })),
  period: selectedPeriod.value,
}))


// ========== METHODS ==========
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'U'
}

const handleAppChange = async () => {
  if (selectedLocalAppId.value) {
    await refreshAnalytics()
  }
}

const refreshAnalytics = async () => {
  if (!selectedLocalAppId.value) {
    console.warn('No app selected')
    return
  }

  isLoading.value = true
  try {
    // Calcula rango de fechas basado en selectedPeriod
    const to = new Date()
    const from = new Date(to)

    switch (selectedPeriod.value) {
      case 'week':
        from.setDate(from.getDate() - 7)
        break
      case 'month':
        from.setDate(from.getDate() - 30)
        break
      case 'quarter':
        from.setDate(from.getDate() - 90)
        break
      case 'year':
        from.setFullYear(from.getFullYear() - 1)
        break
    }

    // Actualiza el rango en el store
    analyticsStore.setDateRange(from, to)

    // Carga todos los datos (summary, performance, heatmap) en paralelo
    await analyticsStore.fetchAllData(selectedLocalAppId.value)
  } catch (error) {
    console.error('Error al cargar analítica:', error)
  } finally {
    isLoading.value = false
  }
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  isLoading.value = true
  try {
    await applicationsStore.fetchAll()

    // Resumen de tickets de soporte: global, no depende de la app seleccionada.
    await analyticsStore.fetchSupportSummary()

    // Autoselecciona la primera aplicación y dispara la carga de analítica,
    // para que los KPIs se muestren sin requerir interacción del usuario.
    if (applicationsStore.applications.length > 0) {
      selectedLocalAppId.value = applicationsStore.applications[0].id
      await refreshAnalytics()
    }
  } catch (error) {
    console.error('Error al inicializar el dashboard:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
/* Smooth transitions for progress bars */
.bg-teal {
  transition: width 0.3s ease;
}
</style>
