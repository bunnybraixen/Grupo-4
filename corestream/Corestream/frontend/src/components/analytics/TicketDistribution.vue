<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ t('ticketDistribution.byStatus') }}{{ groupLabel ? ` · ${groupLabel}` : '' }}
      </h3>
      <Bar :data="statusChart" :options="options" />
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        {{ t('ticketDistribution.byPriority') }}{{ groupLabel ? ` · ${groupLabel}` : '' }}
      </h3>
      <Bar :data="priorityChart" :options="options" />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TicketDistribution: gráficos de barras con la cantidad de tickets
 * por estado y por prioridad (datos de GET /api/analytics/summary/{app_id}).
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
} from 'chart.js'
import type { ApplicationSummary } from '@/types'

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const { t } = useI18n()

const props = defineProps<{
  summary: ApplicationSummary | null
  groupFilter?: 'all' | 'completed' | 'pending' | 'overdue' | 'blocked' | 'redirected'
}>()
const summary = computed(() => props.summary)
const groupFilter = computed(() => props.groupFilter ?? 'all')
const groupLabel = computed(() => {
  if (groupFilter.value === 'all') return ''
  return t(`ticketDistribution.groups.${groupFilter.value}`) || ''
})

const statusKeys = ['TODO', 'IN_PROGRESS', 'BLOCKED', 'REDIRECTED', 'DONE'] as const
const priorityKeys = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const

const statusChart = computed(() => {
  const data = groupFilter.value === 'all'
    ? summary.value?.by_status ?? {}
    : groupFilter.value === 'overdue'
      ? summary.value?.overdue_by_status ?? {}
      : summary.value?.by_group_status?.[groupFilter.value] ?? {}
  return {
    labels: statusKeys.map((k) => t(`ticketDistribution.statuses.${k}`)),
    datasets: [
      {
        label: t('ticketDistribution.tickets'),
        data: statusKeys.map((k) => data[k] ?? 0),
        backgroundColor: ['#9ca3af', '#3b82f6', '#f97316', '#a855f7', '#22c55e']
      }
    ]
  }
})

const priorityChart = computed(() => {
  const data = groupFilter.value === 'all'
    ? summary.value?.by_priority ?? {}
    : summary.value?.by_group_priority?.[groupFilter.value] ?? {}
  return {
    labels: priorityKeys.map((k) => t(`ticketDistribution.priorities.${k}`)),
    datasets: [
      {
        label: t('ticketDistribution.tickets'),
        data: priorityKeys.map((k) => data[k] ?? 0),
        backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444']
      }
    ]
  }
})

const options = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
}
</script>
