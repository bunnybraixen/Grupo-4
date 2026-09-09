<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Lista de Verificación de Subtareas -->
  <!-- ================================================================ -->
  <!-- Muestra subtareas con checkboxes de completación -->
  <!-- Barra de progreso, agregar nuevas, eliminar existentes -->
  <!-- Animaciones suaves para estado completado -->
  <!-- ================================================================ -->

  <div class="space-y-3">
    <!-- ================================================================ -->
    <!-- ENCABEZADO: Título y Barra de Progreso -->
    <!-- ================================================================ -->
    <div>
      <h4 class="text-sm font-semibold text-[var(--text-primary)] mb-2">Subtareas</h4>

      <!-- Barra de progreso -->
      <div class="flex items-center gap-2">
        <div class="flex-1 h-2 bg-[var(--border-subtle)] rounded-full overflow-hidden">
          <div
            class="h-full bg-[var(--lime)] transition-all duration-300"
            :style="{ width: progressPercentage + '%' }"
          />
        </div>
        <span class="text-xs text-[var(--text-secondary)]">
          {{ completedCount }}/{{ subtasks.length }}
        </span>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- LISTA DE SUBTAREAS -->
    <!-- ================================================================ -->
    <!-- Renderiza cada subtarea con checkbox y opciones -->
    <!-- ================================================================ -->
    <div v-if="subtasks.length === 0" class="text-center py-4 text-[var(--text-secondary)]">
      <Icon icon="mdi:checkbox-outline" class="text-2xl mx-auto mb-1" />
      <p class="text-sm">No hay subtareas</p>
    </div>

    <div v-else class="space-y-1">
      <div
        v-for="subtask in subtasks"
        :key="subtask.id"
        class="flex items-center gap-2 group px-2 py-1 hover:bg-[var(--bg-panel)] rounded transition-colors"
      >
        <!-- Checkbox de completación -->
        <input
          type="checkbox"
          :checked="subtask.isCompleted"
          @change="toggleSubtask(subtask)"
          class="w-4 h-4 cursor-pointer accent-[var(--lime)]"
        />

        <!-- Título de la subtarea -->
        <label
          :class="[
            'flex-1 text-sm cursor-pointer transition-all',
            (subtask.isCompleted)
              ? 'text-[var(--text-muted)] line-through'
              : 'text-[var(--text-secondary)]'
          ]"
        >
          {{ subtask.title }}
        </label>

        <!-- Confirmación inline al promover -->
        <template v-if="confirmingSubtaskId === subtask.id">
          <span class="text-[10px] text-[var(--text-muted)] whitespace-nowrap">¿Convertir?</span>
          <button
            @click="confirmingSubtaskId = null"
            class="px-2 py-1 text-[10px] font-medium text-[var(--text-secondary)] bg-[var(--bg-panel)] hover:bg-[var(--border-subtle)] rounded transition-all"
          >Cancelar</button>
          <button
            @click="doPromote(subtask)"
            class="px-2 py-1 mx-1 text-[10px] font-bold text-white bg-[var(--teal)] hover:opacity-80 rounded transition-all"
          >Confirmar</button>
        </template>
        <!-- Botón promover (siempre visible) -->
        <button
          v-else
          @click="confirmingSubtaskId = subtask.id"
          class="px-2 py-1 mx-1 text-[10px] font-bold uppercase tracking-wider text-[var(--teal)]/80 bg-[var(--teal)]/20 hover:bg-[var(--teal)]/40 rounded transition-all"
          title="Convertir esta subtarea en un ticket independiente"
        >
          ↑ Ticket
        </button>

        <!-- Botón eliminar (visible al hacer hover sobre la fila) -->
        <button
          @click="deleteSubtask(subtask.id)"
          class="opacity-0 group-hover:opacity-100 p-1 text-[var(--text-secondary)] hover:text-[var(--priority-urg-bg)] transition-all"
          :title="'Eliminar: ' + subtask.title"
        >
          <Icon icon="mdi:close" class="text-sm" />
        </button>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- AGREGAR NUEVA SUBTAREA -->
    <!-- ================================================================ -->
    <!-- Input en línea para crear nueva subtarea -->
    <!-- ================================================================ -->
    <div class="pt-2 border-t border-[var(--border-subtle)]">
      <button
        v-if="!isAddingSubtask"
        @click="isAddingSubtask = true"
        class="w-full px-2 py-1 text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] rounded transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:plus" />
        Agregar Subtarea
      </button>

      <!-- Input en línea (se muestra cuando isAddingSubtask es true)-->
      <div v-else class="flex gap-2">
        <input
          v-model="newSubtaskTitle"
          @keydown.enter="addSubtask"
          @keydown.escape="isAddingSubtask = false"
          type="text"
          placeholder="Título de la subtarea..."
          autofocus
          maxlength="100"
          class="flex-1 px-2 py-1 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded text-[var(--text-primary)] text-sm placeholder-[var(--text-secondary)] focus:outline-none focus:border-[var(--lime)]"
        />
        <button
          @click="addSubtask"
          class="px-2 py-1 bg-[var(--lime)] hover:bg-[var(--lime-90)] text-[var(--dark-gray)] rounded transition-colors"
          title="Guardar"
        >
          <Icon icon="mdi:check" />
        </button>
        <button
          @click="isAddingSubtask = false"
          class="px-2 py-1 bg-[var(--bg-panel)] hover:bg-[var(--bg-card)] text-[var(--text-primary)] rounded transition-colors"
          title="Cancelar"
        >
          <Icon icon="mdi:close" />
        </button>
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
import type { Subtask } from '@/types'
import { useDialogStore } from '@/stores/dialog'

const dialogStore = useDialogStore()

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  subtasks: Subtask[]
  ticketId: string
}

const props = defineProps<Props>()

// =====================================================================
// EMITS
// =====================================================================

/**
 * Eventos emitidos por el componente SubtaskChecklist
 */
const emit = defineEmits<{
  update: [subtask: Subtask]
  create: [title: string]
  delete: [subtaskId: string]
  promote: [subtask: Subtask]
}>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Control de creación de nueva subtarea
const isAddingSubtask = ref(false)

// Subtask id pendiente de confirmar promoción
const confirmingSubtaskId = ref<string | null>(null)

// Título de la nueva subtarea siendo creada
const newSubtaskTitle = ref('')

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Calcula la cantidad de subtareas completadas
 * Filtramos usando 'isCompleted' según la interfaz oficial
 */
const completedCount = computed(() => {
  return props.subtasks.filter(s => s.isCompleted).length
})

/**
 * Calcula el porcentaje de subtareas completadas
 * Se usa para renderizar el ancho de la barra de progreso
 */
const progressPercentage = computed(() => {
  if (props.subtasks.length === 0) return 0
  return Math.round((completedCount.value / props.subtasks.length) * 100)
})

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Alterna el estado completado de una subtarea
 * Emite evento de actualización hacia el padre
 */
const toggleSubtask = (subtask: any) => {
  // Emitir evento con la subtarea invertida en su estado isCompleted
  const currentState = subtask.isCompleted ?? subtask.is_completed
  emit('update', {
    ...subtask,
    isCompleted: !currentState,
    is_completed: !currentState
  })
}

/**
 * Elimina una subtarea
 * Muestra un diálogo de confirmación y emite evento de eliminación
 */
const deleteSubtask = async (subtaskId: string) => {
  // Confirmar antes de eliminar
  if (await dialogStore.confirm('¿Estás seguro de que quieres eliminar esta subtarea?')) {
    emit('delete', subtaskId)
  }
}

/**
 * Agrega una nueva subtarea
 * Valida que el título no esté vacío y emite evento de creación
 */
const addSubtask = () => {
  // Validación: título no vacío y con al menos 1 carácter
  if (newSubtaskTitle.value.trim().length === 0) {
    return
  }

  // Emitir evento para crear subtarea
  emit('create', newSubtaskTitle.value)

  // Limpiar estado local
  newSubtaskTitle.value = ''
  isAddingSubtask.value = false
}

/**
 * Emite la promoción después de confirmación inline
 */
const doPromote = (subtask: Subtask) => {
  confirmingSubtaskId.value = null
  emit('promote', subtask)
}

</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>


