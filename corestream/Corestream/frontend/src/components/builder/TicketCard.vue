<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Tarjeta de Ticket -->
  <!-- ================================================================ -->
  <!-- Tarjeta compacta que representa un ticket individual -->
  <!-- Soporta: drag and drop, estados visuales, indicadores de prioridad -->
  <!-- Muestra: título, estado, prioridad, asignado, fecha vencimiento -->
  <!-- ================================================================ -->

  <div
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="$emit('dragEnd')"
    @click="$emit('select', ticket)"
    :class="[
      'p-3 bg-slate-700 border border-slate-600 rounded-lg cursor-grab active:cursor-grabbing',
      'hover:shadow-lg hover:border-slate-500 transition-all duration-200',
      ticket.status === 'BLOCKED' ? 'border-orange-500 border-opacity-50' : '',
      'group'
    ]"
  >
    <!-- Contenedor principal con grid layout -->
    <div class="space-y-2">
      <!-- ================================================================ -->
      <!-- FILA 1: Título y Estado -->
      <!-- ================================================================ -->
      <div class="flex items-start justify-between gap-2">
        <!-- Título del ticket -->
        <h4 class="text-sm font-medium text-white flex-1 line-clamp-2">
          {{ ticket.title }}
        </h4>

        <!-- Badge de estado con colores específicos -->
        <span
          :class="[
            'inline-block px-2 py-1 text-xs font-semibold rounded whitespace-nowrap flex-shrink-0',
            getStatusColor(ticket.status)
          ]"
        >
          {{ getStatusLabel(ticket.status) }}
        </span>
      </div>

      <!-- ================================================================ -->
      <!-- FILA 2: Indicadores (Prioridad, Asignado, Vencimiento) -->
      <!-- ================================================================ -->
      <div class="flex items-center gap-2">
        <!-- Indicador de prioridad (círculo de color) -->
        <div
          :class="[
            'w-2 h-2 rounded-full flex-shrink-0',
            getPriorityColor(ticket.priority)
          ]"
          :title="`Prioridad: ${ticket.priority}`"
        />

        <!-- Avatar del asignado -->
        <div
          v-if="ticket.assignee"
          class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold bg-blue-600 text-white flex-shrink-0"
          :title="ticket.assignee.name"
        >
          {{ getInitials(ticket.assignee.name) }}
        </div>

        <!-- Espaciador flexible -->
        <div class="flex-1" />

        <!-- Indicador de vencimiento -->
        <div v-if="ticket.dueDate" class="flex items-center gap-1 text-xs">
          <Icon
            :icon="isOverdue ? 'mdi:alert-circle' : 'mdi:calendar'"
            :class="[
              'flex-shrink-0',
              isOverdue ? 'text-red-400' : 'text-slate-400'
            ]"
          />
          <span :class="[isOverdue ? 'text-red-400 font-semibold' : 'text-slate-400']">
            {{ formatDate(ticket.dueDate) }}
          </span>
        </div>
      </div>

      <!-- ================================================================ -->
      <!-- SECCIÓN: Indicador de Atraso (si aplica) -->
      <!-- ================================================================ -->
      <!-- Muestra cantidad de días atrasados en rojo -->
      <!-- ================================================================ -->
      <div v-if="isOverdue && daysOverdue > 0" class="text-xs font-semibold text-red-400">
        <Icon icon="mdi:close-circle" class="inline mr-1" />
        {{ daysOverdue }} días atrasado
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- ANIMACIÓN: Pulso de bloqueo -->
    <!-- ================================================================ -->
    <!-- Si el ticket está bloqueado, muestra borde pulsante -->
    <!-- ================================================================ -->
    <div
      v-if="ticket.status === 'BLOCKED'"
      class="absolute inset-0 border border-orange-500 rounded-lg animate-pulse pointer-events-none"
    />
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { computed } from 'vue'
import { Icon } from '@iconify/vue'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Assignee {
  id: string
  name: string
  avatar: string
}

interface Ticket {
  id: string
  title: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  assignee?: Assignee
  dueDate?: string
}

// =====================================================================
// PROPS
// =====================================================================

// Objeto ticket con todos sus datos
const props = defineProps<{
  ticket: Ticket
}>()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Determina si el ticket está atrasado
 * Compara fecha de vencimiento con fecha actual
 */
const isOverdue = computed(() => {
  if (!props.ticket.dueDate) return false
  return new Date(props.ticket.dueDate) < new Date()
})

/**
 * Calcula la cantidad de días atrasados
 * Si no está atrasado, retorna 0
 */
const daysOverdue = computed(() => {
  if (!isOverdue.value) return 0
  
  const dueDate = new Date(props.ticket.dueDate!)
  const today = new Date()
  const diffTime = Math.abs(today.getTime() - dueDate.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  return diffDays
})

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Retorna clases de Tailwind para colorear el badge de estado
 * @param status - Estado del ticket
 * @returns String de clases de Tailwind
 */
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'TODO':
      return 'bg-gray-600 text-gray-100'
    case 'IN_PROGRESS':
      return 'bg-blue-600 text-blue-100'
    case 'BLOCKED':
      return 'bg-orange-600 text-orange-100 animate-pulse'
    case 'DONE':
      return 'bg-green-600 text-green-100'
    default:
      return 'bg-slate-600 text-slate-100'
  }
}

/**
 * Retorna etiqueta en español para el estado
 * @param status - Estado del ticket
 * @returns Etiqueta en español
 */
const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'TODO':
      return 'Por Hacer'
    case 'IN_PROGRESS':
      return 'En Curso'
    case 'BLOCKED':
      return 'Bloqueado'
    case 'DONE':
      return 'Completado'
    default:
      return status
  }
}

/**
 * Retorna clase de Tailwind para colorear el punto de prioridad
 * @param priority - Nivel de prioridad
 * @returns String de clase Tailwind
 */
const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'LOW':
      return 'bg-green-500'
    case 'MEDIUM':
      return 'bg-yellow-500'
    case 'HIGH':
      return 'bg-orange-500'
    case 'CRITICAL':
      return 'bg-red-500'
    default:
      return 'bg-slate-500'
  }
}

/**
 * Obtiene las iniciales del nombre de una persona
 * Toma primera letra de primer y último nombre
 * @param name - Nombre completo
 * @returns Iniciales (máximo 2 caracteres)
 */
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Formatea la fecha para mostrar
 * Retorna formato dd/MM/yyyy
 * @param dateString - Fecha en string ISO
 * @returns Fecha formateada
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}/${month}/${year}`
}

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Maneja el inicio del arrastre del ticket
 * Establece el ticket como dato de transferencia drag-drop
 */
const handleDragStart = (event: DragEvent) => {
  // Almacenar ID del ticket siendo arrastrado
  event.dataTransfer!.effectAllowed = 'move'
  event.dataTransfer!.setData('ticketId', props.ticket.id)
  
  // Emitir evento para notificar al padre
  emit('dragStart', props.ticket)
}

// =====================================================================
// EMITS
// =====================================================================

// Define eventos emitidos por el componente
const emit = defineEmits<{
  select: [ticket: Ticket]
  dragStart: [ticket: Ticket]
  dragEnd: []
}>()
</script>

<style scoped>
/* El componente usa Tailwind CSS para todos los estilos */
/* No se requieren estilos personalizados adicionales */
</style>
