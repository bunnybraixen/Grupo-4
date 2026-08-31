<template>
  <!-- Contenedor principal del componente -->
  <div class="w-full flex flex-col gap-4 p-6 bg-white rounded-lg shadow-sm">
    <!-- Encabezado con título y botón de agregar -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-900">
        <!-- Título de la lista de miembros -->
        Equipo
      </h2>
      <!-- Botón para agregar nuevo desarrollador (solo visible para administradores) -->
      <button
        v-if="isAdmin"
        @click="showAddForm = true"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center gap-2"
      >
        <!-- Ícono de plus para agregar miembro -->
        <span>+</span>
        <span>Agregar Desarrollador</span>
      </button>
    </div>

    <!-- Barra de búsqueda y filtrado -->
    <div class="flex items-center gap-2">
      <div class="relative flex-1">
        <!-- Campo de entrada para buscar miembros por nombre o email -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar por nombre o correo..."
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        />
        <!-- Ícono de búsqueda en el campo -->
        <svg
          class="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
    </div>

    <!-- Tabla de miembros o estado vacío -->
    <div v-if="filteredMembers.length > 0" class="overflow-x-auto">
      <!-- Tabla con estilos de Tailwind -->
      <table class="w-full border-collapse">
        <!-- Encabezado de la tabla -->
        <thead>
          <tr class="border-b-2 border-gray-200 bg-gray-50">
            <!-- Columna de avatar -->
            <th class="px-4 py-3 text-left font-semibold text-gray-700 w-20">
              Avatar
            </th>
            <!-- Columna de nombre y email -->
            <th class="px-4 py-3 text-left font-semibold text-gray-700">
              Nombre
            </th>
            <!-- Columna de rol -->
            <th class="px-4 py-3 text-left font-semibold text-gray-700 w-32">
              Rol
            </th>
            <!-- Columna de especialidad -->
            <th class="px-4 py-3 text-left font-semibold text-gray-700">
              Especialidad
            </th>
            <!-- Columna de estadísticas -->
            <th class="px-4 py-3 text-center font-semibold text-gray-700 w-56">
              Estadísticas
            </th>
            <!-- Columna de acciones -->
            <th class="px-4 py-3 text-center font-semibold text-gray-700 w-40">
              Acciones
            </th>
          </tr>
        </thead>
        <!-- Cuerpo de la tabla con filas de miembros -->
        <tbody>
          <!-- Iterar sobre miembros filtrados -->
          <tr
            v-for="member in filteredMembers"
            :key="member.id"
            class="border-b border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <!-- Celda de avatar con iniciales y color de fondo basado en rol -->
            <td class="px-4 py-4">
              <div
                :style="{ backgroundColor: getAvatarColor(member.role) }"
                class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-sm"
              >
                <!-- Iniciales del nombre del miembro -->
                {{ getInitials(member.name) }}
              </div>
            </td>
            <!-- Celda con nombre y correo electrónico -->
            <td class="px-4 py-4">
              <div class="flex flex-col">
                <!-- Nombre del miembro -->
                <span class="font-semibold text-gray-900">{{ member.name }}</span>
                <!-- Correo electrónico del miembro -->
                <span class="text-sm text-gray-600">{{ member.email }}</span>
              </div>
            </td>
            <!-- Celda de rol con badge coloreado -->
            <td class="px-4 py-4">
              <span
                :class="getRoleBadgeClass(member.role)"
                class="px-3 py-1 rounded-full text-sm font-semibold text-white inline-block"
              >
                <!-- Texto del rol del miembro -->
                {{ getRoleLabel(member.role) }}
              </span>
            </td>
            <!-- Celda de especialidad del miembro -->
            <td class="px-4 py-4 text-gray-700">
              <!-- Especialidad técnica del miembro -->
              {{ member.specialty || 'Sin especificar' }}
            </td>
            <!-- Celda con cuatro estadísticas pequeñas -->
            <td class="px-4 py-4">
              <div class="grid grid-cols-4 gap-2 text-center">
                <!-- Estadística de tareas completadas -->
                <div class="bg-green-50 rounded p-2">
                  <div class="text-lg font-bold text-green-700">
                    {{ member.stats.completed }}
                  </div>
                  <div class="text-xs text-green-600">Completadas</div>
                </div>
                <!-- Estadística de tareas pendientes -->
                <div class="bg-yellow-50 rounded p-2">
                  <div class="text-lg font-bold text-yellow-700">
                    {{ member.stats.pending }}
                  </div>
                  <div class="text-xs text-yellow-600">Pendientes</div>
                </div>
                <!-- Estadística de tareas bloqueadas -->
                <div class="bg-red-50 rounded p-2">
                  <div class="text-lg font-bold text-red-700">
                    {{ member.stats.blocked }}
                  </div>
                  <div class="text-xs text-red-600">Bloqueadas</div>
                </div>
                <!-- Estadística de tiempo promedio -->
                <div class="bg-blue-50 rounded p-2">
                  <div class="text-lg font-bold text-blue-700">
                    {{ member.stats.avgTime }}h
                  </div>
                  <div class="text-xs text-blue-600">Promedio</div>
                </div>
              </div>
            </td>
            <!-- Celda de acciones con botones de editar, eliminar y promoción de rol -->
            <td class="px-4 py-4">
              <div class="flex items-center justify-center gap-2">
                <!-- Botón de promoción a Líder de Grupo (visible solo para desarrolladores cuando el usuario es admin) -->
                <button
                  v-if="isAdmin && member.role === 'developer'"
                  @click="handlePromote(member.id)"
                  title="Promocionar a Líder de Grupo"
                  class="p-2 hover:bg-yellow-100 rounded-lg transition-colors text-yellow-600 hover:text-yellow-700"
                >
                  <!-- Ícono de corona para promoción -->
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2l3 6h6l-5 4 2 6-6-4-6 4 2-6-5-4h6l3-6z" />
                  </svg>
                </button>
                <!-- Botón de degradación de Líder (visible solo para líderes cuando el usuario es admin) -->
                <button
                  v-if="isAdmin && member.role === 'leader'"
                  @click="handleDemote(member.id)"
                  title="Degradar de Líder"
                  class="p-2 hover:bg-red-100 rounded-lg transition-colors text-red-600 hover:text-red-700"
                >
                  <!-- Ícono de degradación (flecha hacia abajo) -->
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 14l-7 7m0 0l-7-7m7 7V3"
                    />
                  </svg>
                </button>
                <!-- Botón de edición de miembro -->
                <button
                  @click="handleEdit(member.id)"
                  title="Editar miembro"
                  class="p-2 hover:bg-blue-100 rounded-lg transition-colors text-blue-600 hover:text-blue-700"
                >
                  <!-- Ícono de lápiz para editar -->
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
                <!-- Botón de eliminación de miembro -->
                <button
                  @click="handleDelete(member.id)"
                  title="Eliminar miembro"
                  class="p-2 hover:bg-red-100 rounded-lg transition-colors text-red-600 hover:text-red-700"
                >
                  <!-- Ícono de basura para eliminar -->
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Estado vacío cuando no hay miembros o los resultados están vacíos -->
    <div v-else class="flex flex-col items-center justify-center py-16 text-center">
      <!-- Ícono de estado vacío -->
      <svg class="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 4.354a4 4 0 110 5.292M15 21H3v-2a6 6 0 0112 0v2zm0 0h6v-2a6 6 0 00-9-5.697M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <!-- Mensaje de estado vacío -->
      <p class="text-gray-600 font-semibold">
        {{ searchQuery ? 'No se encontraron miembros' : 'No hay miembros en el equipo' }}
      </p>
      <!-- Sugerencia al usuario para agregar miembros -->
      <p class="text-gray-500 text-sm mt-1">
        {{ isAdmin ? 'Haz clic en "Agregar Desarrollador" para crear un nuevo miembro' : 'Contacta a un administrador' }}
      </p>
    </div>

    <!-- Modal o formulario en línea para agregar nuevo miembro -->
    <div v-if="showAddForm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <!-- Contenedor del modal -->
      <div class="bg-white rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
        <!-- Título del modal -->
        <h3 class="text-xl font-bold text-gray-900 mb-6">
          Agregar Nuevo Desarrollador
        </h3>
        <!-- Formulario de entrada -->
        <form @submit.prevent="handleAddMember" class="space-y-4">
          <!-- Campo de nombre -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Nombre Completo
            </label>
            <input
              v-model="newMember.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Juan Pérez"
            />
          </div>
          <!-- Campo de correo electrónico -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Correo Electrónico
            </label>
            <input
              v-model="newMember.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="juan@example.com"
            />
          </div>
          <!-- Campo de especialidad -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Especialidad
            </label>
            <input
              v-model="newMember.specialty"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Frontend, Backend, etc."
            />
          </div>
          <!-- Botones del formulario -->
          <div class="flex gap-3 pt-4">
            <!-- Botón de cancelación -->
            <button
              type="button"
              @click="showAddForm = false"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <!-- Botón de envío -->
            <button
              type="submit"
              class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Agregar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Componente de Lista de Miembros del Equipo (MemberList.vue)
 * 
 * Este componente muestra una tabla completa de miembros del equipo con:
 * - Búsqueda y filtrado de miembros por nombre o correo
 * - Visualización de rol, especialidad y estadísticas individuales
 * - Acciones de administración: promoción, degradación, edición y eliminación
 * - Modal para agregar nuevos desarrolladores al equipo
 * 
 * Utiliza:
 * - useTeamStore para gestionar el estado del equipo
 * - useAuthStore para validar permisos de administrador
 * - Composición API de Vue 3 con TypeScript
 * - Tailwind CSS para estilos completamente responsivos
 */

import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { useTeamStore } from '@/stores/team'
import { useAuthStore } from '@/stores/auth'

/**
 * Interfaz para un miembro del equipo
 */
interface TeamMember {
  id: string
  name: string
  email: string
  role: 'admin' | 'leader' | 'developer'
  specialty?: string
  stats: {
    completed: number
    pending: number
    blocked: number
    avgTime: number
  }
}

/**
 * Interfaz para nuevo miembro en el formulario
 */
interface NewMemberForm {
  name: string
  email: string
  specialty: string
}

// ============================================================================
// DEFINICIÓN DE EMITS - Eventos que emite este componente
// ============================================================================
const emit = defineEmits<{
  /**
   * Emitido cuando se inicia la edición de un miembro
   * @param userId - ID del usuario a editar
   */
  edit: [userId: string]
  /**
   * Emitido cuando se solicita la eliminación de un miembro
   * @param userId - ID del usuario a eliminar
   */
  delete: [userId: string]
}>()

// ============================================================================
// ESTADO REACTIVO - Variables ref y computed
// ============================================================================

/**
 * Consulta de búsqueda actual - filtra miembros por nombre o correo
 */
const searchQuery: Ref<string> = ref('')

/**
 * Control de visibilidad del modal para agregar nuevo desarrollador
 */
const showAddForm: Ref<boolean> = ref(false)

/**
 * Datos del nuevo miembro siendo creado en el formulario
 */
const newMember: Ref<NewMemberForm> = ref({
  name: '',
  email: '',
  specialty: ''
})

// ============================================================================
// ACCESO A STORES - Pinia stores para estado global
// ============================================================================

/**
 * Store de equipo - contiene lista de miembros del equipo
 */
const teamStore = useTeamStore()

/**
 * Store de autenticación - verifica si el usuario actual es administrador
 */
const authStore = useAuthStore()

// ============================================================================
// PROPIEDADES COMPUTADAS - Valores derivados y filtrados
// ============================================================================

/**
 * Lista de todos los miembros del equipo
 */
const members = computed(() => teamStore.members)

/**
 * Verifica si el usuario actual tiene permisos de administrador
 * Permite ver y usar botones de gestión de roles
 */
const isAdmin = computed(() => authStore.currentUser?.role === 'admin')

/**
 * Miembros filtrados basados en la consulta de búsqueda
 * Busca en nombre y email (case-insensitive)
 */
const filteredMembers = computed(() => {
  if (!searchQuery.value.trim()) {
    return members.value
  }

  const query = searchQuery.value.toLowerCase()
  return members.value.filter(
    (member) =>
      member.name.toLowerCase().includes(query) ||
      member.email.toLowerCase().includes(query)
  )
})

// ============================================================================
// MÉTODOS - Funciones para manejar acciones del usuario
// ============================================================================

/**
 * Obtiene las iniciales del nombre de un miembro
 * Ejemplo: "Juan Pérez" → "JP"
 * 
 * @param name - Nombre completo del miembro
 * @returns Iniciales en mayúsculas (máximo 2 caracteres)
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
 * Retorna el color de fondo del avatar basado en el rol del miembro
 * - Admin: Rojo
 * - Líder de Grupo: Oro/Amarillo
 * - Desarrollador: Gris
 * 
 * @param role - Rol del miembro (admin, leader, developer)
 * @returns Código de color hexadecimal
 */
function getAvatarColor(role: string): string {
  const colorMap: Record<string, string> = {
    admin: '#DC2626', // Rojo
    leader: '#D97706', // Oro/Amarillo
    developer: '#6B7280' // Gris
  }
  return colorMap[role] || '#9CA3AF'
}

/**
 * Retorna las clases CSS de Tailwind para el badge de rol
 * Colorea el badge según el tipo de rol
 * 
 * @param role - Rol del miembro
 * @returns Clases de Tailwind para el badge
 */
function getRoleBadgeClass(role: string): string {
  const classMap: Record<string, string> = {
    admin: 'bg-red-600',
    leader: 'bg-yellow-600',
    developer: 'bg-gray-600'
  }
  return classMap[role] || 'bg-gray-600'
}

/**
 * Retorna la etiqueta legible en español del rol
 * 
 * @param role - Rol del miembro
 * @returns Nombre del rol en español
 */
function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    admin: 'Administrador',
    leader: 'Líder de Grupo',
    developer: 'Desarrollador'
  }
  return labels[role] || 'Desconocido'
}

/**
 * Maneja la promoción de un desarrollador a líder de grupo
 * Solo visible y accesible para administradores
 * 
 * @param userId - ID del desarrollador a promocionar
 */
async function handlePromote(userId: string): Promise<void> {
  try {
    await teamStore.promoteToLeader(userId)
  } catch (error) {
    console.error('Error al promocionar miembro:', error)
  }
}

/**
 * Maneja la degradación de un líder de grupo a desarrollador
 * Solo visible y accesible para administradores
 * 
 * @param userId - ID del líder a degradar
 */
async function handleDemote(userId: string): Promise<void> {
  try {
    await teamStore.demoteFromLeader(userId)
  } catch (error) {
    console.error('Error al degradar miembro:', error)
  }
}

/**
 * Maneja la acción de editar un miembro
 * Emite evento 'edit' para que el componente padre maneje la edición
 * 
 * @param userId - ID del miembro a editar
 */
function handleEdit(userId: string): void {
  emit('edit', userId)
}

/**
 * Maneja la acción de eliminar un miembro
 * Emite evento 'delete' para que el componente padre maneje la eliminación
 * 
 * @param userId - ID del miembro a eliminar
 */
function handleDelete(userId: string): void {
  emit('delete', userId)
}

/**
 * Maneja la adición de un nuevo miembro del equipo
 * Valida los datos del formulario y llama a la acción del store
 * Cierra el modal y limpia el formulario al completar
 */
async function handleAddMember(): Promise<void> {
  try {
    // Validación básica de campos
    if (!newMember.value.name || !newMember.value.email) {
      console.warn('Nombre y correo son obligatorios')
      return
    }

    // Llamar acción del store para crear nuevo miembro
    await teamStore.addMember({
      name: newMember.value.name,
      email: newMember.value.email,
      specialty: newMember.value.specialty || 'Sin especificar',
      role: 'developer' // Los nuevos miembros siempre comienzan como desarrolladores
    })

    // Cerrar modal y limpiar formulario
    showAddForm.value = false
    newMember.value = {
      name: '',
      email: '',
      specialty: ''
    }
  } catch (error) {
    console.error('Error al agregar miembro:', error)
  }
}
</script>

<style scoped>
/**
 * Estilos locales para el componente MemberList
 * Todos los estilos están encapsulados y no afectan otros componentes
 */

/* Animación suave para transiciones de hover en filas */
tr {
  transition: background-color 0.2s ease-in-out;
}

/* Estilos específicos para botones de acción en cada fila */
button {
  transition: all 0.2s ease-in-out;
}

/* Efecto visual al pasar sobre avatares */
.avatar {
  transition: transform 0.2s ease-in-out;
}

.avatar:hover {
  transform: scale(1.05);
}
</style>
