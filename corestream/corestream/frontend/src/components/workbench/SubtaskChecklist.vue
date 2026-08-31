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
      <h4 class="text-sm font-semibold text-white mb-2">Subtareas</h4>

      <!-- Barra de progreso -->
      <div class="flex items-center gap-2">
        <div class="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-green-500 transition-all duration-300"
            :style="{ width: progressPercentage + '%' }"
          />
        </div>
        <span class="text-xs text-slate-400">
          {{ completedCount }}/{{ subtasks.length }}
        </span>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- LISTA DE SUBTAREAS -->
    <!-- ================================================================ -->
    <!-- Renderiza cada subtarea con checkbox y opciones -->
    <!-- ================================================================ -->
    <div v-if="subtasks.length === 0" class="text-center py-4 text-slate-400">
      <Icon icon="mdi:checkbox-outline" class="text-2xl mx-auto mb-1" />
      <p class="text-sm">No hay subtareas</p>
    </div>

    <div v-else class="space-y-1">
      <div
        v-for="subtask in subtasks"
        :key="subtask.id"
        class="flex items-center gap-2 group px-2 py-1 hover:bg-slate-700 rounded transition-colors"
      >
        <!-- Checkbox de completación -->
        <input
          type="checkbox"
          :checked="subtask.completed"
          @change="toggleSubtask(subtask)"
          class="w-4 h-4 cursor-pointer accent-green-500"
        />

        <!-- Título de la subtarea -->
        <label
          :class="[
            'flex-1 text-sm cursor-pointer transition-all',
            subtask.completed
              ? 'text-slate-500 line-through'
              : 'text-slate-300'
          ]"
        >
          {{ subtask.title }}
        </label>

        <!-- Botón eliminar (visible al hacer hover) -->
        <button
          @click="deleteSubtask(subtask.id)"
          class="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-400 transition-all"
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
    <div class="pt-2 border-t border-slate-700">
      <button
        v-if="!isAddingSubtask"
        @click="isAddingSubtask = true"
        class="w-full px-2 py-1 text-sm text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:plus" />
        Agregar Subtarea
      </button>

      <!-- Input en línea -->
      <div v-else class="flex gap-2">
        <input
          v-model="newSubtaskTitle"
          @keydown.enter="addSubtask"
          @keydown.escape="isAddingSubtask = false"
          type="text"
          placeholder="Título de la subtarea..."
          autofocus
          maxlength="100"
          class="flex-1 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-white text-sm placeholder-slate-400 focus:outline-none focus:border-green-500"
        />
        <button
          @click="addSubtask"
          class="px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
        >
          <Icon icon="mdi:check" />
        </button>
        <button
          @click="isAddingSubtask = false"
          class="px-2 py-1 bg-slate-600 hover:bg-slate-500 text-white rounded transition-colors"
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

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Subtask {
  id: string
  title: string
  completed: boolean
}

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  subtasks: Subtask[]
  ticketId: string
}

const props = defineProps<Props>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Control de creación de nueva subtarea
const isAddingSubtask = ref(false)

// Título de la nueva subtarea siendo creada
const newSubtaskTitle = ref('')

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Calcula la cantidad de subtareas completadas
 */
const completedCount = computed(() => {
  return props.subtasks.filter(s => s.completed).length
})

/**
 * Calcula el porcentaje de subtareas completadas
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
 * Emite evento de actualización
 */
const toggleSubtask = (subtask: Subtask) => {
  // Emitir evento con subtarea actualizada
  emit('update', {
    ...subtask,
    completed: !subtask.completed
  })
}

/**
 * Elimina una subtarea
 * Emite evento de eliminación
 */
const deleteSubtask = (subtaskId: string) => {
  // Confirmar antes de eliminar
  if (confirm('¿Estás seguro de que quieres eliminar esta subtarea?')) {
    emit('delete', subtaskId)
  }
}

/**
 * Agrega una nueva subtarea
 * Valida que el título no esté vacío
 * Emite evento de creación
 */
const addSubtask = () => {
  // Validación: título no vacío y con al menos 1 carácter
  if (newSubtaskTitle.value.trim().length === 0) {
    return
  }

  // Emitir evento para crear subtarea
  emit('create', newSubtaskTitle.value)

  // Limpiar estado
  newSubtaskTitle.value = ''
  isAddingSubtask.value = false
}

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
}>()
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>
