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
    <div v-if="ticket.status === TicketStatus.BLOCKED_QUESTION" class="space-y-3">
      <!-- Input de área para resolver pregunta -->
      <textarea
        v-model="resolutionText"
        placeholder="Describe cómo se resolvió el bloqueo..."
        maxlength="500"
        class="w-full px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] text-sm placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--lime)] resize-none h-20"
      />

      <!-- Botón para reanudar trabajo -->
      <button
        @click="handleResolve"
        :disabled="resolutionText.trim().length < 10"
        class="w-full px-4 py-2 bg-[var(--lime)] hover:bg-[var(--lime-90)] disabled:bg-[var(--lime)] disabled:opacity-50 disabled:cursor-not-allowed text-[var(--dark-gray)] font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:check-circle" />
        Reanudar Trabajo
      </button>

      <!-- Separador visual -->
      <div class="border-t border-[var(--border-subtle)]" />
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 0 - INICIAR TRABAJO (Solo para TODO) -->
    <!-- Color: Azul (#2563EB) -->
    <!-- ================================================================ -->
    <div v-if="ticket.status === TicketStatus.TODO" class="space-y-2 mb-4">
      <button
        @click="emit('start')"
        class="w-full px-4 py-3 bg-[var(--lime)] hover:bg-[var(--lime-90)] text-[var(--dark-gray)] font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg"
      >
        <Icon icon="mdi:play-circle" class="text-xl" />
        Comenzar Trabajo
      </button>

      <!-- Separador visual -->
      <div class="border-t border-[var(--border-subtle)] mt-4" />
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 1 - COMPLETAR -->
    <!-- ================================================================ -->
    <!-- Verde (#10B981) -->
    <!-- Requiere link de PR válido, deshabilitado si no hay PR -->
    <!-- ================================================================ -->
    <div v-if="ticket.status === TicketStatus.IN_PROGRESS" class="space-y-2">
      <!-- Botón completar (ahora usa prLink del ticket que viene de TicketSidePanel) -->
      <button
        data-cy="btn-completar"
        @click="handleComplete"
        :disabled="!isPrLinkValid"
        :class="[
          'w-full px-4 py-3 font-semibold rounded-lg transition-colors flex items-center justify-center gap-2',
          isPrLinkValid
            ? 'bg-[var(--lime)] hover:bg-[var(--lime-90)] text-[var(--dark-gray)]'
            : 'bg-[var(--bg-panel)] hover:bg-[var(--bg-panel)] disabled:opacity-50 disabled:cursor-not-allowed text-[var(--text-secondary)]'
        ]"
        :title="!isPrLinkValid ? 'Requiere PR válido en el campo de arriba' : 'Completar ticket'"
      >
        <Icon icon="mdi:check-circle" class="text-lg" />
        Completar Ticket
      </button>
      <p v-if="!isPrLinkValid" class="text-xs text-[var(--text-muted)]">
        ⚠️ Requiere PR válido
      </p>
    </div>

    <!-- Separador visual -->
    <div v-if="ticket.status === TicketStatus.IN_PROGRESS" class="border-t border-[var(--border-subtle)]" />

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 2 - LEVANTAR PREGUNTA -->
    <!-- ================================================================ -->
    <!-- Ámbar (#F59E0B) -->
    <!-- Bloquea el ticket, requiere mínimo 10 caracteres -->
    <!-- ================================================================ -->
    <div data-cy="pregunta-form" v-if="ticket.status === TicketStatus.IN_PROGRESS || ticket.status === TicketStatus.TODO" class="space-y-2">
      <!-- Label -->
      <label class="block text-xs font-semibold text-[var(--text-secondary)]">
        Levantar Pregunta
      </label>

      <!-- Textarea para pregunta -->
      <textarea
        data-cy="pregunta-textarea"
        v-model="questionText"
        placeholder="¿Qué impide avanzar?"
        maxlength="500"
        :disabled="(ticket.status as TicketStatus) === TicketStatus.BLOCKED_QUESTION"
        class="w-full px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] text-sm placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent-warm-2)] disabled:opacity-50 disabled:cursor-not-allowed resize-none h-20"
      />

      <!-- Indicador de caracteres -->
      <div class="text-xs text-[var(--text-muted)]">
        {{ questionText.length }}/500 caracteres (mínimo 10)
      </div>

      <!-- Botón levantar pregunta -->
      <button
        data-cy="btn-enviar-pregunta"
        @click="handleQuestion"
        :disabled="questionText.trim().length < 10 || (ticket.status as TicketStatus) === TicketStatus.BLOCKED_QUESTION"
        :class="[
          'w-full px-4 py-3 bg-[var(--accent-warm-2)] hover:bg-[var(--accent-warm-1)] disabled:bg-[var(--accent-warm-2)] disabled:opacity-50 disabled:cursor-not-allowed',
          'text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2'
        ]"
      >
        <Icon icon="mdi:help-circle" class="text-lg" />
        Levantar Pregunta
      </button>

      <!-- Texto informativo -->
      <p class="text-xs text-[var(--accent-warm-3)]">
        El ticket será bloqueado hasta que se resuelva la duda.
      </p>
    </div>

    <!-- Separador visual -->
    <div v-if="ticket.status === TicketStatus.IN_PROGRESS || ticket.status === TicketStatus.TODO" class="border-t border-[var(--border-subtle)]" />

    <!-- ================================================================ -->
    <!-- SECCIÓN: Botón 3 - REDIRECCIONAR -->
    <!-- ================================================================ -->
    <!-- Índigo (#6366F1) -->
    <!-- Abre popover con selector de usuario y razón -->
    <!-- ================================================================ -->
    <div v-if="ticket.status === TicketStatus.IN_PROGRESS || ticket.status === TicketStatus.TODO" class="space-y-2">
      <!-- Label -->
      <label class="block text-xs font-semibold text-[var(--text-secondary)]">
        Redireccionar Ticket
      </label>

      <!-- Popover/Modal de redirección -->
      <div
        v-if="showRedirectPopover"
        class="bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg p-3 space-y-3"
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
            class="flex-1 px-3 py-2 bg-accent-cold-2 hover:bg-accent-cold-1 text-white disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold rounded transition-colors"
          >
            Confirmar
          </button>
          <button
            @click="closeRedirectPopover"
            class="flex-1 px-3 py-2 bg-[var(--bg-panel)] hover:bg-[var(--bg-card)] text-[var(--text-primary)] text-sm font-semibold rounded transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>

      <!-- Botón para abrir redirección (cuando popover cerrado) -->
      <button
        v-else
        @click="showRedirectPopover = true"
        :disabled="(ticket.status as TicketStatus) === TicketStatus.COMPLETED"
        class="w-full px-4 py-3 bg-accent-cold-2 hover:bg-accent-cold-1 text-white disabled:opacity-50 disabled:cursor-not-allowed font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
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

import type { Ticket } from '@/types'
import { TicketStatus, NotificationType } from '@/types'
import { ref, computed, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'
import { useNotificationsStore } from '@/stores/notifications'

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

const props = defineProps<{
  ticket: Ticket
  isPrValid?: boolean
}>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

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

// Acceso al store de usuarios y autenticación
const authStore = useAuthStore()
const notificationStore = useNotificationsStore()

// Lista de miembros del equipo para redirección
const teamMembers = ref<User[]>([])

// Cargar miembros del equipo al montar el componente
onMounted(async () => {
  await loadTeamMembers()
})

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Valida que la URL de PR sea válida
 * Usa prLink del ticket (centralizado en TicketSidePanel)
 * Soporta GitHub, GitLab, Bitbucket
 */
const isPrLinkValid = computed(() => {
  // Ahora usamos directamente la validación que viene en tiempo real desde el panel padre
  return props.isPrValid ?? false
})

/**
 * Filtra usuarios según búsqueda
 * Excluye al usuario actualmente autenticado
 */
const filteredUsers = computed(() => {
  // Buscamos la variable que tiene el texto del input (asumiendo que se llama searchQuery)
  // Si tu variable se llama diferente (ej: search), cámbiala aquí:
  const query = (redirectUserSearch.value || '').toLowerCase()
  
  return teamMembers.value.filter((user: any) => 
    user.name.toLowerCase().includes(query) && 
    user.id !== authStore.user?.id
  )
})

// =====================================================================
// MÉTODOS DE API
// =====================================================================

/**
 * Carga los miembros del equipo desde la API
 */
const loadTeamMembers = async () => {
  try {
    const members = await api.tickets.getTeamMembers()
    teamMembers.value = members.map((member: any) => ({
      id: member.id,
      name: member.fullName || member.full_name,
      specialty: member.role,
      email: member.email
    }))
  } catch (error) {
    console.error('Error cargando miembros del equipo:', error)
    notificationStore.addNotification({
      userId: authStore.user?.id || '',
      id: `team-members-error-${Date.now()}`,
      title: 'Error',
      message: 'No se pudieron cargar los miembros del equipo',
      type: NotificationType.SYSTEM,
      createdAt: new Date().toISOString(),
      isRead: false
    })
  }
}

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
 * Emite evento con URL de PR del ticket
 */
const handleComplete = () => {
  if (isPrLinkValid.value) {
    const prUrl: string = props.ticket.prLink || ''
    emit('complete', prUrl)
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
 * Usa API backend para redirigir el ticket
 */
const handleRedirect = async () => {
  if (selectedRedirectUser.value && redirectReason.value.trim().length >= 10) {
    try {
      const response = await api.tickets.redirect(
        props.ticket.id,
        selectedRedirectUser.value.id,
        redirectReason.value
      )

      // Mostrar notificación de éxito
      notificationStore.addNotification({
        userId: authStore.user?.id || '',
        id: `redirect-success-${Date.now()}`,
        title: 'Ticket Redirigido',
        message: `Ticket redirigido exitosamente a ${selectedRedirectUser.value.name}`,
        type: NotificationType.STATUS_CHANGED,
        createdAt: new Date().toISOString(),
        isRead: false
      })

      // Emitir evento para actualizar el componente padre
      if (selectedRedirectUser.value) {
        emit('redirect', {
          toUserId: selectedRedirectUser.value.id,
          reason: redirectReason.value
        })
      }

      // Limpiar estado
      closeRedirectPopover()
    } catch (error: any) {
      console.error('Error redirigiendo ticket:', error)
      notificationStore.addNotification({
        userId: authStore.user?.id || '',
        id: `redirect-error-${Date.now()}`,
        title: 'Error',
        message: error.response?.data?.detail || 'No se pudo redirigir el ticket',
        type: NotificationType.SYSTEM,
        createdAt: new Date().toISOString(),
        isRead: false
      })
    }
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
  start: []
  complete: [prUrl: string]
  question: [questionText: string]
  redirect: [data: { toUserId: string; reason: string }]
  resolve: [resolution: string]
}>()
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>

