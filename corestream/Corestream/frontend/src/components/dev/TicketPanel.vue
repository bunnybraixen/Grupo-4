<template>
  <Teleport to="body">
  <!-- Overlay para cerrar -->
  <Transition name="fade">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black/30 z-40"
      @click="$emit('close')"
    />
  </Transition>

  <!-- Panel deslizante desde la derecha -->
  <Transition name="slide-right">
    <div
      v-if="isOpen && ticket"
      class="fixed right-0 top-[61px] h-[calc(100vh-61px)] w-[520px] bg-[var(--bg-card)] shadow-2xl z-50 flex flex-col overflow-hidden"
    >
      <!-- HEADER -->
      <div class="border-b border-[var(--border-subtle)] px-6 py-4 flex items-start justify-between">
        <div>
          <p class="text-xs text-[var(--text-muted)] mb-1">
            {{ ticket.appName }} › {{ ticket.epicTitle }}
          </p>
          <h2 class="text-lg font-bold text-[var(--text-primary)]">{{ ticket.title }}</h2>
        </div>
        <button
          @click="$emit('close')"
          class="text-[var(--text-muted)] hover:text-[var(--text-primary)] w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[var(--bg-card-hover)] transition-colors ml-4 flex-shrink-0"
        >
          ✕
        </button>
      </div>

      <!-- BODY (scrollable) -->
      <div class="flex-1 overflow-y-auto">
        <!-- Info general -->
        <div class="px-6 py-4 border-b border-[var(--border-subtle)]">
          <div class="flex gap-4 text-sm">
            <div>
              <span class="text-[var(--text-muted)] text-xs">Estado</span>
              <div class="mt-1">
                <span :class="statusBadgeClass">{{ statusLabel }}</span>
              </div>
            </div>
            <div>
              <span class="text-[var(--text-muted)] text-xs">Prioridad</span>
              <div class="mt-1">
                <span :class="priorityBadgeClass">{{ priorityLabel }}</span>
              </div>
            </div>
            <div v-if="ticket.dueDate">
              <span class="text-[var(--text-muted)] text-xs">Vence</span>
              <p class="mt-1 text-sm font-medium" :class="isOverdue ? 'text-[var(--priority-urg-bg)]' : 'text-[var(--text-primary)]'">
                {{ formatDate(ticket.dueDate) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Timer -->
        <div class="px-6 py-4 border-b border-[var(--border-subtle)]">
          <div class="bg-[var(--teal)] rounded-xl px-6 py-4 flex items-center gap-4">
            <span class="text-white text-2xl">⏱</span>
            <div>
              <p class="text-white/70 text-xs font-medium">Tiempo en este ticket</p>
              <p class="text-white text-3xl font-bold font-mono tracking-wider">{{ formattedTime }}</p>
            </div>
          </div>
        </div>

        <!-- PR Link -->
        <div class="px-6 py-4 border-b border-[var(--border-subtle)]">
          <label class="block text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2">
            Enlace del Pull Request
          </label>
          <input
            data-cy="pr-link-input"
            v-model="prLink"
            @blur="savePrLink"
            type="url"
            placeholder="https://github.com/owner/repo/pull/123"
            class="w-full bg-[var(--bg-input)] border rounded-xl px-4 py-2.5 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 transition-colors"
            :class="prLinkValid
              ? 'border-[var(--teal)] focus:ring-[var(--teal)]/20'
              : prLink
                ? 'border-[var(--priority-urg-bg)] focus:ring-[var(--priority-urg-bg)]/20'
                : 'border-[var(--border-subtle)] focus:border-[var(--teal)] focus:ring-[var(--teal)]/20'"
          />
          <p v-if="prLink && !prLinkValid" class="text-xs text-[var(--priority-urg-bg)] mt-1">
            ⚠ Debe ser un enlace válido de GitHub, GitLab o Bitbucket
          </p>
          <p v-if="prLinkValid" class="text-xs text-[var(--teal)] mt-1">
            ✓ Enlace válido
          </p>
        </div>

        <!-- Subtareas -->
        <div class="px-6 py-4 border-b border-[var(--border-subtle)]">
          <SubtaskChecklist
            :subtasks="localSubtasks"
            :ticket-id="ticket.id"
            @create="handleSubtaskCreate"
            @update="handleSubtaskUpdate"
            @delete="handleSubtaskDelete"
            @promote="handleSubtaskPromote"
          />
        </div>
      </div>

      <!-- ACTION DOCK (footer) -->
      <div class="border-t border-[var(--border-subtle)] bg-[var(--bg-card)] px-6 py-4">
        <!-- Acciones de ejecución: solo para Developer / Team Leader -->
        <template v-if="!authStore.isAdmin">
          <!-- Comenzar (si está en TODO) -->
          <button
            v-if="ticket?.status === 'TODO'"
            @click="handleStart"
            :disabled="isStarting"
            class="w-full flex items-center justify-center gap-2 font-bold py-3 rounded-xl transition-all duration-200 mb-3 bg-[var(--teal)] text-white hover:opacity-90 cursor-pointer"
          >
            <span>▶</span>
            <span>{{ isStarting ? 'Iniciando...' : 'Comenzar Ticket' }}</span>
          </button>

          <!-- Completar (si está en IN_PROGRESS) -->
          <button
            data-cy="btn-completar"
            v-if="ticket?.status === 'IN_PROGRESS'"
            @click="handleComplete"
            :disabled="!prLinkValid || isCompleting"
            class="w-full flex items-center justify-center gap-2 font-bold py-3 rounded-xl transition-all duration-200 mb-3"
            :class="prLinkValid
              ? 'bg-[var(--lime)] text-[var(--dark-gray)] hover:brightness-95 cursor-pointer'
              : 'bg-[var(--bg-panel)] text-[var(--text-muted)] cursor-not-allowed opacity-60'"
          >
            <span>✓</span>
            <span>{{ isCompleting ? 'Completando...' : 'Completar Ticket' }}</span>
          </button>
          <p v-if="ticket?.status === 'IN_PROGRESS' && !prLinkValid" class="text-xs text-[var(--text-muted)] text-center mb-3">
            ⚠ Requiere PR válido para completar
          </p>

          <div class="grid grid-cols-2 gap-3">
            <!-- Preguntar (activo en IN_PROGRESS y TODO) -->
            <button
              @click="showQuestionForm = !showQuestionForm"
              :disabled="ticket?.status !== 'IN_PROGRESS' && ticket?.status !== 'TODO'"
              :class="ticket?.status === 'IN_PROGRESS' || ticket?.status === 'TODO'
                ? 'bg-purple-500 text-white hover:bg-purple-600 cursor-pointer'
                : 'bg-[var(--bg-panel)] text-[var(--text-muted)] border border-[var(--border-subtle)] cursor-not-allowed opacity-60'"
              class="w-full flex items-center justify-center gap-2 font-semibold py-2.5 rounded-xl transition-colors"
            >
              <span>❓</span>
              <span class="text-sm">{{ ticket?.status === 'BLOCKED_QUESTION' ? 'Pendiente' : 'Preguntar' }}</span>
            </button>

            <!-- Redireccionar -->
            <button
              @click="showRedirectModal = true"
              :disabled="ticket?.status !== 'TODO' && ticket?.status !== 'IN_PROGRESS'"
              :class="ticket?.status === 'TODO' || ticket?.status === 'IN_PROGRESS'
                ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
                : 'bg-[var(--bg-panel)] text-[var(--text-muted)] border border-[var(--border-subtle)] cursor-not-allowed opacity-60'"
              class="w-full flex items-center justify-center gap-2 font-semibold py-2.5 rounded-xl transition-colors"
            >
              <span>↪</span>
              <span class="text-sm">Redireccionar</span>
            </button>
          </div>
        </template>

        <!-- Mini-form de pregunta -->
        <Transition name="slide-down">
          <div v-if="showQuestionForm" data-cy="pregunta-form" class="mt-3 p-4 bg-[var(--bg-panel)] rounded-xl border border-[var(--border-subtle)]">
            <label class="text-xs font-semibold text-[var(--text-secondary)] mb-2 block">¿Qué impide avanzar?</label>
            <textarea
              data-cy="pregunta-textarea"
              v-model="questionText"
              rows="3"
              placeholder="Describe tu duda (mínimo 10 caracteres)..."
              class="w-full bg-[var(--bg-input)] border border-[var(--border-subtle)] rounded-xl px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)] resize-none"
            />
            <div class="flex items-center justify-between mt-2">
              <span class="text-xs text-[var(--text-muted)]">{{ questionText.length }}/500 caracteres</span>
              <div class="flex gap-2">
                <button @click="showQuestionForm = false; questionText = ''" class="text-xs px-3 py-1.5 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)]">
                  Cancelar
                </button>
                <button
                  data-cy="btn-enviar-pregunta"
                  @click="handleQuestion"
                  :disabled="questionText.length < 10 || isQuestioning"
                  class="text-xs px-3 py-1.5 rounded-lg font-semibold transition-colors"
                  :class="questionText.length >= 10
                    ? 'bg-purple-500 text-white hover:bg-purple-600 cursor-pointer'
                    : 'bg-[var(--bg-tag)] text-[var(--text-muted)] cursor-not-allowed'"
                >
                  {{ isQuestioning ? 'Enviando...' : 'Enviar' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>

  <!-- Modal de Redirección -->
  <div
    v-if="showRedirectModal"
      class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4"
    >
      <div class="bg-[var(--bg-card)] rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h3 class="text-base font-bold text-[var(--text-primary)] mb-4">↪ Redireccionar Ticket</h3>

        <!-- Selector de developer -->
        <label class="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2 block">
          Seleccionar Desarrollador
        </label>

        <!-- Búsqueda BUG #8 -->
        <input
          v-model="redirectSearch"
          type="text"
          placeholder="Buscar por nombre o email..."
          class="w-full mb-2 px-3 py-2 text-sm bg-[var(--bg-input)] border border-[var(--border-subtle)] rounded-xl text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)]"
        />

        <div class="space-y-2 max-h-44 overflow-y-auto mb-4">
          <p v-if="filteredDevelopers.length === 0" class="text-xs text-[var(--text-muted)] text-center py-2">
            Sin resultados
          </p>
          <button
            v-for="dev in filteredDevelopers"
            :key="dev.id"
            @click="selectedRedirectDev = dev.id"
            class="w-full flex items-center gap-3 p-3 rounded-xl border transition-colors text-left"
            :class="selectedRedirectDev === dev.id
              ? 'border-[var(--teal)] bg-[var(--bg-card-hover)]'
              : 'border-[var(--border-subtle)] hover:bg-[var(--bg-card-hover)]'"
          >
            <div class="w-8 h-8 rounded-full bg-[var(--teal)] flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {{ (dev.fullName || dev.name || '?').slice(0, 2).toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <span class="text-sm font-medium text-[var(--text-primary)]">{{ dev.fullName || dev.name }}</span>
              <p v-if="dev.email" class="text-xs text-[var(--text-muted)] truncate">{{ dev.email }}</p>
            </div>
          </button>
        </div>

        <!-- Campo de contexto -->
        <label class="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-2 block">
          Motivo de la redirección
        </label>
        <textarea
          v-model="redirectContext"
          rows="3"
          placeholder="Explica por qué (mínimo 10 caracteres)..."
          class="w-full bg-[var(--bg-input)] border border-[var(--border-subtle)] rounded-xl px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--teal)] resize-none mb-1"
        />
        <p class="text-xs text-[var(--text-muted)] mb-4">{{ redirectContext.length }}/500</p>

        <div class="flex gap-3">
          <button
            @click="showRedirectModal = false; selectedRedirectDev = null; redirectContext = ''; redirectSearch = ''"
            class="flex-1 py-2.5 rounded-xl border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)] font-medium text-sm transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="handleRedirect"
            :disabled="!selectedRedirectDev || redirectContext.length < 10 || isRedirecting"
            class="flex-1 py-2.5 rounded-xl font-bold text-sm transition-colors"
            :class="selectedRedirectDev && redirectContext.length >= 10
              ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
              : 'bg-[var(--bg-panel)] text-[var(--text-muted)] cursor-not-allowed'"
          >
            {{ isRedirecting ? 'Redireccionando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>

  <!-- Toast de éxito al promover subtarea -->
  <Transition name="fade">
    <div
      v-if="promoteToast"
      class="fixed bottom-6 right-6 z-[200] bg-[var(--teal)] text-white text-sm font-medium px-4 py-3 rounded-xl shadow-xl flex items-center gap-2"
    >
      ✓ Subtarea convertida en ticket exitosamente.
    </div>
  </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { api } from '@/services/api'
import { useTicketsStore } from '@/stores/tickets'
import { useAuthStore } from '@/stores/auth'
import { useDialogStore } from '@/stores/dialog'
import SubtaskChecklist from '@/components/workbench/SubtaskChecklist.vue'
import type { Ticket } from '@/types'

const props = defineProps<{
  ticket: Ticket | null
  isOpen: boolean
  developers?: any[]
}>()

const emit = defineEmits<{
  close: []
  updated: [ticketId: string]
}>()

const ticketsStore = useTicketsStore()
const authStore = useAuthStore()
const dialogStore = useDialogStore()

// Estado local
const prLink = ref('')
const showQuestionForm = ref(false)
const questionText = ref('')
const showRedirectModal = ref(false)
const selectedRedirectDev = ref<string | null>(null)
const redirectContext = ref('')
const redirectSearch = ref('')
const localSubtasks = ref<any[]>([])

// Developers available for redirection: exclude ADMINs (frontend guard)
const filteredDevelopers = computed(() => {
  const nonAdmins = (props.developers ?? []).filter(
    (d: any) => !['ADMIN', 'SUPERADMIN'].includes((d.role ?? '').toUpperCase())
  )
  const q = redirectSearch.value.trim().toLowerCase()
  if (!q) return nonAdmins
  return nonAdmins.filter((d: any) =>
    (d.fullName || d.name || '').toLowerCase().includes(q) ||
    (d.email || '').toLowerCase().includes(q)
  )
})

// Toast
const promoteToast = ref(false)
const showPromoteToast = () => {
  promoteToast.value = true
  setTimeout(() => { promoteToast.value = false }, 3000)
}

// Estados de carga
const isStarting = ref(false)
const isCompleting = ref(false)
const isQuestioning = ref(false)
const isRedirecting = ref(false)

// Timer
const elapsedSeconds = ref(0)
let timerInterval: ReturnType<typeof setInterval> | null = null

// Developers list
const developers = ref<any[]>(props.developers || [])

const PLACEHOLDER_PR = /github\.com\/owner\/repo\/|gitlab\.com\/owner\/repo\/|bitbucket\.org\/owner\/repo\//

// Computed
const prLinkValid = computed(() => {
  if (!prLink.value) return false
  if (PLACEHOLDER_PR.test(prLink.value)) return false
  const patterns = [
    /^https:\/\/github\.com\/.+\/pull\/\d+/,
    /^https:\/\/gitlab\.com\/.+\/merge_requests\/\d+/,
    /^https:\/\/bitbucket\.org\/.+\/pull-requests\/\d+/,
  ]
  return patterns.some(p => p.test(prLink.value))
})

const formattedTime = computed(() => {
  const h = Math.floor(elapsedSeconds.value / 3600)
  const m = Math.floor((elapsedSeconds.value % 3600) / 60)
  const s = elapsedSeconds.value % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const isOverdue = computed(() => {
  if (!props.ticket?.dueDate) return false
  return new Date(props.ticket.dueDate) < new Date()
})

const statusLabel = computed(() => {
  const map: Record<string, string> = {
    TODO: 'Por Hacer',
    IN_PROGRESS: 'En Progreso',
    COMPLETED: 'Completado',
    DONE: 'Completado',
    BLOCKED: 'Bloqueado',
    BLOCKED_QUESTION: 'Bloqueado',
    REDIRECTED: 'Redirigido',
  }
  return map[props.ticket?.status || ''] || props.ticket?.status
})

const priorityLabel = computed(() => {
  const map: Record<string, string> = {
    LOW: 'Baja',
    MEDIUM: 'Media',
    HIGH: 'Alta',
    CRITICAL: 'Crítica',
    URGENT: 'Urgente',
  }
  return map[props.ticket?.priority || ''] || props.ticket?.priority
})

const statusBadgeClass = computed(() => {
  const map: Record<string, string> = {
    TODO: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]',
    IN_PROGRESS: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--teal)] text-white',
    BLOCKED: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-urg-bg)] text-white animate-pulse',
    BLOCKED_QUESTION: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-urg-bg)] text-white animate-pulse',
    REDIRECTED: 'px-2 py-0.5 rounded-full text-xs font-medium bg-indigo-500 text-white',
    DONE: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--lime)] text-[var(--dark-gray)]',
  }
  return map[props.ticket?.status || ''] || ''
})

const priorityBadgeClass = computed(() => {
  const map: Record<string, string> = {
    LOW: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-low-bg)] text-white',
    MEDIUM: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-med-bg)] text-white',
    HIGH: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-high-bg)] text-white',
    URGENT: 'px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--priority-urg-bg)] text-white animate-pulse',
  }
  return map[props.ticket?.priority || ''] || ''
})

// Funciones
function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' })
}



async function handleSubtaskCreate(title: string) {
  if (!props.ticket?.id) return
  try {
    const newSubtask = await ticketsStore.createSubtask(props.ticket.id, title)
    localSubtasks.value.push(newSubtask)
  } catch (error) {
    console.error('Error creating subtask:', error)
    dialogStore.alert('No se pudo crear la subtarea. Intenta de nuevo.')
  }
}

async function handleSubtaskUpdate(subtask: any) {
  if (!props.ticket?.id) return
  const index = localSubtasks.value.findIndex(s => s.id === subtask.id)
  if (index === -1) return
  const previous = { ...localSubtasks.value[index] }
  localSubtasks.value[index] = { ...localSubtasks.value[index], ...subtask }
  try {
    const updated = await ticketsStore.updateSubtask(props.ticket.id, subtask.id, {
      title: subtask.title,
      isCompleted: subtask.isCompleted,
    })
    localSubtasks.value[index] = updated
  } catch {
    localSubtasks.value[index] = previous
  }
}

async function handleSubtaskDelete(subtaskId: string) {
  if (!props.ticket?.id) return
  try {
    await ticketsStore.deleteSubtask(props.ticket.id, subtaskId)
    localSubtasks.value = localSubtasks.value.filter(s => s.id !== subtaskId)
  } catch (error) { console.error('Error deleting subtask:', error) }
}

async function handleSubtaskPromote(subtask: any) {
  if (!props.ticket?.id) return
  try {
    await ticketsStore.create({ epicId: props.ticket.epicId, title: subtask.title, priority: 'MEDIUM' })
    await ticketsStore.deleteSubtask(props.ticket.id, subtask.id)
    localSubtasks.value = localSubtasks.value.filter(s => s.id !== subtask.id)
    emit('updated', props.ticket.id)
    showPromoteToast()
  } catch (error) { console.error('Error promoting subtask:', error) }
}

async function savePrLink() {
  if (!props.ticket?.id || !prLink.value) return
  try {
    await api.tickets.update(props.ticket.id, { prLink: prLink.value })
  } catch (e) {
    console.error('Error saving PR link:', e)
  }
}

async function handleStart() {
  if (!props.ticket?.id || isStarting.value) return
  isStarting.value = true
  try {
    await ticketsStore.startWorking(props.ticket.id)
    emit('updated', props.ticket.id)
  } catch (e) {
    console.error('Error starting ticket:', e)
  } finally {
    isStarting.value = false
  }
}

async function handleComplete() {
  if (!prLinkValid.value || !props.ticket?.id || isCompleting.value) return
  isCompleting.value = true
  try {
    await ticketsStore.completeTicket(props.ticket.id, prLink.value)
    emit('updated', props.ticket.id)
    emit('close')
  } catch (e) {
    console.error('Error completing ticket:', e)
  } finally {
    isCompleting.value = false
  }
}

async function handleQuestion() {
  if (!props.ticket?.id || questionText.value.length < 10 || isQuestioning.value) return
  isQuestioning.value = true
  try {
    // Try different API methods for asking a question
    if (api.tickets.question) {
      await api.tickets.question(props.ticket.id, questionText.value)
    } else {
      // Fallback: use update with blockedQuestion
      await api.tickets.update(props.ticket.id, { blockedQuestion: questionText.value })
    }
    showQuestionForm.value = false
    questionText.value = ''
    emit('updated', props.ticket.id)
  } catch (e) {
    console.error('Error asking question:', e)
  } finally {
    isQuestioning.value = false
  }
}

async function handleRedirect() {
  if (!selectedRedirectDev.value || !props.ticket?.id || redirectContext.value.length < 10 || isRedirecting.value) return
  isRedirecting.value = true
  try {
    await api.tickets.redirect(props.ticket.id, {
      toUserId: selectedRedirectDev.value,
      reason: redirectContext.value,
    })
    showRedirectModal.value = false
    selectedRedirectDev.value = null
    redirectContext.value = ''
    redirectSearch.value = ''
    emit('updated', props.ticket.id)
    emit('close')
  } catch (e) {
    console.error('Error redirecting:', e)
  } finally {
    isRedirecting.value = false
  }
}

function startTimer() {
  if (timerInterval) clearInterval(timerInterval)
  if (props.ticket?.status === 'IN_PROGRESS') {
    const accumulated = props.ticket.timeSpentSeconds || 0
    if (props.ticket.timerStartedAt) {
      // Timer activo en servidor: recalcular desde el timestamp de inicio
      const sessionElapsed = Math.floor((Date.now() - new Date(props.ticket.timerStartedAt).getTime()) / 1000)
      elapsedSeconds.value = accumulated + Math.max(0, sessionElapsed)
    } else {
      elapsedSeconds.value = accumulated
    }
    timerInterval = setInterval(() => {
      elapsedSeconds.value++
    }, 1000)
  } else {
    elapsedSeconds.value = props.ticket?.timeSpentSeconds || 0
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

// Watchers
watch(
  () => props.ticket,
  (newTicket) => {
    if (newTicket) {
      prLink.value = newTicket.prLink || ''
      showQuestionForm.value = newTicket.status === 'IN_PROGRESS'
      localSubtasks.value = [...(newTicket.subtasks || [])]
      startTimer()
      if (props.developers?.length) {
        developers.value = props.developers
      }
    }
  },
  { immediate: true }
)

watch(
  () => props.developers,
  (newDevs) => {
    if (newDevs?.length) developers.value = newDevs
  }
)

watch(() => props.isOpen, (open) => {
  if (!open) {
    if (timerInterval) clearInterval(timerInterval)
    showQuestionForm.value = false
    showRedirectModal.value = false
  }
})

onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
