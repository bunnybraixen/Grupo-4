<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Modal para Redireccionar Ticket -->
  <!-- ================================================================ -->
  <!-- Modal overlay para redireccionar ticket a otro usuario -->
  <!-- Incluye: selector de usuario, razón, confirmación -->
  <!-- Validación: usuario seleccionado y razón de mínimo 10 caracteres -->
  <!-- ================================================================ -->

  <Transition name="fade-modal">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <!-- ================================================================ -->
      <!-- CONTENEDOR: Modal -->
      <!-- ================================================================ -->
      <div class="bg-slate-800 rounded-lg shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        <!-- ================================================================ -->
        <!-- SECCIÓN: Encabezado -->
        <!-- ================================================================ -->
        <div class="p-6 space-y-2 bg-slate-750 border-b border-slate-700">
          <!-- Ícono de redirección -->
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-full bg-indigo-900 bg-opacity-50 flex items-center justify-center flex-shrink-0">
              <Icon icon="mdi:arrow-right-circle" class="text-indigo-400 text-lg" />
            </div>
          </div>

          <!-- Título -->
          <h2 class="text-lg font-bold text-white">
            Redireccionar Ticket
          </h2>

          <!-- Subtítulo -->
          <p class="text-sm text-slate-400">
            Asigna este ticket a otro miembro del equipo
          </p>
        </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Contenido Principal -->
        <!-- ================================================================ -->
        <div class="p-6 space-y-4">
          <!-- Información del ticket -->
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-700">
            <p class="text-xs text-slate-400 mb-1">Ticket</p>
            <p class="text-sm font-medium text-white truncate">
              {{ ticketTitle }}
            </p>
          </div>

          <!-- ================================================================ -->
          <!-- SUB-SECCIÓN: Selector de Usuario -->
          <!-- ================================================================ -->
          <div>
            <label class="block text-sm font-semibold text-white mb-2">
              Asignar a
            </label>

            <!-- Input de búsqueda -->
            <div class="relative mb-2">
              <input
                v-model="userSearch"
                type="text"
                placeholder="Buscar usuario..."
                class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
              />
              <Icon
                icon="mdi:magnify"
                class="absolute right-3 top-2.5 text-slate-400 pointer-events-none"
              />
            </div>

            <!-- Lista de resultados de búsqueda -->
            <div
              v-if="filteredUsers.length > 0"
              class="max-h-40 overflow-y-auto bg-slate-700 rounded-lg border border-slate-600 mb-3"
            >
              <button
                v-for="user in filteredUsers"
                :key="user.id"
                @click="selectUser(user)"
                class="w-full p-2 hover:bg-slate-600 transition-colors flex items-center gap-2 border-b border-slate-600 last:border-b-0"
              >
                <!-- Avatar del usuario -->
                <div
                  class="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                >
                  {{ getInitials(user.name) }}
                </div>

                <!-- Información del usuario -->
                <div class="flex-1 text-left min-w-0">
                  <p class="text-sm font-medium text-white truncate">{{ user.name }}</p>
                  <p v-if="user.specialty" class="text-xs text-slate-400">
                    {{ user.specialty }}
                  </p>
                </div>
              </button>
            </div>

            <!-- Usuario seleccionado -->
            <div v-if="selectedUser" class="p-2 bg-indigo-900 bg-opacity-30 border border-indigo-700 rounded-lg flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div
                  class="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                >
                  {{ getInitials(selectedUser.name) }}
                </div>
                <span class="text-sm font-medium text-white">{{ selectedUser.name }}</span>
              </div>
              <button
                @click="selectedUser = null; userSearch = ''"
                class="text-slate-400 hover:text-white"
              >
                <Icon icon="mdi:close" />
              </button>
            </div>
          </div>

          <!-- ================================================================ -->
          <!-- SUB-SECCIÓN: Razón de Redirección -->
          <!-- ================================================================ -->
          <div>
            <label class="block text-sm font-semibold text-white mb-2">
              Razón
            </label>
            <textarea
              v-model="reasonText"
              placeholder="¿Por qué se lo pasas?"
              maxlength="500"
              rows="3"
              class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none"
            />

            <!-- Contador de caracteres -->
            <div class="flex justify-between mt-2">
              <span class="text-xs text-slate-400">
                Mínimo 10 caracteres para continuar
              </span>
              <span :class="[
                'text-xs font-medium',
                reasonText.length >= 10
                  ? 'text-green-400'
                  : 'text-slate-400'
              ]">
                {{ reasonText.length }}/500
              </span>
            </div>
          </div>
        </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Footer con Botones -->
        <!-- ================================================================ -->
        <div class="p-4 bg-slate-750 border-t border-slate-700 flex gap-2">
          <!-- Botón cancelar -->
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            Cancelar
          </button>

          <!-- Botón confirmar -->
          <button
            @click="handleSubmit"
            :disabled="!selectedUser || reasonText.trim().length < 10"
            :class="[
              'flex-1 px-4 py-2 font-semibold rounded-lg transition-colors',
              selectedUser && reasonText.trim().length >= 10
                ? 'bg-indigo-600 hover:bg-indigo-700 text-white'
                : 'bg-indigo-600 opacity-50 cursor-not-allowed text-white'
            ]"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  </Transition>
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

interface User {
  id: string
  name: string
  specialty?: string
  avatar?: string
}

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  isOpen: boolean
  ticketTitle: string
  availableUsers: User[]
}

const props = defineProps<Props>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Búsqueda de usuario
const userSearch = ref('')

// Usuario seleccionado para redirección
const selectedUser = ref<User | null>(null)

// Texto de razón de redirección
const reasonText = ref('')

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Filtra usuarios según búsqueda
 * Excluye al usuario seleccionado de resultados
 */
const filteredUsers = computed(() => {
  const query = userSearch.value.toLowerCase()

  return props.availableUsers.filter(user =>
    user.name.toLowerCase().includes(query) && (!selectedUser.value || user.id !== selectedUser.value.id)
  )
})

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Obtiene iniciales de un nombre
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

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Selecciona un usuario de la lista
 * Limpia la búsqueda
 * @param user - Usuario seleccionado
 */
const selectUser = (user: User) => {
  selectedUser.value = user
  userSearch.value = ''
}

/**
 * Maneja el envío de redirección
 * Valida usuario y razón
 * Emite evento con datos de redirección
 */
const handleSubmit = () => {
  // Validación
  if (!selectedUser.value || reasonText.value.trim().length < 10) {
    return
  }

  // Emitir evento con datos de redirección
  emit('submit', {
    toUserId: selectedUser.value.id,
    reason: reasonText.value
  })

  // Limpiar estado
  selectedUser.value = null
  reasonText.value = ''
  userSearch.value = ''
}

// =====================================================================
// EMITS
// =====================================================================

/**
 * Eventos emitidos por el componente RedirectModal
 */
const emit = defineEmits<{
  close: []
  submit: [data: { toUserId: string; reason: string }]
}>()
</script>

<style scoped>
/* ================================================================ */
/* TRANSICIONES */
/* ================================================================ */

/* Transición de fade para el modal */
.fade-modal-enter-active,
.fade-modal-leave-active {
  transition: opacity 0.3s ease;
}

.fade-modal-enter-from,
.fade-modal-leave-to {
  opacity: 0;
}

/* Escala del modal durante transición */
.fade-modal-enter-active {
  & > div {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    transform: scale(1);
  }
}

.fade-modal-enter-from > div {
  transform: scale(0.95);
}
</style>
