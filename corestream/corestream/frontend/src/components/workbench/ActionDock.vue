<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Dock de Acciones (Crítico) -->
  <!-- ================================================================ -->
  <!-- Barra sticky con 3 botones principales para acciones en ticket -->
  <!-- Botones: Completar (con PR), Levantar Pregunta, Redireccionar -->
  <!-- Si ticket está bloqueado: muestra "Reanudar Trabajo" -->
  <!-- ================================================================ -->

  <div class="p-4 space-y-3">
    <!-- ================================================================ -->
    <!-- SECCIÓN: Estado Bloqueado (mutualmente excluyente) -->
    <!-- ================================================================ -->
    <!-- Si ticket está bloqueado, muestra botón para resolver problema -->
    <!-- ================================================================ -->
    <div v-if="ticket.status === 'BLOCKED'" class="space-y-3">
      <!-- Input de área para resolver pregunta -->
      <textarea
        v-model="resolutionText"
        placeholder="Describe cómo se resolvió el bloqueo..."
        maxlength="500"
        class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-400 focus:outline-none focus:border-blue-500 resize-none h-20"
      />

      <!-- Botón para reanudar trabajo -->
      <button
        @click="handleResolve"
        :disabled="resolutionText.trim().length < 10"
        class="w-full px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:check-circle" />
        Reanudar Trabajo
      </button>

      <!-- Separador visual -->
      <div class="border-t border-slate-700" />
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 1 - COMPLETAR -->
    <!-- ================================================================ -->
    <!-- Verde (#10B981) -->
    <!-- Requiere link de PR válido, deshabilitado si está bloqueado -->
    <!-- ================================================================ -->
    <div class="space-y-2">
      <!-- Label -->
      <label class="block text-xs font-semibold text-slate-300">
        Link Pull Request
      </label>

      <!-- Input para URL de PR -->
      <div class="flex gap-2">
        <input
          v-model="prUrl"
          type="url"
          placeholder="https://github.com/owner/repo/pull/123"
          class="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-400 focus:outline-none focus:border-blue-500"
        />
      </div>

      <!-- Botón completar -->
      <button
        @click="handleComplete"
        :disabled="!isValidPrUrl || ticket.status === 'BLOCKED'"
        :class="[
          'w-full px-4 py-3 bg-green-600 hover:bg-green-700 disabled:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed',
          'text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2'
        ]"
      >
        <Icon icon="mdi:check-circle" class="text-lg" />
        Completar
      </button>
    </div>

    <!-- Separador visual -->
    <div class="border-t border-slate-700" />

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 2 - LEVANTAR PREGUNTA -->
    <!-- ================================================================ -->
    <!-- Ámbar (#F59E0B) -->
    <!-- Bloquea el ticket, requiere mínimo 10 caracteres -->
    <!-- ================================================================ -->
    <div class="space-y-2">
      <!-- Label -->
      <label class="block text-xs font-semibold text-slate-300">
        Levantar Pregunta
      </label>

      <!-- Textarea para pregunta -->
      <textarea
        v-model="questionText"
        placeholder="¿Qué impide avanzar?"
        maxlength="500"
        :disabled="ticket.status === 'BLOCKED'"
        class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-400 focus:outline-none focus:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed resize-none h-20"
      />

      <!-- Indicador de caracteres -->
      <div class="text-xs text-slate-400">
        {{ questionText.length }}/500 caracteres (mínimo 10)
      </div>

      <!-- Botón levantar pregunta -->
      <button
        @click="handleQuestion"
        :disabled="questionText.trim().length < 10 || ticket.status === 'BLOCKED'"
        :class="[
          'w-full px-4 py-3 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-500 disabled:opacity-50 disabled:cursor-not-allowed',
          'text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2'
        ]"
      >
        <Icon icon="mdi:help-circle" class="text-lg" />
        Levantar Pregunta
      </button>

      <!-- Texto informativo -->
      <p class="text-xs text-amber-200">
        El ticket será bloqueado hasta que se resuelva la duda.
      </p>
    </div>

    <!-- Separador visual -->
    <div class="border-t border-slate-700" />

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 3 - REDIRECCIONAR -->
    <!-- ================================================================ -->
    <!-- Índigo (#6366F1) -->
    <!-- Abre popover con selector de usuario y razón -->
    <!-- ================================================================ -->
    <div class="space-y-2">
      <!-- Label -->
      <label class="block text-xs font-semibold text-slate-300">
        Redireccionar Ticket
      </label>

      <!-- Popover/Modal de redirección -->
      <div
        v-if="showRedirectPopover"
        class="bg-slate-700 border border-slate-600 rounded-lg p-3 space-y-3"
      >
        <!-- Buscador de usuario -->
        <div>
          <input
            v-model="redirectUserSearch"
            type="text"
            placeholder="Buscar usuario..."
            class="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500"
          />

          <!-- Lista de resultados -->
          <div v-if="filteredUsers.length > 0" class="mt-2 space-y-1 max-h-32 overflow-y-auto">
            <button
              v-for="user in filteredUsers"
              :key="user.id"
              @click="selectedRedirectUser = user"
              class="w-full flex items-center gap-2 px-2 py-1 hover:bg-slate-600 rounded text-left text-sm text-slate-200"
            >
              <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                {{ getInitials(user.name) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium truncate">{{ user.name }}</p>
                <p class="text-xs text-slate-400">{{ user.specialty }}</p>
              </div>
            </button>
          </div>
        </div>

        <!-- Usuario seleccionado -->
        <div v-if="selectedRedirectUser" class="flex items-center gap-2 p-2 bg-slate-600 rounded">
          <div class="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
            {{ getInitials(selectedRedirectUser.name) }}
          </div>
          <span class="text-sm text-white font-medium">{{ selectedRedirectUser.name }}</span>
          <button
            @click="selectedRedirectUser = null"
            class="ml-auto text-slate-400 hover:text-white"
          >
            <Icon icon="mdi:close" />
          </button>
        </div>

        <!-- Razón de redirección -->
        <textarea
          v-model="redirectReason"
          placeholder="¿Por qué se lo pasas?"
          maxlength="500"
          class="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500 resize-none h-16"
        />

        <!-- Indicador de caracteres -->
        <div class="text-xs text-slate-400">
          {{ redirectReason.length }}/500 caracteres (mínimo 10)
        </div>

        <!-- Botones de acción -->
        <div class="flex gap-2">
          <button
            @click="handleRedirect"
            :disabled="!selectedRedirectUser || redirectReason.trim().length < 10"
            class="flex-1 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold rounded transition-colors"
          >
            Confirmar
          </button>
          <button
            @click="closeRedirectPopover"
            class="flex-1 px-3 py-2 bg-slate-600 hover:bg-slate-500 text-white text-sm font-semibold rounded transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>

      <!-- Botón para abrir redirección (cuando popover cerrado) -->
      <button
        v-else
        @click="showRedirectPopover = true"
        :disabled="ticket.status === 'DONE'"
        class="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:arrow-right-circle" class="text-lg" />
        Redireccionar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useUsersStore } from '@/stores/users'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface User {
  id: string
  name: string
  specialty?: string
  avatar?: string
}

interface Ticket {
  id: string
  status: 'TODO' | 'IN_PROGRESS' | 'BLOCKED' | 'DONE'
}

// =====================================================================
// PROPS
// =====================================================================

const props = defineProps<{
  ticket: Ticket
}>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// URL del pull request
const prUrl = ref('')

// Texto de la pregunta siendo levantada
const questionText = ref('')

// Texto de resolución del bloqueo
const resolutionText = ref('')

// Control de mostrar popover de redirección
const showRedirectPopover = ref(false)

// Búsqueda de usuario para redirección
const redirectUserSearch = ref('')

// Usuario seleccionado para redirección
const selectedRedirectUser = ref<User | null>(null)

// Razón de redirección
const redirectReason = ref('')

// =====================================================================
// STORE Y DATOS
// =====================================================================

// Acceso al store de usuarios
const usersStore = useUsersStore()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Valida que la URL de PR sea válida
 * Soporta GitHub, GitLab, Bitbucket
 */
const isValidPrUrl = computed(() => {
  const url = prUrl.value.trim()
  if (url.length === 0) return false

  // Patrones para URLs válidas de PR
  const patterns = [
    /github\.com.*\/pull\/\d+/,
    /gitlab\.com.*\/merge_requests\/\d+/,
    /bitbucket\.org.*\/pull-requests\/\d+/
  ]

  return patterns.some(pattern => pattern.test(url))
})

/**
 * Filtra usuarios según búsqueda
 * Excluye al usuario actualmente asignado
 */
const filteredUsers = computed(() => {
  const query = redirectUserSearch.value.toLowerCase()

  return usersStore.allUsers.filter(user =>
    user.name.toLowerCase().includes(query)
  )
})

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

/**
 * Obtiene iniciales de un nombre
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
// MANEJADORES DE EVENTOS
// =====================================================================

/**
 * Maneja completación del ticket
 * Emite evento con URL de PR
 */
const handleComplete = () => {
  if (isValidPrUrl.value) {
    emit('complete', prUrl.value)
    prUrl.value = ''
  }
}

/**
 * Maneja levantamiento de pregunta
 * Valida mínimo de caracteres y emite evento
 */
const handleQuestion = () => {
  if (questionText.value.trim().length >= 10) {
    emit('question', questionText.value)
    questionText.value = ''
  }
}

/**
 * Maneja resolución de bloqueo
 * Emite evento para reanudar trabajo
 */
const handleResolve = () => {
  if (resolutionText.value.trim().length >= 10) {
    emit('resolve', resolutionText.value)
    resolutionText.value = ''
  }
}

/**
 * Maneja redirección del ticket
 * Valida usuario y razón, emite evento
 */
const handleRedirect = () => {
  if (selectedRedirectUser && redirectReason.value.trim().length >= 10) {
    emit('redirect', {
      toUserId: selectedRedirectUser.id,
      reason: redirectReason.value
    })

    // Limpiar estado
    closeRedirectPopover()
  }
}

/**
 * Cierra el popover de redirección
 * Limpia todos los campos
 */
const closeRedirectPopover = () => {
  showRedirectPopover.value = false
  redirectUserSearch.value = ''
  selectedRedirectUser.value = null
  redirectReason.value = ''
}

// =====================================================================
// EMITS
// =====================================================================

/**
 * Eventos emitidos por el componente ActionDock
 */
const emit = defineEmits<{
  complete: [prUrl: string]
  question: [questionText: string]
  redirect: [data: { toUserId: string; reason: string }]
  resolve: [resolution: string]
}>()
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>
