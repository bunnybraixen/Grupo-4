<template>
  <div
    :class="[
      'bg-[var(--bg-card)] rounded-lg border border-[var(--border-subtle)] overflow-hidden mb-4 transition-opacity',
      isDraggingEpic ? 'opacity-50 shadow-none' : ''
    ]"
  >
    <!-- Epic drag bar (full-width top strip) -->
    <div
      draggable="true"
      @dragstart="handleEpicDragStart"
      @dragend="handleEpicDragEnd"
      :class="[
        'h-2 w-full cursor-grab active:cursor-grabbing transition-colors',
        isDraggingEpic ? 'bg-[var(--accent-cold-2)]' : 'hover:bg-[var(--accent-cold-2)] bg-transparent'
      ]"
      title="Arrastrar épica"
    />

    <!-- Header -->
    <div
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleTicketDrop"
      :class="[
        'bg-[var(--bg-panel)] p-4 border-b border-[var(--border-color)] transition-colors',
        isDraggingOver ? 'bg-[color-mix(in_srgb,var(--accent-cold-2)_20%,var(--bg-panel))] border-[var(--accent-cold-2)]' : ''
      ]"
    >
      <div class="flex items-center gap-3">

        <!-- Expand/collapse -->
        <button
          @click="isExpanded = !isExpanded"
          class="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        >
          <Icon
            :icon="isExpanded ? 'mdi:chevron-down' : 'mdi:chevron-right'"
            :class="[
              'text-xl transition-transform duration-200',
              isExpanded ? 'rotate-0' : 'rotate-180'
            ]"
          />
        </button>

        <!-- Title -->
        <div class="flex-1 min-w-0">
          <h3 class="text-[var(--text-primary)] font-semibold truncate">{{ epic.title }}</h3>
        </div>

        <!-- Progress bar -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="w-24 h-2 bg-[var(--border-subtle)] rounded-full overflow-hidden">
            <div
              class="h-full bg-[var(--lime)] transition-all duration-300"
              :style="{ width: progressPercentage + '%' }"
            />
          </div>
          <span class="text-xs text-[var(--text-muted)] w-8 text-right">
            {{ progressPercentage }}%
          </span>
        </div>

        <!-- Ticket count -->
        <span class="inline-flex items-center justify-center w-6 h-6 text-xs font-bold bg-[var(--bg-panel)] text-[var(--text-secondary)] rounded-full">
          {{ epic.tickets.length }}
        </span>

        <!-- Documents toggle -->
        <button
          @click="toggleDocuments"
          class="relative text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          :title="`${localDocuments.length} documentos`"
        >
          <Icon icon="mdi:paperclip" class="text-lg" />
          <span
            v-if="localDocuments.length"
            class="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center"
          >
            {{ localDocuments.length }}
          </span>
        </button>
      </div>

      <!-- Documents panel -->
      <div v-if="showDocuments" class="mt-3 pt-3 border-t border-[var(--border-subtle)]">
        <!-- Upload button -->
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-[var(--text-secondary)] font-medium">Documentos adjuntos</span>
          <button
            @click="fileInputRef?.click()"
            :disabled="isUploading"
            class="flex items-center gap-1 px-2 py-1 text-xs bg-[var(--accent-cold-2)] hover:bg-[var(--accent-cold-1)] disabled:opacity-50 text-white rounded transition-colors"
          >
            <Icon :icon="isUploading ? 'mdi:loading' : 'mdi:upload'" :class="isUploading ? 'animate-spin' : ''" />
            {{ isUploading ? 'Subiendo...' : 'Subir' }}
          </button>
        </div>

        <!-- Hidden file input -->
        <input
          ref="fileInputRef"
          type="file"
          class="hidden"
          @change="handleFileSelected"
        />

        <!-- Document list -->
        <div v-if="localDocuments.length" class="grid grid-cols-1 gap-1">
          <div
            v-for="doc in localDocuments"
            :key="doc.id"
            class="flex items-center gap-2 text-xs text-[var(--text-secondary)] bg-[var(--bg-panel)] rounded px-2 py-1"
          >
            <Icon icon="mdi:file" class="text-[var(--text-secondary)] flex-shrink-0" />
            <span class="flex-1 truncate">{{ doc.filename }}</span>
            <span class="text-[var(--text-muted)] flex-shrink-0">{{ formatSize(doc.file_size) }}</span>
            <a
              :href="`/api/documents/${doc.id}/download`"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-400 hover:text-blue-300 flex-shrink-0"
              title="Descargar"
            >
              <Icon icon="mdi:download" />
            </a>
            <button
              @click="removeDocument(doc.id)"
              class="text-red-400 hover:text-red-300 flex-shrink-0"
              title="Eliminar"
            >
              <Icon icon="mdi:trash-can-outline" />
            </button>
          </div>
        </div>
        <p v-else class="text-xs text-[var(--text-muted)] text-center py-1">Sin documentos adjuntos</p>
      </div>
    </div>

    <!-- Ticket list -->
    <div v-show="isExpanded" class="p-4 space-y-2 bg-[var(--bg-app)]">
      <div v-if="epic.tickets.length === 0" class="text-center py-4 text-[var(--text-secondary)]">
        <Icon icon="mdi:inbox-outline" class="text-2xl mx-auto mb-2" />
        <p class="text-sm">No hay tickets en esta épica</p>
      </div>

      <div v-else>
        <TicketCard
          v-for="ticket in epic.tickets"
          :key="ticket.id"
          :ticket="(ticket as any)"
          @select="$emit('selectTicket', ticket)"
          @dragstart="handleTicketDragStart"
          @dragend="$emit('epicDragEnd')"
        />
      </div>

      <!-- Add ticket -->
      <div class="pt-2 border-t border-[var(--border-subtle)] mt-2">
        <button
          v-if="!isAddingTicket"
          @click="isAddingTicket = true"
          class="w-full px-3 py-2 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] rounded transition-colors flex items-center justify-center gap-2"
        >
          <Icon icon="mdi:plus" />
          Agregar Ticket
        </button>

        <div v-else class="flex gap-2">
          <input
            v-model="newTicketTitle"
            @keydown.enter="addNewTicket"
            @keydown.escape="isAddingTicket = false"
            type="text"
            placeholder="Título del ticket..."
            autofocus
            class="flex-1 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent-cold-2)] text-sm"
          />
          <button
            @click="addNewTicket"
            class="px-2 py-2 bg-[var(--lime)] hover:bg-[var(--lime-90)] text-[var(--dark-gray)] rounded transition-colors"
          >
            <Icon icon="mdi:check" />
          </button>
          <button
            @click="isAddingTicket = false"
            class="px-2 py-2 bg-[var(--bg-panel)] hover:bg-[var(--bg-card)] text-[var(--text-primary)] rounded transition-colors"
          >
            <Icon icon="mdi:close" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import TicketCard from './TicketCard.vue'
import { useEpicsStore } from '@/stores/epics'
import { api } from '@/services/api'

// ── Types ──────────────────────────────────────────────────────────────────

interface Ticket {
  id: string
  title: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'REDIRECTED' | 'COMPLETED'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  assignee?: { id: string; name: string; avatar: string }
  dueDate?: string
}

interface Epic {
  id: string
  title: string
  tickets: Ticket[]
  completedTickets?: number
}

interface DocumentItem {
  id: string
  filename: string
  file_size: number
  mime_type: string
  doc_type: string
  epic_id?: string | null
  ticket_id?: string | null
}

// ── Props & emits ──────────────────────────────────────────────────────────

const props = defineProps<{ epic: Epic }>()

const emit = defineEmits<{
  toggleCollapse: [isExpanded: boolean]
  addTicket: [data: { epicId: string; title: string }]
  selectTicket: [ticket: Ticket]
  reorderTickets: [data: { epicId: string; draggedTicketId: string }]
  epicDragStart: [data: any]
  epicDragEnd: []
}>()

// ── Store ──────────────────────────────────────────────────────────────────

const epicsStore = useEpicsStore()

// ── State ──────────────────────────────────────────────────────────────────

const isExpanded = ref(true)
const showDocuments = ref(false)
const isAddingTicket = ref(false)
const newTicketTitle = ref('')
const isDraggingOver = ref(false)
const isDraggingEpic = ref(false)
const localDocuments = ref<DocumentItem[]>([])
const isUploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
let hoverTimeout: number | null = null

// ── Lifecycle ──────────────────────────────────────────────────────────────

onMounted(async () => {
  isExpanded.value = !epicsStore.collapsedEpics.has(props.epic.id)
  await fetchDocuments()
})

watch(isExpanded, (newValue) => {
  if (newValue) epicsStore.expand(props.epic.id)
  else epicsStore.collapse(props.epic.id)
})

// ── Computed ───────────────────────────────────────────────────────────────

const progressPercentage = computed(() => {
  if (props.epic.tickets.length === 0) return 0
  const completed = props.epic.tickets.filter(t => t.status === 'COMPLETED').length
  return Math.round((completed / props.epic.tickets.length) * 100)
})

// ── Document methods ───────────────────────────────────────────────────────

const fetchDocuments = async () => {
  try {
    const docs = await api.documents.list({ epicId: props.epic.id })
    localDocuments.value = docs as unknown as DocumentItem[]
  } catch {
    // non-critical; silently ignore
  }
}

const toggleDocuments = async () => {
  showDocuments.value = !showDocuments.value
  if (showDocuments.value) {
    await fetchDocuments()
  }
}

const handleFileSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  isUploading.value = true
  try {
    const uploaded = await api.documents.upload(file, {
      epicId: props.epic.id,
      docType: 'DOCUMENTATION',
    })
    localDocuments.value.unshift(uploaded as unknown as DocumentItem)
  } catch (err) {
    console.error('Error al subir documento:', err)
  } finally {
    isUploading.value = false
    input.value = ''
  }
}

const removeDocument = async (docId: string) => {
  try {
    await api.documents.delete(docId)
    localDocuments.value = localDocuments.value.filter(d => d.id !== docId)
  } catch (err) {
    console.error('Error al eliminar documento:', err)
  }
}

const formatSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ── Ticket methods ─────────────────────────────────────────────────────────

const addNewTicket = () => {
  if (!newTicketTitle.value.trim()) return
  emit('addTicket', { epicId: props.epic.id, title: newTicketTitle.value })
  newTicketTitle.value = ''
  isAddingTicket.value = false
}

const handleEpicDragStart = () => {
  isDraggingEpic.value = true
  emit('epicDragStart', props.epic)
}

const handleEpicDragEnd = () => {
  isDraggingEpic.value = false
  emit('epicDragEnd')
}

const handleTicketDragStart = (ticket: Ticket) => {
  emit('epicDragStart', { epic: props.epic, ticket })
}

const handleDragOver = () => {
  isDraggingOver.value = true
  if (!isExpanded.value) {
    if (hoverTimeout) clearTimeout(hoverTimeout)
    hoverTimeout = setTimeout(() => {
      isExpanded.value = true
    }, 500) as unknown as number
  }
}

const handleDragLeave = () => {
  isDraggingOver.value = false
  if (hoverTimeout) {
    clearTimeout(hoverTimeout)
    hoverTimeout = null
  }
}

const handleTicketDrop = (event: DragEvent) => {
  isDraggingOver.value = false
  const draggedTicketId = event.dataTransfer?.getData('ticketId')
  if (draggedTicketId) {
    emit('reorderTickets', { epicId: props.epic.id, draggedTicketId })
  }
}
</script>

<style scoped>
.rotate-180 {
  transform: rotate(-180deg);
}
.rotate-0 {
  transform: rotate(0deg);
}
</style>
