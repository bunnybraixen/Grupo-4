<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Carril de Épica (Swimlane) -->
  <!-- ================================================================ -->
  <!-- Representa una épica con sus tickets asociados en un carril -->
  <!-- Soporta: colapsar/expandir, arrastrar y soltar, adjuntar documentos -->
  <!-- Muestra barra de progreso, contador de tickets y documentos -->
  <!-- ================================================================ -->

  <div class="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden mb-4">
    <!-- ================================================================ -->
    <!-- SECCIÓN: Encabezado del Carril -->
    <!-- ================================================================ -->
    <!-- Título, progreso, contador de tickets, documentos y controles -->
    <!-- ================================================================ -->
    <div
      @dragover.prevent="isDraggingOver = true"
      @dragleave="isDraggingOver = false"
      @drop.prevent="handleTicketDrop"
      :class="[
        'bg-slate-750 p-4 border-b border-slate-700 transition-colors',
        isDraggingOver ? 'bg-blue-900 border-blue-500' : ''
      ]"
    >
      <div class="flex items-center gap-3">
        <!-- Icono de arrastre (6 puntos) -->
        <div
          draggable="true"
          @dragstart="$emit('epicDragStart', epic)"
          @dragend="$emit('epicDragEnd')"
          class="cursor-grab active:cursor-grabbing text-slate-400 hover:text-slate-300 transition-colors"
        >
          <Icon icon="mdi:drag-vertical" class="text-xl" />
        </div>

        <!-- Botón de expandir/contraer épica -->
        <button
          @click="isExpanded = !isExpanded"
          class="text-slate-400 hover:text-white transition-colors"
        >
          <Icon
            :icon="isExpanded ? 'mdi:chevron-down' : 'mdi:chevron-right'"
            class="text-xl"
          />
        </button>

        <!-- Título de la épica -->
        <div class="flex-1 min-w-0">
          <h3 class="text-white font-semibold truncate">{{ epic.title }}</h3>
        </div>

        <!-- Barra de progreso: porcentaje completado -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              class="h-full bg-green-500 transition-all duration-300"
              :style="{ width: progressPercentage + '%' }"
            />
          </div>
          <span class="text-xs text-slate-300 w-8 text-right">
            {{ progressPercentage }}%
          </span>
        </div>

        <!-- Contador de tickets -->
        <span class="inline-flex items-center justify-center w-6 h-6 text-xs font-bold bg-slate-700 text-slate-200 rounded-full">
          {{ epic.tickets.length }}
        </span>

        <!-- Icono de documentos adjuntos -->
        <button
          @click="showDocuments = !showDocuments"
          class="relative text-slate-400 hover:text-white transition-colors"
          :title="`${epic.attachedDocuments?.length || 0} documentos`"
        >
          <Icon icon="mdi:paperclip" class="text-lg" />
          <span
            v-if="epic.attachedDocuments?.length"
            class="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-xs rounded-full flex items-center justify-center"
          >
            {{ epic.attachedDocuments.length }}
          </span>
        </button>
      </div>

      <!-- ================================================================ -->
      <!-- SUB-SECCIÓN: Información de Documentos (desplegable) -->
      <!-- ================================================================ -->
      <div v-if="showDocuments && epic.attachedDocuments?.length" class="mt-3 pt-3 border-t border-slate-700">
        <div class="grid grid-cols-2 gap-2">
          <a
            v-for="doc in epic.attachedDocuments"
            :key="doc.id"
            :href="doc.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs text-blue-400 hover:text-blue-300 truncate flex items-center gap-1"
          >
            <Icon icon="mdi:file" />
            {{ doc.name }}
          </a>
        </div>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Lista de Tickets (expandible) -->
    <!-- ================================================================ -->
    <!-- Renderiza todos los tickets del carril cuando está expandido -->
    <!-- ================================================================ -->
    <div
      v-show="isExpanded"
      class="p-4 space-y-2 bg-slate-900"
    >
      <!-- Lista de tickets -->
      <div v-if="epic.tickets.length === 0" class="text-center py-4 text-slate-400">
        <Icon icon="mdi:inbox-outline" class="text-2xl mx-auto mb-2" />
        <p class="text-sm">No hay tickets en esta épica</p>
      </div>

      <div v-else>
        <TicketCard
          v-for="ticket in epic.tickets"
          :key="ticket.id"
          :ticket="ticket"
          @select="$emit('selectTicket', ticket)"
          @dragstart="handleTicketDragStart"
          @dragend="$emit('epicDragEnd')"
        />
      </div>

      <!-- ================================================================ -->
      <!-- SUB-SECCIÓN: Botón para agregar nuevo ticket -->
      <!-- ================================================================ -->
      <!-- Input en línea para crear nuevo ticket -->
      <!-- ================================================================ -->
      <div class="pt-2 border-t border-slate-700 mt-2">
        <button
          v-if="!isAddingTicket"
          @click="isAddingTicket = true"
          class="w-full px-3 py-2 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded transition-colors flex items-center justify-center gap-2"
        >
          <Icon icon="mdi:plus" />
          Agregar Ticket
        </button>

        <!-- Input en línea para nuevo ticket -->
        <div v-else class="flex gap-2">
          <input
            v-model="newTicketTitle"
            @keydown.enter="addNewTicket"
            @keydown.escape="isAddingTicket = false"
            type="text"
            placeholder="Título del ticket..."
            autofocus
            class="flex-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 text-sm"
          />
          <button
            @click="addNewTicket"
            class="px-2 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
          >
            <Icon icon="mdi:check" />
          </button>
          <button
            @click="isAddingTicket = false"
            class="px-2 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors"
          >
            <Icon icon="mdi:close" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import TicketCard from './TicketCard.vue'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Ticket {
  id: string
  title: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  assignee?: { id: string; name: string; avatar: string }
  dueDate?: string
}

interface Document {
  id: string
  name: string
  url: string
}

interface Epic {
  id: string
  title: string
  tickets: Ticket[]
  attachedDocuments?: Document[]
  completedTickets?: number
}

// =====================================================================
// PROPS
// =====================================================================

// Objeto épica con todos sus datos
const props = defineProps<{
  epic: Epic
}>()

// =====================================================================
// ESTADO LOCAL (COMPOSABLE)
// =====================================================================

// Control de expansión del carril
const isExpanded = ref(true)

// Control de mostrar lista de documentos
const showDocuments = ref(false)

// Control de creación de nuevo ticket
const isAddingTicket = ref(false)

// Título del nuevo ticket siendo creado
const newTicketTitle = ref('')

// Control visual de drag-over para Drop Zone
const isDraggingOver = ref(false)

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Calcula el porcentaje de tickets completados
 * Basado en tickets con status DONE dividido total de tickets
 */
const progressPercentage = computed(() => {
  if (props.epic.tickets.length === 0) return 0
  
  const completedCount = props.epic.tickets.filter(
    t => t.status === 'DONE'
  ).length
  
  return Math.round((completedCount / props.epic.tickets.length) * 100)
})

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Agrega un nuevo ticket a la épica
 * Valida que el título no esté vacío
 * Emite evento y limpia formulario
 */
const addNewTicket = () => {
  // Validación: título no vacío
  if (newTicketTitle.value.trim().length === 0) {
    return
  }

  // Emitir evento para crear ticket
  emit('addTicket', {
    epicId: props.epic.id,
    title: newTicketTitle.value
  })

  // Limpiar estado
  newTicketTitle.value = ''
  isAddingTicket.value = false
}

/**
 * Maneja el inicio de arrastre de un ticket
 * Propaga evento hacia componente padre
 */
const handleTicketDragStart = (ticket: Ticket) => {
  emit('epicDragStart', { epic: props.epic, ticket })
}

/**
 * Maneja el drop de un ticket sobre el carril
 * Actualiza el orden de tickets dentro de la épica
 */
const handleTicketDrop = (event: DragEvent) => {
  isDraggingOver.value = false
  
  // Obtener datos del ticket siendo arrastrado
  const draggedTicketId = event.dataTransfer?.getData('ticketId')
  
  if (draggedTicketId) {
    // Emitir evento de reorden
    emit('reorderTickets', {
      epicId: props.epic.id,
      draggedTicketId
    })
  }
}

// =====================================================================
// EMITS
// =====================================================================

// Define eventos emitidos por el componente
const emit = defineEmits<{
  toggleCollapse: [isExpanded: boolean]
  addTicket: [data: { epicId: string; title: string }]
  selectTicket: [ticket: Ticket]
  reorderTickets: [data: { epicId: string; draggedTicketId: string }]
  epicDragStart: [data: any]
  epicDragEnd: []
  uploadDoc: [data: { epicId: string; file: File }]
}>()
</script>

<style scoped>
/* Transiciones suaves para expansión */
.transition-all {
  transition: all 0.3s ease;
}
</style>
