<script setup lang="ts">
import type { Incident } from '@/types/incidents'

const props = defineProps<{
  title: string
  count: number
  incidents: Incident[]
  dotClass?: string
  headerClass?: string
  defaultOpen?: boolean
  canResolve?: boolean
}>()

const emit = defineEmits(['select', 'action'])
</script>

<template>
  <section class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
    <div class="mb-3 flex items-center justify-between border-b border-slate-200 pb-2 dark:border-slate-700">
      <div class="flex items-center gap-2">
        <span :class="['h-2.5 w-2.5 rounded-full', props.dotClass || 'bg-blue-500']" />
        <h2 class="text-base font-semibold text-slate-800 dark:text-white">{{ title }}</h2>
      </div>
      <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-300">
        {{ count }}
      </span>
    </div>

    <div class="space-y-3">
      <div
        v-for="incident in incidents"
        :key="incident.id"
        :id="`incident-${incident.id}`"
        class="cursor-pointer rounded-lg border border-slate-200 p-3 transition hover:border-blue-300 hover:bg-blue-50 dark:border-slate-700 dark:hover:border-blue-600 dark:hover:bg-slate-800"
        @click="emit('select', incident)"
      >
        <div class="flex items-center justify-between gap-2">
          <p class="font-medium text-slate-800 dark:text-white">{{ incident.title }}</p>
          <span class="text-xs uppercase text-slate-500">{{ incident.severity }}</span>
        </div>
        <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ incident.status }}</p>
        <div class="mt-3 flex flex-wrap gap-2">
          <button v-if="incident.status === 'OPEN' || incident.status === 'REOPENED'" type="button" class="rounded-md bg-blue-600 px-2.5 py-1 text-xs font-medium text-white" @click.stop="emit('action', incident.id, 'start')">Iniciar</button>
          <button v-if="incident.status === 'IN_PROGRESS'" type="button" class="rounded-md bg-amber-600 px-2.5 py-1 text-xs font-medium text-white" @click.stop="emit('action', incident.id, 'review')">Enviar a revisión</button>
          <button v-if="incident.status === 'UNDER_REVIEW' && canResolve" type="button" class="rounded-md bg-emerald-600 px-2.5 py-1 text-xs font-medium text-white" @click.stop="emit('action', incident.id, 'resolve')">Resolver</button>
          <button v-if="incident.status === 'RESOLVED' || incident.status === 'CLOSED'" type="button" class="rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-700 dark:border-slate-600 dark:text-slate-200" @click.stop="emit('action', incident.id, 'reopen')">Reabrir</button>
        </div>
      </div>
    </div>
  </section>
</template>
