<template>
  <div 
    class="mb-6 border rounded-xl overflow-hidden shadow-lg transition-all duration-200"
    :class="[
      getDragClasses(epic.id),
      isDragging && dragType === 'epic' ? 'border-dashed border-[var(--teal)]/50' : '',
      epic.progress >= 75 ? 'bg-[var(--status-done-bg)]/20 border-[var(--status-done-bg)]' :
      epic.progress >= 50 ? 'bg-amber-900/20 border-amber-700' :
      epic.progress >= 25 ? 'bg-[var(--teal)]/20 border-[var(--teal)]' :
      'bg-[var(--bg-card)]/50 border-[var(--border-subtle)]'
    ]"
    @dragover="handleEpicDragOver($event)"
    @dragenter="dragEnter($event, epic.id)"
    @dragleave="dragLeave"
    @drop="handleEpicDrop"
  >
    
    <!-- Epic Header con mejoras del wireframe -->
    <div 
      @click="toggleCollapse"
      class="p-4 flex items-center justify-between cursor-pointer hover:bg-[var(--bg-panel)]/30 transition-all"
    >
      <div class="flex items-center gap-3">
        <!-- Drag Handle mejorado -->
        <div class="flex items-center gap-1">
          <div class="w-1 h-1 bg-[var(--text-muted)] rounded-full"></div>
          <div class="w-1 h-1 bg-[var(--text-muted)] rounded-full"></div>
          <div class="w-1 h-1 bg-[var(--text-muted)] rounded-full"></div>
        </div>
        
        <span 
          class="text-[var(--text-muted)] hover:text-[var(--teal)] cursor-grab active:cursor-grabbing p-2 text-lg select-none"
          draggable="true"
          @dragstart="handleEpicDragStart($event)"
          @dragend="dragEnd"
        >
          ⠿
        </span>
        
        <!-- Epic Title con icono de estado -->
        <div class="flex items-center gap-2">
          <span 
            class="w-2.5 h-2.5 rounded-full"
            :class="[
              epic.progress >= 75 ? 'bg-[var(--status-done-bg)]' :
              epic.progress >= 50 ? 'bg-amber-500' :
              epic.progress >= 25 ? 'bg-[var(--teal)]' :
              'bg-[var(--text-muted)]'
            ]"
          ></span>
          <h3 class="font-bold text-[var(--text-primary)] text-lg">{{ epic.title }}</h3>
        </div>
        
        <!-- Botones de acción -->
        <div class="flex items-center gap-2">
          <button 
            @click.stop="attachDocument"
            class="text-[var(--text-muted)] hover:text-[var(--teal)] text-sm p-1"
            title="Adjuntar documentos"
          >
            📎
          </button>
          <button 
            @click.stop="toggleCollapse"
            class="text-[var(--text-muted)] hover:text-[var(--teal)] text-sm"
            :title="isCollapsed ? 'Expandir' : 'Colapsar'"
          >
            {{ isCollapsed ? '▶' : '▼' }}
          </button>
        </div>
      </div>

      <!-- Progress Bar mejorada -->
      <div class="flex items-center gap-3 w-1/3">
        <div class="flex-1 bg-[var(--bg-app)] h-2.5 rounded-full border border-[var(--border-subtle)] overflow-hidden">
          <div 
            class="h-full transition-all duration-700 ease-out rounded-full" 
            :class="[
              epic.progress >= 75 ? 'bg-gradient-to-r from-emerald-600 to-emerald-500' :
              epic.progress >= 50 ? 'bg-gradient-to-r from-amber-600 to-amber-500' :
              epic.progress >= 25 ? 'bg-gradient-to-r from-blue-600 to-blue-500' :
              'bg-gradient-to-r from-slate-600 to-slate-500'
            ]"
            :style="{ width: (epic.progress || 0) + '%' }"
          ></div>
        </div>
        <span 
          class="text-xs font-mono w-12 text-right font-medium"
          :class="[
            epic.progress >= 75 ? 'text-[var(--status-done-bg)]' :
            epic.progress >= 50 ? 'text-amber-400' :
            epic.progress >= 25 ? 'text-[var(--teal)]' :
            'text-[var(--text-muted)]'
          ]"
        >
          {{ Math.round(epic.progress || 0) }}%
        </span>
      </div>
    </div>

    <transition name="fade">
      <div v-if="!isCollapsed" class="border-t border-[var(--border-subtle)]">
        <!-- Description Section -->
        <div class="p-4 bg-[var(--bg-app)]/20">
          <p class="text-sm text-[var(--text-muted)] italic mb-4">
            {{ epic.description || 'Sin descripción detallada.' }}
          </p>
          
          <!-- Documentos adjuntos mejorados -->
          <div v-if="epic.documents && epic.documents.length > 0" class="mb-4">
            <div class="text-xs text-slate-500 mb-3 font-medium">📄 Documentos adjuntos:</div>
            <div class="grid grid-cols-1 gap-2">
              <div 
                v-for="doc in epic.documents" 
                :key="doc.id"
                class="bg-[var(--bg-card)] px-3 py-2 rounded-lg text-xs text-[var(--text-secondary)] border border-slate-600 flex items-center justify-between hover:bg-slate-700/50 transition-all"
              >
                <div class="flex items-center gap-2">
                  <span class="text-base">📄</span>
                  <span>{{ doc.name }}</span>
                </div>
                <span class="text-slate-500 text-xs">{{ doc.size || '1 MB' }}</span>
              </div>
            </div>
          </div>
          
          <!-- Lista de tickets de la épica -->
          <div v-if="epicTickets.length > 0" class="space-y-2 mb-4">
            <WorkbenchTicketCard
              v-for="ticket in epicTickets"
              :key="ticket.id"
              :ticket="ticket"
              @select="$emit('selectTicket', ticket)"
            />
          </div>

          <!-- Ticket Drop Zone mejorada -->
          <div
            v-if="!isCreatingTicket"
            class="min-h-[120px] border-2 border-dashed rounded-lg flex flex-col items-center justify-center transition-all duration-200 cursor-pointer"
            :class="[
              dragOverTarget === 'tickets-' + epic.id
                ? 'border-[var(--teal)] bg-[var(--teal)]/10 text-[var(--teal)] scale-[1.02]'
                : 'border-slate-600 bg-[var(--bg-card)]/30 text-slate-500 hover:border-slate-500 hover:bg-slate-700/20'
            ]"
            @dragover.prevent="dragOver($event, 'tickets-' + epic.id)"
            @drop="handleTicketDrop"
            @click="startCreatingTicket"
          >
            <div class="text-center">
              <div class="w-8 h-8 mx-auto mb-3 rounded-full bg-slate-700 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <span class="text-sm font-medium mb-1">Arrastra tickets aquí</span>
              <span class="text-xs opacity-75"> o haz clic para agregar</span>
            </div>
          </div>

          <!-- Formulario inline de creación de ticket -->
          <div
            v-else
            class="rounded-lg p-4 border-2 border-dashed border-[var(--teal)] bg-[var(--bg-card)]/30"
          >
            <input
              ref="newTicketInputEl"
              v-model="newTicketTitle"
              type="text"
              placeholder="Título del ticket..."
              class="w-full px-3 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-panel)] text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)] focus:ring-1 focus:ring-[var(--teal)]"
              @keydown.enter="saveNewTicket"
              @keydown.esc="cancelCreatingTicket"
              @blur="saveNewTicket"
            />
            <p class="text-xs mt-2 text-[var(--text-muted)]">↵ Enter para crear • Esc para cancelar</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, inject, computed, nextTick } from 'vue'
import { useDragDrop } from '@/composables/useDragDrop'
import { useTicketsStore } from '@/stores/tickets'
import { api } from '@/services/api'
import WorkbenchTicketCard from './WorkbenchTicketCard.vue'

// Definimos las propiedades que recibe del padre (EpicManager)
const props = defineProps({
  epic: {
    type: Object,
    required: true // Necesitamos el objeto épica completo que viene del backend
  }
});

const emit = defineEmits(['reorder', 'selectTicket'])

const { 
  dragStart, 
  dragEnd, 
  dragOver, 
  dragEnter, 
  dragLeave, 
  drop, 
  getDragClasses,
  dragOverTarget,
  isDragging,
  dragType
} = useDragDrop()

const ticketsStore = useTicketsStore()
const reorderEpics = inject('reorderEpics')
const createTicket = inject('createTicket')

// Estado local para controlar si el acordeón está abierto o cerrado
// Inicializamos con el valor que viene de la BD (is_collapsed)
const isCollapsed = ref(props.epic.collapsed || false);

const epicTickets = computed(() => props.epic.tickets || [])

// Estado local del formulario inline de creación de ticket
const isCreatingTicket = ref(false)
const newTicketTitle = ref('')
const newTicketInputEl = ref(null)

const startCreatingTicket = () => {
  isCreatingTicket.value = true
  nextTick(() => newTicketInputEl.value?.focus())
}

const cancelCreatingTicket = () => {
  isCreatingTicket.value = false
  newTicketTitle.value = ''
}

const saveNewTicket = async () => {
  const title = newTicketTitle.value.trim()
  if (!title) {
    cancelCreatingTicket()
    return
  }
  try {
    if (createTicket) {
      await createTicket(props.epic.id, title)
    }
  } catch (err) {
    console.error('Error al crear ticket:', err)
  } finally {
    cancelCreatingTicket()
  }
}

// Función para colapsar/expandir
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

// Función para adjuntar documentos
const attachDocument = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.pdf,.doc,.docx,.md,.txt,.html,.xlsx,.ppt,.pptx';
  input.onchange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await api.documents.upload(file, {
        epicId: props.epic.id.toString()
      });
      if (!props.epic.documents) {
        props.epic.documents = [];
      }
      // api.documents.upload returns ApiResponse<Document>; doc is in result.data
      props.epic.documents.push(result.data ?? result);
    } catch (err) {
      console.error('Error uploading document:', err);
    }
  };
  input.click();
};

// Drag and Drop functions
/**
 * Inicia el arrastre de la épica para reordenamiento
 */
const handleEpicDragStart = (event) => {
  // Detener propagación para que el clic no active eventos del contenedor padre
  event.stopPropagation()
  dragStart(props.epic, 'epic', event)
}

/**
 * Maneja el dragover específico para el contenedor de la épica
 * Solo permite dragover si lo que se arrastra es otra épica
 */
const handleEpicDragOver = (event) => {
  if (dragType.value === 'epic') {
    dragOver(event, props.epic.id)
  }
}

/**
 * Maneja el drop de una épica sobre otra (Reordenar)
 */
const handleEpicDrop = (event) => {
  const result = drop(event, props.epic.id, 'epic')
  if (result && result.type === 'epic' && reorderEpics) {
    reorderEpics(result.item.id, props.epic.id)
  }
}

/**
 * Maneja el drop de un ticket dentro de esta épica (Mover Ticket)
 */
const handleTicketDrop = async (event) => {
  const result = drop(event, props.epic.id, 'epic')
  if (result && result.type === 'ticket') {
    console.log(`Moviendo ticket ${result.item.id} a épica: ${props.epic.title}`)
    try {
      await ticketsStore.moveToEpic(result.item.id, props.epic.id)
    } catch (err) {
      console.error('Error al mover ticket:', err)
    }
  }
};
</script>

<style scoped>
/* Animación simple para que el acordeón no aparezca de golpe */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
