<template>
  <!-- Contenedor principal del panel de asignación -->
  <div class="w-full h-screen flex flex-col bg-gray-50">
    <!-- Encabezado del panel -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
      <h1 class="text-2xl font-bold text-gray-900">
        <!-- Título: Panel de Asignación de Tickets para Líderes de Grupo -->
        Panel de Asignación de Tickets
      </h1>
      <p class="text-gray-600 text-sm mt-1">
        <!-- Subtítulo explicativo del propósito del panel -->
        Distribuye tickets entre los miembros de tu equipo de desarrollo
      </p>
    </div>

    <!-- Contenedor principal con dos paneles laterales -->
    <div class="flex-1 flex overflow-hidden">
      <!-- PANEL IZQUIERDO: Tickets sin asignar (50% del ancho) -->
      <div class="w-1/2 border-r border-gray-200 flex flex-col bg-white">
        <!-- Encabezado del panel izquierdo -->
        <div class="border-b border-gray-200 px-6 py-4 bg-gray-50">
          <h2 class="text-lg font-bold text-gray-900">
            <!-- Título: Tickets Sin Asignar -->
            Tickets Sin Asignar
          </h2>
          <p class="text-gray-500 text-sm mt-1">
            <!-- Contador de tickets sin asignar -->
            {{ unassignedTickets.length }} ticket{{ unassignedTickets.length !== 1 ? 's' : '' }} disponible{{ unassignedTickets.length !== 1 ? 's' : '' }}
          </p>
        </div>

        <!-- Área de contenido del panel izquierdo (con scroll) -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <!-- Tarjetas de tickets sin asignar -->
          <div v-if="unassignedTickets.length > 0">
            <!-- Iterar sobre cada ticket sin asignar -->
            <div
              v-for="ticket in unassignedTickets"
              :key="ticket.id"
              class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            >
              <!-- Contenedor principal de la tarjeta -->
              <div class="space-y-3">
                <!-- Título del ticket -->
                <div class="flex items-start justify-between gap-2">
                  <h3 class="font-semibold text-gray-900 flex-1 line-clamp-2">
                    {{ ticket.title }}
                  </h3>
                  <!-- Badge de prioridad -->
                  <span
                    :class="getPriorityBadgeClass(ticket.priority)"
                    class="px-2 py-1 rounded text-xs font-semibold text-white whitespace-nowrap"
                  >
                    <!-- Etiqueta de nivel de prioridad -->
                    {{ getPriorityLabel(ticket.priority) }}
                  </span>
                </div>

                <!-- Nombre de la épica asociada -->
                <div v-if="ticket.epicName" class="flex items-center gap-2 text-sm text-gray-600">
                  <!-- Ícono de épica -->
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                    />
                  </svg>
                  <!-- Nombre de la épica -->
                  <span>{{ ticket.epicName }}</span>
                </div>

                <!-- Fecha de vencimiento -->
                <div class="flex items-center gap-2 text-sm text-gray-600">
                  <!-- Ícono de calendario -->
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <!-- Fecha formateada -->
                  <span>{{ formatDate(ticket.dueDate) }}</span>
                </div>

                <!-- Botón de asignación -->
                <button
                  @click="openAssignmentModal(ticket)"
                  class="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors text-sm"
                >
                  <!-- Texto del botón de asignación -->
                  Asignar Ticket
                </button>
              </div>
            </div>
          </div>

          <!-- Estado vacío cuando no hay tickets sin asignar -->
          <div v-else class="flex flex-col items-center justify-center h-full py-8 text-center">
            <!-- Ícono de estado vacío -->
            <svg class="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <!-- Mensaje de estado vacío -->
            <p class="text-gray-600 font-semibold">
              No hay tickets sin asignar
            </p>
            <!-- Sugerencia al usuario -->
            <p class="text-gray-500 text-sm mt-1">
              Todos los tickets han sido distribuidos
            </p>
          </div>
        </div>
      </div>

      <!-- PANEL DERECHO: Carga de trabajo por desarrollador (50% del ancho) -->
      <div class="w-1/2 flex flex-col bg-white">
        <!-- Encabezado del panel derecho -->
        <div class="border-b border-gray-200 px-6 py-4 bg-gray-50">
          <h2 class="text-lg font-bold text-gray-900">
            <!-- Título: Carga de Trabajo por Desarrollador -->
            Carga por Desarrollador
          </h2>
          <p class="text-gray-500 text-sm mt-1">
            <!-- Subtítulo: distribución de tickets asignados -->
            Visualiza la distribución actual de tickets
          </p>
        </div>

        <!-- Área de contenido del panel derecho (con scroll) -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <!-- Secciones de desarrolladores agrupados por carga de trabajo -->
          <div v-if="developerWorkload.length > 0">
            <!-- Iterar sobre cada desarrollador -->
            <div
              v-for="developer in developerWorkload"
              :key="developer.id"
              class="bg-gray-50 rounded-lg border border-gray-200 p-4 hover:shadow-sm transition-shadow"
            >
              <!-- Encabezado del desarrollador con avatar y nombre -->
              <div class="flex items-center gap-3 mb-3">
                <!-- Avatar del desarrollador con iniciales -->
                <div
                  :style="{ backgroundColor: '#6B7280' }"
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm"
                >
                  <!-- Iniciales del nombre del desarrollador -->
                  {{ getInitials(developer.name) }}
                </div>
                <!-- Nombre del desarrollador -->
                <div class="flex-1">
                  <h3 class="font-semibold text-gray-900">
                    {{ developer.name }}
                  </h3>
                </div>
                <!-- Contador de tickets asignados -->
                <span class="text-sm font-semibold text-gray-700 bg-white px-3 py-1 rounded-full border border-gray-300">
                  {{ developer.assignedTickets.length }} ticket{{ developer.assignedTickets.length !== 1 ? 's' : '' }}
                </span>
              </div>

              <!-- Barra de carga de trabajo coloreada -->
              <div class="mb-3">
                <!-- Texto de etiqueta sobre la barra -->
                <div class="flex justify-between items-center mb-1">
                  <span class="text-xs font-medium text-gray-600">
                    Carga de Trabajo
                  </span>
                  <!-- Porcentaje de carga -->
                  <span class="text-xs font-semibold text-gray-700">
                    {{ Math.round((developer.assignedTickets.length / 10) * 100) }}%
                  </span>
                </div>
                <!-- Barra de progreso con color basado en carga -->
                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    :style="{ width: `${Math.min((developer.assignedTickets.length / 10) * 100, 100)}%` }"
                    :class="getWorkloadBarColor(developer.assignedTickets.length)"
                    class="h-full rounded-full transition-all"
                  />
                </div>
              </div>

              <!-- Lista de tickets asignados a este desarrollador -->
              <div v-if="developer.assignedTickets.length > 0" class="space-y-2">
                <!-- Iterar sobre tickets asignados -->
                <div
                  v-for="ticket in developer.assignedTickets"
                  :key="ticket.id"
                  class="flex items-start justify-between gap-2 bg-white p-2 rounded border border-gray-300"
                >
                  <!-- Información del ticket -->
                  <div class="flex-1 min-w-0">
                    <!-- Título del ticket -->
                    <p class="text-sm font-medium text-gray-900 line-clamp-1">
                      {{ ticket.title }}
                    </p>
                    <!-- Épica del ticket -->
                    <p class="text-xs text-gray-600 line-clamp-1">
                      {{ ticket.epicName || 'Sin épica' }}
                    </p>
                  </div>
                  <!-- Botón para desasignar ticket -->
                  <button
                    @click="handleUnassign(ticket.id, developer.id)"
                    title="Desasignar ticket"
                    class="p-1 hover:bg-red-100 rounded transition-colors text-red-600 hover:text-red-700 flex-shrink-0"
                  >
                    <!-- Ícono de X para desasignar -->
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fill-rule="evenodd"
                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                        clip-rule="evenodd"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Mensaje cuando el desarrollador no tiene tickets asignados -->
              <div v-else class="text-center py-2">
                <p class="text-sm text-gray-500">
                  Sin tickets asignados
                </p>
              </div>
            </div>
          </div>

          <!-- Estado vacío cuando no hay desarrolladores -->
          <div v-else class="flex flex-col items-center justify-center h-full py-8 text-center">
            <!-- Ícono de estado vacío -->
            <svg class="w-12 h-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-2a6 6 0 0112 0v2zm0 0h6v-2a6 6 0 00-9-5.697M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <!-- Mensaje de estado vacío -->
            <p class="text-gray-600 font-semibold">
              No hay desarrolladores
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL DE ASIGNACIÓN: Modal para seleccionar desarrollador -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <!-- Contenedor del modal -->
      <div class="bg-white rounded-lg shadow-2xl p-8 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
        <!-- Encabezado del modal -->
        <div class="mb-6">
          <!-- Título del modal -->
          <h3 class="text-xl font-bold text-gray-900">
            Asignar Ticket
          </h3>
          <!-- Subtítulo con nombre del ticket -->
          <p class="text-gray-600 text-sm mt-2">
            {{ selectedTicket?.title || 'Selecciona un ticket' }}
          </p>
        </div>

        <!-- Mensaje informativo -->
        <p class="text-gray-600 text-sm mb-4">
          Selecciona un desarrollador para asignar este ticket:
        </p>

        <!-- Lista de desarrolladores disponibles para asignación -->
        <div class="space-y-2">
          <!-- Iterar sobre desarrolladores disponibles -->
          <button
            v-for="developer in availableDevelopers"
            :key="developer.id"
            @click="assignTicket(developer.id)"
            class="w-full text-left p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
          >
            <!-- Contenedor del desarrollador en la lista de selección -->
            <div class="flex items-center justify-between gap-3">
              <!-- Información del desarrollador -->
              <div class="flex items-center gap-3 flex-1">
                <!-- Avatar del desarrollador -->
                <div
                  :style="{ backgroundColor: '#6B7280' }"
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
                >
                  <!-- Iniciales del desarrollador -->
                  {{ getInitials(developer.name) }}
                </div>
                <!-- Nombre e información de carga -->
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-gray-900">
                    {{ developer.name }}
                  </p>
                  <p class="text-xs text-gray-600">
                    {{ developer.assignedTickets.length }} ticket{{ developer.assignedTickets.length !== 1 ? 's' : '' }} asignado{{ developer.assignedTickets.length !== 1 ? 's' : '' }}
                  </p>
                </div>
              </div>
              <!-- Indicador de carga visual -->
              <div class="w-12 h-2 bg-gray-200 rounded-full overflow-hidden flex-shrink-0">
                <div
                  :style="{ width: `${Math.min((developer.assignedTickets.length / 10) * 100, 100)}%` }"
                  :class="getWorkloadBarColor(developer.assignedTickets.length)"
                  class="h-full rounded-full"
                />
              </div>
            </div>
          </button>
        </div>

        <!-- Botones de acción del modal -->
        <div class="flex gap-3 mt-6 pt-6 border-t border-gray-200">
          <!-- Botón de cancelación -->
          <button
            @click="closeAssignmentModal"
            class="flex-1 px-4 py-2 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Componente de Panel de Asignación de Tickets (AssignmentPanel.vue)
 * 
 * Este componente es exclusivamente para Líderes de Grupo y proporciona:
 * - Panel izquierdo: Lista de tickets sin asignar con cards informativos
 * - Panel derecho: Visualización de carga de trabajo por desarrollador
 * - Modal de asignación: Para distribuir tickets entre desarrolladores
 * - Barra de carga visual: Cambia de color según el número de tickets (verde, amarillo, rojo)
 * 
 * Utiliza:
 * - useTeamStore para datos de desarrolladores
 * - useTicketsStore para datos de tickets
 * - Composición API de Vue 3 con TypeScript
 * - Tailwind CSS para diseño responsivo
 */

import { ref, computed, onMounted } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import { useTeamStore } from '@/stores/team'
import { useTicketsStore } from '@/stores/tickets'
import { useAuthStore } from '@/stores/auth'

/**
 * Interfaz para un ticket del sistema
 */
interface Ticket {
  id: string
  title: string
  epicName?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  dueDate: string
  assignedTo?: string
}

/**
 * Interfaz para un desarrollador con su información de carga
 */
interface Developer {
  id: string
  name: string
  assignedTickets: Ticket[]
}

// ============================================================================
// ESTADO REACTIVO - Variables ref y computed
// ============================================================================

/**
 * Control de visibilidad del modal de asignación de tickets
 */
const showAssignModal: Ref<boolean> = ref(false)

/**
 * Ticket actualmente seleccionado para asignación en el modal
 */
const selectedTicket: Ref<Ticket | null> = ref(null)

// ============================================================================
// ACCESO A STORES - Pinia stores para estado global
// ============================================================================

/**
 * Store de equipo - contiene información de desarrolladores
 */
const teamStore = useTeamStore()

/**
 * Store de tickets - contiene información de tickets
 */
const ticketsStore = useTicketsStore()

/**
 * Store de autenticación - verifica permisos del usuario
 */
const authStore = useAuthStore()

// ============================================================================
// PROPIEDADES COMPUTADAS - Valores derivados y filtrados
// ============================================================================

/**
 * Lista de tickets sin asignar
 * Filtra solo aquellos tickets que no tienen desarrollador asignado
 */
const unassignedTickets: ComputedRef<Ticket[]> = computed(() => {
  return ticketsStore.tickets.filter((ticket) => !ticket.assignedTo)
})

/**
 * Lista de desarrolladores con su información de carga de trabajo
 * Agrupa los tickets asignados por desarrollador
 */
const developerWorkload: ComputedRef<Developer[]> = computed(() => {
  return teamStore.members
    .filter((member) => member.role === 'developer')
    .map((developer) => ({
      id: developer.id,
      name: developer.name,
      assignedTickets: ticketsStore.tickets.filter(
        (ticket) => ticket.assignedTo === developer.id
      )
    }))
})

/**
 * Lista de desarrolladores disponibles para la asignación actual
 * Se usa en el modal para mostrar opciones de asignación
 */
const availableDevelopers: ComputedRef<Developer[]> = computed(() => {
  return developerWorkload.value
})

// ============================================================================
// MÉTODOS - Funciones para manejar acciones del usuario
// ============================================================================

/**
 * Obtiene las iniciales de un nombre
 * Ejemplo: "Juan Pérez" → "JP"
 * 
 * @param name - Nombre completo
 * @returns Iniciales en mayúsculas
 */
function getInitials(name: string): string {
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Retorna las clases CSS de Tailwind para el badge de prioridad
 * Colorea el badge según la prioridad del ticket
 * 
 * @param priority - Nivel de prioridad (low, medium, high, critical)
 * @returns Clases de Tailwind para el badge
 */
function getPriorityBadgeClass(priority: string): string {
  const classMap: Record<string, string> = {
    low: 'bg-green-600',
    medium: 'bg-yellow-600',
    high: 'bg-orange-600',
    critical: 'bg-red-600'
  }
  return classMap[priority] || 'bg-gray-600'
}

/**
 * Retorna la etiqueta legible en español de la prioridad
 * 
 * @param priority - Nivel de prioridad
 * @returns Nombre de la prioridad en español
 */
function getPriorityLabel(priority: string): string {
  const labels: Record<string, string> = {
    low: 'Baja',
    medium: 'Media',
    high: 'Alta',
    critical: 'Crítica'
  }
  return labels[priority] || 'Desconocida'
}

/**
 * Retorna la clase CSS de Tailwind para la barra de carga según cantidad de tickets
 * - 1-3 tickets: verde (carga baja)
 * - 4-5 tickets: amarillo (carga media)
 * - 6+ tickets: rojo (carga alta)
 * 
 * @param ticketCount - Número de tickets asignados
 * @returns Clase de color de Tailwind para la barra
 */
function getWorkloadBarColor(ticketCount: number): string {
  if (ticketCount <= 3) {
    return 'bg-green-500'
  } else if (ticketCount <= 5) {
    return 'bg-yellow-500'
  } else {
    return 'bg-red-500'
  }
}

/**
 * Formatea una fecha a formato legible en español
 * Ejemplo: "2026-03-15" → "15 de mar, 2026"
 * 
 * @param dateString - Fecha en formato ISO (YYYY-MM-DD)
 * @returns Fecha formateada en español
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

/**
 * Abre el modal de asignación de tickets
 * Establece el ticket seleccionado y muestra el modal
 * 
 * @param ticket - Ticket a asignar
 */
function openAssignmentModal(ticket: Ticket): void {
  selectedTicket.value = ticket
  showAssignModal.value = true
}

/**
 * Cierra el modal de asignación de tickets
 * Limpia la selección de ticket y oculta el modal
 */
function closeAssignmentModal(): void {
  showAssignModal.value = false
  selectedTicket.value = null
}

/**
 * Asigna un ticket a un desarrollador
 * Actualiza el estado del ticket en el store y cierra el modal
 * 
 * @param developerId - ID del desarrollador a asignar
 */
async function assignTicket(developerId: string): Promise<void> {
  if (!selectedTicket.value) {
    return
  }

  try {
    // Llamar acción del store para asignar ticket
    await ticketsStore.assignTicket(selectedTicket.value.id, developerId)
    // Cerrar modal después de asignación exitosa
    closeAssignmentModal()
  } catch (error) {
    console.error('Error al asignar ticket:', error)
  }
}

/**
 * Desasigna un ticket de un desarrollador
 * Remueve la asignación y permite reasignar el ticket
 * 
 * @param ticketId - ID del ticket a desasignar
 * @param developerId - ID del desarrollador actual
 */
async function handleUnassign(ticketId: string, developerId: string): Promise<void> {
  try {
    // Llamar acción del store para desasignar ticket
    await ticketsStore.unassignTicket(ticketId)
  } catch (error) {
    console.error('Error al desasignar ticket:', error)
  }
}

// ============================================================================
// INICIALIZACIÓN - Hook de montaje del componente
// ============================================================================

/**
 * Hook de montaje: se ejecuta cuando el componente está listo
 * Valida que el usuario sea un Líder de Grupo
 * Carga datos iniciales de desarrolladores y tickets
 */
onMounted(async () => {
  try {
    // Verificar que el usuario actual sea líder de grupo
    if (authStore.currentUser?.role !== 'leader') {
      console.warn('Solo líderes de grupo pueden acceder a este panel')
      return
    }

    // Cargar datos iniciales si es necesario
    if (teamStore.members.length === 0) {
      await teamStore.fetchMembers()
    }
    if (ticketsStore.tickets.length === 0) {
      await ticketsStore.fetchTickets()
    }
  } catch (error) {
    console.error('Error en inicialización del panel:', error)
  }
})
</script>

<style scoped>
/**
 * Estilos locales para el componente AssignmentPanel
 * Todos los estilos están encapsulados en el componente
 */

/* Animación suave para transiciones de hover */
button {
  transition: all 0.2s ease-in-out;
}

/* Estilos para la barra de progreso */
.h-2 {
  background-color: #e5e7eb;
}

/* Scroll personalizado para paneles */
div::-webkit-scrollbar {
  width: 6px;
}

div::-webkit-scrollbar-track {
  background: transparent;
}

div::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

div::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
