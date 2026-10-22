<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
    <article
      v-for="metric in metrics"
      :key="metric.key"
      role="button"
      tabindex="0"
      class="relative rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800"
      @click="emit('selectGroup', metric.group)"
      @keydown.enter="emit('selectGroup', metric.group)"
      @keydown.space.prevent="emit('selectGroup', metric.group)"
    >
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ metric.label }}</p>
          <p class="mt-2 text-3xl font-bold" :class="metric.color">{{ metric.value }}</p>
          <p v-if="metric.key === 'completed'" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {{ t('metricCards.remainingToComplete', { count: Math.max(0, summary.total_tickets - summary.completed_tickets) }) }}
          </p>
          <p v-else-if="metric.key === 'blocked'" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {{ t('metricCards.ofTotal', { percentage: summary.blocked_percentage }) }}
          </p>
          <p v-else-if="metric.key === 'overdue'" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {{ t('metricCards.pastDeadline') }}
          </p>
          <p v-else-if="metric.key === 'redirected'" class="mt-2 text-xs text-slate-500 dark:text-slate-400">
            {{ t('metricCards.redirectionEvents', { count: summary.redirection_events_count ?? 0 }) }}
          </p>
        </div>
        <div
          v-if="metric.key === 'completed'"
          class="grid h-14 w-14 shrink-0 place-items-center rounded-full"
          :style="{ background: `conic-gradient(#22c55e ${summary.completion_percentage}%, #e2e8f0 0)` }"
          :aria-label="t('metricCards.completedPct', { pct: summary.completion_percentage })"
        >
          <div class="grid h-10 w-10 place-items-center rounded-full bg-white text-xs font-bold text-emerald-700 dark:bg-slate-800 dark:text-emerald-300">
            {{ Math.round(summary.completion_percentage) }}%
          </div>
        </div>
      </div>
      <button
        type="button"
        class="absolute bottom-4 right-4 grid h-8 w-8 place-items-center rounded-md text-slate-500 transition hover:bg-slate-100 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:hover:bg-slate-700 dark:hover:text-blue-300"
        :aria-label="t('metricCards.openInBuilder', { label: metric.builderLabel })"
        :title="t('metricCards.openInBuilder', { label: metric.builderLabel })"
        @click.stop="emit('openBuilder', metric.status, metric.key === 'overdue')"
      >
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path d="M7 17 17 7M8 7h9v9" />
        </svg>
      </button>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationSummary } from '@/types'

const { t } = useI18n()

type MetricGroup = 'all' | 'completed' | 'pending' | 'overdue' | 'blocked' | 'redirected'

const props = defineProps<{ summary: ApplicationSummary }>()
const emit = defineEmits<{
  selectGroup: [group: MetricGroup]
  openBuilder: [status: string, overdue: boolean]
}>()

const summary = computed(() => props.summary)
const metrics = computed(() => [
  { key: 'total', label: t('metricCards.totalTickets'), value: summary.value.total_tickets, group: 'all' as MetricGroup, status: 'all', builderLabel: t('metricCards.ofProject'), color: 'text-slate-900 dark:text-white' },
  { key: 'completed', label: t('metricCards.completed'), value: summary.value.completed_tickets, group: 'completed' as MetricGroup, status: 'DONE', builderLabel: t('metricCards.completedLabel'), color: 'text-emerald-600 dark:text-emerald-400' },
  { key: 'pending', label: t('metricCards.pending'), value: summary.value.pending_tickets, group: 'pending' as MetricGroup, status: 'PENDING', builderLabel: t('metricCards.pendingLabel'), color: 'text-blue-600 dark:text-blue-400' },
  { key: 'overdue', label: t('metricCards.overdue'), value: summary.value.overdue_tickets, group: 'overdue' as MetricGroup, status: 'PENDING', builderLabel: t('metricCards.overdueLabel'), color: 'text-red-600 dark:text-red-400' },
  { key: 'blocked', label: t('metricCards.blocked'), value: summary.value.blocked_tickets, group: 'blocked' as MetricGroup, status: 'BLOCKED', builderLabel: t('metricCards.blockedLabel'), color: 'text-orange-600 dark:text-orange-400' },
  { key: 'redirected', label: t('metricCards.redirected'), value: summary.value.redirected_tickets ?? 0, group: 'redirected' as MetricGroup, status: 'REDIRECTED', builderLabel: t('metricCards.redirectedLabel'), color: 'text-amber-600 dark:text-amber-400' },
  { key: 'avgTime', label: t('metricCards.avgTime'), value: `${summary.value.avg_time_hours ?? 0} h`, group: 'all' as MetricGroup, status: 'all', builderLabel: t('metricCards.ofProject'), color: 'text-violet-600 dark:text-violet-400' },
])
</script>
