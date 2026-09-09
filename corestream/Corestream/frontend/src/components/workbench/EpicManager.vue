<template>
  <div class="p-6">
    <div v-if="!showForm" class="mb-6">
      <button
        @click="showForm = true"
        class="w-full py-4 border-2 border-dashed border-[var(--border-subtle)] rounded-xl text-[var(--text-muted)] hover:border-[var(--teal)] hover:text-[var(--teal)] transition-all font-medium"
      >
        + Añadir nueva Épica al Proyecto
      </button>
    </div>

    <div v-else class="bg-[var(--bg-card)] p-4 rounded-xl border border-[var(--teal)]/50 mb-6 shadow-2xl">
      <input
        v-model="newEpicTitle"
        @keyup.enter="saveEpic"
        placeholder="Nombre de la épica..."
        class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 text-[var(--text-primary)] mb-3 outline-none"
        autofocus
      />
      <div class="flex gap-2">
        <button @click="saveEpic" class="bg-[var(--teal)] hover:bg-[var(--teal-90)] text-[var(--text-primary)] px-4 py-1.5 rounded-lg text-sm">Guardar</button>
        <button @click="showForm = false" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
      </div>
    </div>

    <div v-if="epicsStore.isLoading" class="text-center py-12 text-[var(--text-muted)]">
      Cargando épicas...
    </div>

    <div v-else-if="epicsStore.error" class="text-center py-8 text-red-400 text-sm">
      {{ epicsStore.error }}
    </div>

    <div v-else-if="epicsStore.withProgress.length === 0" class="text-center py-12 text-[var(--text-muted)]">
      No hay épicas para este proyecto. Crea la primera.
    </div>

    <div v-else class="space-y-4" data-epic-manager>
      <EpicSwimlane
        v-for="epic in epicsStore.withProgress"
        :key="epic.id"
        :epic="epic"
        @reorder="reorderEpics"
        @select-ticket="$emit('ticketSelected', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, provide } from 'vue'
// @ts-ignore
import EpicSwimlane from './EpicSwimlane.vue'
import { useEpicsStore } from '@/stores/epics'
import { useTicketsStore } from '@/stores/tickets'

const props = defineProps({
  applicationId: { type: String, required: true }
})

const emit = defineEmits(['ticketSelected'])

const epicsStore = useEpicsStore()
const ticketsStore = useTicketsStore()
const showForm = ref(false)
const newEpicTitle = ref('')

const fetchEpics = async () => {
  if (!props.applicationId) return
  try {
    await epicsStore.fetchByApp(props.applicationId)
  } catch (err) {
    console.error('Error cargando épicas:', err)
  }
}

const saveEpic = async () => {
  if (!newEpicTitle.value.trim()) return
  try {
    await epicsStore.create({
      applicationId: props.applicationId,
      title: newEpicTitle.value.trim(),
    })
    newEpicTitle.value = ''
    showForm.value = false
  } catch (err) {
    console.error('Error al guardar épica:', err)
  }
}

const reorderEpics = async (draggedId: string, targetId: string) => {
  const epics = epicsStore.withProgress
  const fromIndex = epics.findIndex(e => e.id === draggedId)
  const toIndex = epics.findIndex(e => e.id === targetId)

  if (fromIndex === -1 || toIndex === -1 || fromIndex === toIndex) return

  epicsStore.reorderLocal(fromIndex, toIndex)

  try {
    await epicsStore.persistEpicReorder(draggedId)
  } catch (err) {
    console.error('Error al persistir reorden de épicas:', err)
  }
}

const createTicket = async (epicId: string, title: string) => {
  // Antes esto solo actualizaba el mapa de progreso (associatedTickets), que no es
  // lo que lee la plantilla (epic.tickets) — el ticket nuevo no aparecía hasta
  // recargar la página. Recargamos la épica completa para mantener todo en sync.
  await ticketsStore.create({ epicId, title })
  await fetchEpics()
}

provide('reorderEpics', reorderEpics)
provide('createTicket', createTicket)

watch(() => props.applicationId, fetchEpics, { immediate: true })
</script>

