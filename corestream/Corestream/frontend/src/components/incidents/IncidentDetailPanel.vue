<script setup lang="ts">
import { ref } from 'vue'
import type { Incident } from '@/types/incidents'

const props = defineProps<{ incident: Incident | null }>()
const emit = defineEmits(['close', 'update-status', 'assign', 'resolve', 'add-comment'])
const resolutionNotes = ref('')
</script>

<template>
  <aside v-if="incident" class="h-full w-full bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-700 p-5 shadow-xl">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Detalle del incidente</h3>
      <button
        class="px-2 py-1 text-sm text-slate-500 hover:text-slate-900 dark:hover:text-white"
        @click="emit('close')"
      >Cerrar</button>
    </div>

    <div class="space-y-3 text-sm text-slate-700 dark:text-slate-200">
      <div>
        <p class="text-xs uppercase tracking-wide text-slate-500">Título</p>
        <p class="font-semibold">{{ incident.title }}</p>
      </div>

      <div>
        <p class="text-xs uppercase tracking-wide text-slate-500">Estado</p>
        <p>{{ incident.status }}</p>
      </div>

      <div>
        <p class="text-xs uppercase tracking-wide text-slate-500">Severidad</p>
        <p>{{ incident.severity }}</p>
      </div>

      <div v-if="incident.description">
        <p class="text-xs uppercase tracking-wide text-slate-500">Descripción</p>
        <p>{{ incident.description }}</p>
      </div>
    </div>

    <div class="mt-6 flex flex-wrap gap-2">
      <button
        class="px-3 py-2 rounded-lg bg-blue-600 text-white text-sm"
        @click="emit('update-status', incident.id, 'IN_PROGRESS')"
      >Marcar en progreso</button>
      <button
        class="px-3 py-2 rounded-lg bg-green-600 text-white text-sm disabled:opacity-50"
        :disabled="!resolutionNotes.trim()"
        @click="emit('resolve', incident.id, resolutionNotes.trim()); resolutionNotes = ''"
      >Resolver</button>
    </div>
    <textarea
      v-model="resolutionNotes"
      rows="3"
      placeholder="Notas de resolución requeridas..."
      class="mt-3 w-full rounded-lg border border-slate-300 bg-white p-2 text-sm text-slate-900 outline-none focus:border-green-500 dark:border-slate-700 dark:bg-slate-950 dark:text-white"
    />
  </aside>
</template>
