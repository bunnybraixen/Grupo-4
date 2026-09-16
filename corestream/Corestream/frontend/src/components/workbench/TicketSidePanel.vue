<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Panel Lateral de Ticket (Lado Derecho) -->
  <!-- ================================================================ -->
  <!-- Panel deslizable desde la derecha que muestra detalles del ticket -->
  <!-- Incluye: encabezado con timer, descripción, subtareas, actividad -->
  <!-- Footer con acciones: Completar, Levantar Pregunta, Redireccionar -->
  <!-- ================================================================ -->
  <Teleport to="body">
    <Transition name="slide-right">
      <div
        v-if="isOpen"
        class="fixed top-[61px] bottom-0 right-0 w-2/5 min-w-[400px] bg-[var(--bg-card)] shadow-2xl overflow-hidden flex flex-col z-50"
      >
        <!-- ================================================================ -->
        <!-- SECCIÓN: Encabezado (Sticky) -->
        <!-- ================================================================ -->
        <!-- Breadcrumbs, título, asignado y timer -->
        <!-- ================================================================ -->
        <div class="relative flex-shrink-0 p-6 border-b border-[var(--border-subtle)] space-y-3">
          <!-- Botón cerrar en esquina superior derecha -->
          <div class="absolute top-4 right-4 z-10">
            <button
              @click="handleClose"
              class="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] rounded-lg transition-colors"
              aria-label="Cerrar panel"
            >
              <Icon icon="mdi:close" class="text-xl" />
            </button>
          </div>

          <!-- Breadcrumbs: Aplicación > Épica > Ticket -->
          <div class="flex items-center gap-1 text-xs text-[var(--text-muted)]">
            <span>{{ ticket.appName  || 'App' }}</span>
            <Icon icon="mdi:chevron-right" class="inline" />
            <span>{{ ticket.epicTitle || 'Épica' }}</span>
            <Icon icon="mdi:chevron-right" class="inline" />
            <span class="text-[var(--teal)] font-semibold">T-{{ ticket.id.substring(0, 8) }}</span>
          </div>

          <input
            v-model="editedTitle"
            @keydown.enter="saveTicket"
            @blur="saveTicket"
            class="w-full text-2xl font-bold bg-transparent text-[var(--text-primary)] border-b border-transparent hover:border-[var(--border-subtle)] focus:border-[var(--lime)] focus:outline-none transition-colors pr-8 mb-2"
            placeholder="Título del ticket..."
          />

          <div class="flex items-center gap-3 pt-2">
            <div
              v-if="editedAssignee && selectedAssigneeMember"
              class="w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center text-sm font-bold bg-[var(--teal)] text-[var(--text-primary)]"
              :title="selectedAssigneeMember.fullName"
            >
              {{ getInitials(selectedAssigneeMember) }}
            </div>

            <select
              v-if="isAdminOrLeader"
              v-model="editedAssignee"
              @change="saveAssignee"
              class="text-sm bg-[var(--bg-panel)] text-[var(--text-secondary)] border border-[var(--border-subtle)] rounded-md px-2 py-1.5 focus:outline-none focus:border-[var(--lime)] cursor-pointer hover:bg-[var(--bg-input)] transition-colors truncate max-w-[160px]"
            >
              <option :value="null">Sin asignar</option>
              <option v-for="member in teamMembers" :key="member.id" :value="member.id">
                {{ member.fullName }}
              </option>
            </select>
            <span v-else class="text-sm text-[var(--text-secondary)] truncate max-w-[150px]">
              {{ ticket.assignee ? getAssigneeName(ticket.assignee) : 'Sin asignar' }}
            </span>

            <div class="flex items-center gap-1.5 ml-2">
              <!-- Mismo mapeo de color que las tarjetas del Workbench (WorkbenchTicketCard),
                   para que la prioridad se vea igual dentro y fuera del ticket. -->
              <span
                :class="['w-2.5 h-2.5 rounded-full flex-shrink-0', priorityDotClass]"
                :title="`Prioridad: ${editedPriority}`"
              />
              <select
                v-model="editedPriority"
                @change="saveTicket"
                class="text-xs font-semibold bg-[var(--bg-panel)] text-[var(--text-secondary)] border border-[var(--border-subtle)] rounded-md px-2 py-1.5 focus:outline-none focus:border-[var(--lime)] cursor-pointer hover:bg-[var(--bg-input)] transition-colors"
              >
                <option value="LOW">Baja</option>
                <option value="MEDIUM">Media</option>
                <option value="HIGH">Alta</option>
                <option value="URGENT">Urgente</option>
              </select>
            </div>

            <div class="flex-1" />

            <TimeTracker
              :work-seconds="totalWorkSeconds"
              :blocked-seconds="totalBlockedSeconds"
              :is-working="isWorking"
              :is-blocked="isBlockedTimer"
            />
          </div>
          <div v-if="(currentStatus === 'COMPLETED' || ticket.status === 'COMPLETED') && (editedPrLink || ticket.prLink)">
            <div class="flex items-center gap-2">
              <span class="text-xl">✅</span>
              <div class="overflow-hidden">
                <p class="text-sm font-bold text-[var(--teal)]">Pull Request Vinculado</p>
                <a 
                  :href="editedPrLink" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  class="text-xs text-blue-500 hover:underline truncate block"
                >
                  {{ editedPrLink }}
                </a>
              </div>
            </div>
          </div>
          </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Contenido Principal (Scrollable) -->
        <!-- ================================================================ -->
        <!-- Descripción, subtareas, y log de actividad -->
        <!-- ================================================================ -->
        <div class="flex-1 overflow-y-auto">
          <!-- ================================================================ -->
          <!-- SUB-SECCIÓN: Descripción -->
          <!-- ================================================================ -->
          <div class="p-6 border-b border-[var(--border-subtle)]">
            <div class="flex justify-between items-center mb-3">
              <h3 class="text-sm font-semibold text-[var(--text-primary)]">Descripción</h3>
              
              <div class="flex gap-2">
                <button 
                  @click="deleteTicket" 
                  class="px-3 py-1.5 bg-[var(--priority-urg-bg)]/30 text-[var(--priority-urg-bg)] hover:bg-[var(--priority-urg-bg)] hover:text-[var(--text-primary)] border border-[var(--priority-urg-bg)]/50 rounded-lg text-xs font-medium transition-all"
                >
                  🗑️ Eliminar
                </button>
                <button
                  @click="saveTicket"
                  :disabled="isSaving"
                  class="px-3 py-1.5 bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 text-[var(--text-primary)] rounded-lg text-xs font-medium transition-all flex items-center gap-1 shadow-lg"
                >
                  <span>{{ isSaving ? '⏳' : '💾' }}</span>
                  {{ isSaving ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
              </div>
            </div>
            
            <textarea
              v-model="editedDescription"
              @blur="saveTicket"
              rows="4"
              class="w-full text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] text-[var(--text-primary)] rounded-lg p-3 focus:outline-none focus:border-[var(--lime)] hover:border-[var(--border-color)] transition-colors resize-y placeholder-[var(--text-muted)]"
              placeholder="Añade una descripción detallada del ticket aquí..."
            ></textarea>
          </div>

          <!-- ================================================================ -->
          <!-- SUB-SECCIÓN: Subtareas -->
          <!-- ================================================================ -->
          <div class="p-6 border-b border-[var(--border-subtle)]">
            <SubtaskChecklist
              :subtasks="localSubtasks"
              :ticket-id="ticket.id"
              @update="handleSubtaskUpdate"
              @create="handleSubtaskCreate"
              @delete="handleSubtaskDelete"
              @promote="handleSubtaskPromote"
            />
          </div>

          <!-- ================================================================ -->
          <!-- SUB-SECCIÓN: Log de Actividad -->
          <!-- ================================================================ -->
        <div class="p-6 border-b border-[var(--border-subtle)]">
            <h3 class="text-sm font-semibold text-[var(--text-primary)] mb-3">Actividad</h3>
            <ActivityLog :events="localEvents" />
          </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Pregunta Bloqueada (CS-023) -->
        <!-- ================================================================ -->
        <div v-if="ticket.status === 'BLOCKED_QUESTION'" class="p-6 border-b border-[var(--border-subtle)] bg-[color-mix(in_srgb,var(--status-blocked-bg)_10%,var(--bg-card))]">
          <div class="space-y-4">
            <div class="flex items-center gap-2 pb-3 border-b border-[var(--status-blocked-bg)]/30">
              <span class="text-lg">🔶</span>
              <h3 class="text-sm font-semibold text-[var(--status-blocked-text)]">Ticket Bloqueado por Pregunta</h3>
            </div>

            <!-- Mostrar la pregunta del dev -->
            <div class="space-y-2">
              <p class="text-xs text-[var(--text-secondary)]">Pregunta del desarrollador:</p>
              <div class="bg-[var(--bg-panel)] border border-[var(--status-blocked-bg)]/30 rounded-lg p-3">
                <p class="text-sm text-[var(--text-primary)]">{{ ticket.blockedQuestion || 'Sin pregunta registrada' }}</p>
              </div>
            </div>

            <!-- Si el usuario es Admin/TEAM_LEADER, mostrar textarea para responder -->
            <div v-if="isAdminOrLeader" class="space-y-3">
              <label class="text-xs font-semibold text-[var(--text-secondary)]">Tu respuesta:</label>
              <textarea
                v-model="resolutionAnswer"
                rows="3"
                placeholder="Escribe la respuesta a la pregunta del desarrollador..."
                class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border border-[var(--status-blocked-bg)]/50 text-[var(--text-primary)] rounded-lg focus:outline-none focus:border-[var(--status-blocked-bg)] placeholder-[var(--text-muted)] resize-none"
              ></textarea>
              <button
                @click="resolveQuestion"
                :disabled="!resolutionAnswer.trim() || isResolvingQuestion"
                class="w-full px-4 py-2 bg-[var(--lime)] text-[var(--dark-gray)] font-semibold rounded-lg hover:bg-[var(--lime-90)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ isResolvingQuestion ? '⏳ Enviando respuesta...' : '✓ Resolver Duda' }}
              </button>
            </div>

            <!-- Si el usuario es Developer, mostrar mensaje de espera -->
            <div v-else class="space-y-2 rounded-lg bg-[var(--bg-panel)] p-3 border border-[var(--status-blocked-bg)]/30">
              <p class="text-xs text-[var(--text-primary)]">⏳ Esperando respuesta del equipo...</p>
              <p class="text-xs text-[var(--text-secondary)]">Bloqueado hace {{ getBlockedDuration() }}</p>
            </div>
          </div>
        </div>

        <!-- ================================================================ -->
        <!-- SUB-SECCIÓN: Pull Request Link (CRÍTICO) -->
        <!-- ================================================================ -->
        <div class="p-6 border-b border-[var(--border-subtle)] space-y-3">
          <label class="text-sm font-semibold text-[var(--text-primary)]">
            Enlace del Pull Request
          </label>
          <div class="relative">
            <input
              data-cy="pr-link-input"
              v-model="editedPrLink"
              @blur="validateAndSavePrLink"
              type="url"
              placeholder="https://github.com/owner/repo/pull/123"
              class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border rounded-lg text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none transition-colors"
              :class="[
                editedPrLink.trim() === ''
                  ? 'border-[var(--border-subtle)] focus:border-[var(--lime)]'
                  : isPrLinkValid
                    ? 'border-[var(--teal)] focus:border-[var(--lime)]'
                    : 'border-red-500 focus:border-red-500'
              ]"
            />
            <span v-if="editedPrLink.trim() !== ''" class="absolute right-3 top-2 text-lg">
              {{ isPrLinkValid ? '✓' : '✗' }}
            </span>
          </div>
          <p v-if="editedPrLink.trim() !== '' && !isPrLinkValid" class="text-xs text-[var(--priority-urg-bg)]">
            URL no válida. Asegúrate de usar GitHub, GitLab o Bitbucket.
          </p>
          <p v-if="isPrLinkValid" class="text-xs text-[var(--teal)]">
            ✓ PR válido — El botón Completar está habilitado
          </p>
        </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Footer con Acciones (Sticky) -->
        <!-- ================================================================ -->
        <!-- Componente ActionDock con botones principales -->
        <!-- ================================================================ -->
        <div class="p-6 bg-[var(--bg-card)] border-t border-[var(--border-subtle)]">
            <ActionDock
              :ticket="ticketWithCurrentStatus"
              :is-pr-valid="isPrLinkValid"
              @start="handleStart"
              @complete="handleComplete"
              @question="handleQuestion"
              @redirect="handleRedirect"
              @resolve="handleResolve"
            />
          </div>

        <!-- ================================================================ -->
        <!-- ANIMACIÓN: Confetti -->
        <!-- ================================================================ -->
        </div> <ConfettiAnimation ref="confettiRef" />
      </div>
    </Transition>

    <!-- Overlay oscuro detrás del panel -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        @click="handleClose"
        class="fixed inset-0 bg-black bg-opacity-50 z-30"
      />
    </Transition>

    <!-- Toast de confirmación -->
    <Transition name="toast-up">
      <div
        v-if="toastVisible"
        class="fixed bottom-6 right-6 z-[200] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-2xl border text-sm font-semibold pointer-events-none"
        :class="toastType === 'success'
          ? 'bg-emerald-600 text-white border-emerald-400/30'
          : 'bg-red-600 text-white border-red-400/30'"
      >
        <span class="text-base">{{ toastType === 'success' ? '✓' : '✗' }}</span>
        {{ toastMessage }}
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import TimeTracker from '@/components/shared/TimeTracker.vue'
import SubtaskChecklist from './SubtaskChecklist.vue'
import ActivityLog from './ActivityLog.vue'
import ActionDock from './ActionDock.vue'
import ConfettiAnimation from '@/components/shared/ConfettiAnimation.vue'
import { useTicketTimer } from '@/composables/useTicketTimer'
import { useTicketsStore } from '@/stores/tickets'
import { useAuthStore } from '@/stores/auth'
import { useDialogStore } from '@/stores/dialog'
import { api } from '@/services/api'
import { TicketStatus, TicketPriority, UserRole } from '@/types'
import type { Ticket, Subtask, User } from '@/types'

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  ticket: Ticket
  isOpen: boolean
}

const props = defineProps<Props>()

// =====================================================================
// ESTADO LOCAL Y STORES
// =====================================================================

const dialogStore = useDialogStore()
const currentStatus = ref(props.ticket.status)

// Mantén sincronizado si el padre cambia (por si acaso)
watch(() => props.ticket.status, (newVal) => {
  currentStatus.value = newVal
})

const confettiRef = ref()
const {
  totalWorkSeconds,
  totalBlockedSeconds,
  isWorking,
  isBlocked: isBlockedTimer,
  startWork,
  pauseWork,
  resumeWork,
  stopWork,
  startBlocked,
  pauseBlocked,
} = useTicketTimer(computed(() => props.ticket))

// Instanciamos el store de tickets
const ticketsStore = useTicketsStore()
const authStore = useAuthStore()

// =====================================================================
// ESTADO LOCAL PARA EDICIÓN (CRUD)
// =====================================================================
const editedTitle = ref('')
const editedDescription = ref('')
const editedPriority = ref<TicketPriority>(TicketPriority.MEDIUM)
const editedPrLink = ref('')
const editedAssignee = ref<string | null>(null)
const teamMembers = ref<User[]>([])
const selectedAssigneeMember = computed(() => teamMembers.value.find(m => m.id === editedAssignee.value) ?? null)
const isSaving = ref(false)
const localSubtasks = ref<any[]>([])

// CS-023: Estado para resolver preguntas de desarrolladores bloqueados
const resolutionAnswer = ref('')
const isResolvingQuestion = ref(false)


// 1a. CRUD — sincroniza campos editables cuando cambia el ticket (shallow+deep para campos)
watch(
  () => props.ticket,
  (newTicket) => {
    if (newTicket) {
      editedTitle.value = newTicket.title || ''
      editedDescription.value = newTicket.description || ''
      editedPriority.value = newTicket.priority || 'MEDIUM'
      editedPrLink.value = newTicket.prLink || ''
      editedAssignee.value = (newTicket.assigneeId as string | null) || null
    }
  },
  { immediate: true, deep: true }
)

// 1b. Subtareas — solo se resetean cuando cambia el ID del ticket (ticket diferente abierto)
watch(
  () => props.ticket?.id,
  () => {
    localSubtasks.value = [...(props.ticket?.subtasks || [])]
  },
  { immediate: true }
)

// 2. CRONÓMETRO REACTIVO — optimista: responde al usuario sin esperar la API
watch(currentStatus, (newStatus) => {
  if (newStatus === TicketStatus.IN_PROGRESS) { pauseBlocked(); startWork() }
  // BLOCKED_QUESTION (pregunta del developer) también bloquea el trabajo: al hacer
  // una pregunta el estado pasa a BLOCKED_QUESTION, no a BLOCKED, por lo que debe
  // pausar el cronómetro de trabajo igual que un bloqueo normal.
  else if (newStatus === TicketStatus.BLOCKED || newStatus === TicketStatus.BLOCKED_QUESTION) { pauseWork(); startBlocked() }
  else if (newStatus === TicketStatus.COMPLETED) stopWork()
})

// 3. CARGAR EL HISTORIAL DE EVENTOS
const localEvents = ref<any[]>([])

const loadTicketEvents = async () => {
  try {
    // ¡Usamos la función del store que ya sabe cómo enviar el token!
    localEvents.value = await ticketsStore.getTicketEvents(props.ticket.id)
  } catch (error) {
    console.error("Error cargando eventos:", error)
  }
}

// Cargar eventos apenas se abre el panel
watch(() => props.ticket.id, () => {
  if (props.ticket?.id) loadTicketEvents()
}, { immediate: true })

// =====================================================================
// FUNCIONES CRUD DEL ADMINISTRADOR
// =====================================================================

const loadTeamMembers = async () => {
  try {
    teamMembers.value = await api.tickets.getTeamMembers()
  } catch (error) {
    console.error('Error al cargar miembros del equipo:', error)
  }
}

const saveAssignee = async () => {
  try {
    if (editedAssignee.value) {
      await api.team.assignTicket(props.ticket.id, editedAssignee.value)
    } else {
      await api.team.unassignTicket(props.ticket.id)
    }
    emit('ticketUpdated', { ticketId: props.ticket.id, action: 'assigned', data: { assigneeId: editedAssignee.value } })
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error) {
    console.error('Error al asignar ticket:', error)
  }
}

const saveTicket = async () => {
  // Evitar doble guardado si ya está procesando
  if (isSaving.value) return

  isSaving.value = true
  try {
    await ticketsStore.update(props.ticket.id, {
      title: editedTitle.value,
      description: editedDescription.value,
      priority: editedPriority.value,
      prLink: editedPrLink.value.trim() || undefined
    })
    // Pinia actualizará la vista automáticamente
    emit('ticketUpdated', { action: 'saved' })
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error) {
    console.error("Error al actualizar ticket:", error)
    dialogStore.alert("Hubo un error al guardar los cambios.")
  } finally {
    isSaving.value = false
  }
}

const validateAndSavePrLink = async () => {
  if (editedPrLink.value.trim() === '') {
    // Si está vacío, permitir (puede no tener PR aún)
    await saveTicket()
    return
  }

  if (!isPrLinkValid.value) {
    // Si no es válido, no guardar
    return
  }

  // Si es válido, guardar
  await saveTicket()
}

const deleteTicket = async () => {
  if (!(await dialogStore.confirm(`¿Estás seguro de que deseas eliminar el ticket "${props.ticket.title}"? Esta acción no se puede deshacer.`))) {
    return
  }
  try {
    await ticketsStore.remove(props.ticket.id)
    emit('close') // Cerramos el panel lateral porque el ticket ya no existe
  } catch (error) {
    console.error("Error al eliminar ticket:", error)
    dialogStore.alert("Hubo un error al eliminar el ticket.")
  }
}

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

const isBlocked = computed(() => currentStatus.value === 'BLOCKED')

const PLACEHOLDER_PR = /github\.com\/owner\/repo\/|gitlab\.com\/owner\/repo\/|bitbucket\.org\/owner\/repo\//

// Validar PR Link según plataforma (GitHub, GitLab, Bitbucket)
const isPrLinkValid = computed(() => {
  const url = editedPrLink.value.trim()
  if (url === '') return false
  if (PLACEHOLDER_PR.test(url)) return false
  const prUrlRegex = /^https:\/\/(github\.com|gitlab\.com|bitbucket\.org)\/.+\/(pull|merge_requests|pull-requests)\/\d+/i
  return prUrlRegex.test(url)
})

// CS-023: Verificar si el usuario actual es Admin o Team Leader
const isAdminOrLeader = computed(() => {
  const userRole = authStore.user?.role
  return userRole === UserRole.ADMIN || userRole === UserRole.TEAM_LEADER
})

// Mismo mapeo de color de prioridad que WorkbenchTicketCard/TicketList,
// para que el punto de color coincida con el que se ve fuera del panel.
const priorityDotClass = computed(() => {
  const map: Record<string, string> = {
    LOW: 'bg-[var(--priority-low-bg)]',
    MEDIUM: 'bg-[var(--priority-med-bg)]',
    HIGH: 'bg-[var(--priority-high-bg)]',
    URGENT: 'bg-[var(--priority-urg-bg)]',
  }
  return map[editedPriority.value] ?? 'bg-[var(--text-secondary)]'
})

// Ticket con estado optimista para que ActionDock refleje cambios de inmediato
const ticketWithCurrentStatus = computed(() => ({
  ...props.ticket,
  status: currentStatus.value,
  prLink: editedPrLink.value
}))

// =====================================================================
// WATCHERS
// =====================================================================

watch(
  () => props.isOpen,
  (isOpen: boolean) => {
    if (!isOpen) {
      pauseWork()
    } else if (props.ticket.status === TicketStatus.IN_PROGRESS) {
      resumeWork()
    }
  }
)

// =====================================================================
// MÉTODOS DE UTILIDAD
// =====================================================================

const getInitials = (name: any): string => {
  // 1. Si no hay nada, devuelve 'U' de Usuario
  if (!name) return 'U'
  
  // 2. Si recibimos un objeto en vez de un texto, buscamos su nombre adentro
  let nameStr = ''
  if (typeof name === 'object') {
    nameStr = name.fullName || name.full_name || name.name || 'U'
  } else {
    nameStr = String(name)
  }

  // 3. Extraemos las iniciales con seguridad
  return nameStr
    .split(' ')
    .filter(n => n.length > 0) // Evita errores si hay espacios dobles
    .map(n => n)
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'U'
}

const getAssigneeName = (assignee: string | User | Record<string, any> | undefined): string => {
  if (!assignee) return 'Sin asignar'
  if (typeof assignee === 'string') return assignee
  return (assignee as any).fullName || (assignee as any).full_name || (assignee as any).name || 'Sin asignar'
}

// =====================================================================
// MANEJADORES DE EVENTOS DE SUBTAREAS (Conectados a Pinia)
// =====================================================================

/**
 * Crea una nueva subtarea usando el store
 */
const handleSubtaskCreate = async (title: string) => {
  try {
    const newSubtask = await ticketsStore.createSubtask(props.ticket.id, title)
    localSubtasks.value.push(newSubtask)
  } catch (error) {
    console.error('Error al crear subtarea:', error)
    showToast('No se pudo crear la subtarea', 'error')
  }
}

/**
 * Actualiza una subtarea (marcarla como completada o desmarcarla)
 * Optimistic update: actualiza la UI inmediatamente y revierte si falla
 */
const handleSubtaskUpdate = async (subtask: any) => {
  const index = localSubtasks.value.findIndex(s => s.id === subtask.id)
  if (index === -1) return

  // 1. Guardar estado anterior para poder revertir
  const previous = { ...localSubtasks.value[index] }

  // 2. Aplicar cambio optimistamente
  localSubtasks.value[index] = { ...localSubtasks.value[index], ...subtask }

  try {
    const updated = await ticketsStore.updateSubtask(props.ticket.id, subtask.id, {
      title: subtask.title,
      isCompleted: subtask.isCompleted,
    })
    // Confirmar con la respuesta del servidor
    localSubtasks.value[index] = updated
  } catch (error) {
    // Revertir si falla
    localSubtasks.value[index] = previous
    console.error('Error al actualizar subtarea', error)
  }
}

/**
 * Elimina una subtarea
 */
const handleSubtaskDelete = async (subtaskId: string) => {
  try {
    await ticketsStore.deleteSubtask(props.ticket.id, subtaskId)
    localSubtasks.value = localSubtasks.value.filter(s => s.id !== subtaskId)
  } catch (error) { console.error("Error", error) }
}

/**
 * Convierte una subtarea en un ticket independiente
 */
const handleSubtaskPromote = async (subtask: any) => {
  try {
    await ticketsStore.create({
      epicId: props.ticket.epicId,
      title: subtask.title,
      priority: 'MEDIUM'
    })
    await ticketsStore.deleteSubtask(props.ticket.id, subtask.id)
    localSubtasks.value = localSubtasks.value.filter(s => s.id !== subtask.id)
    emit('ticketUpdated', { action: 'refresh', ticketId: props.ticket.id })
    showToast('Subtarea convertida en ticket exitosamente.', 'success')
  } catch (error) {
    console.error('Error promoting subtask:', error)
    showToast('Error al convertir la subtarea en ticket.', 'error')
  }
}

// =====================================================================
// MANEJADORES DE EVENTOS DEL TICKET (ActionDock)
// =====================================================================
const handleStart = async () => {
  try {
    await api.tickets.start(props.ticket.id)
    currentStatus.value = TicketStatus.IN_PROGRESS
    emit('ticketUpdated', { ticketId: props.ticket.id, action: 'start', data: {} })
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error: any) {
    console.error('Error al iniciar ticket:', error)
  }
}

const handleComplete = async () => {
  // 1. Doble validación de seguridad en el Frontend
  if (!isPrLinkValid.value) {
    dialogStore.alert('⚠️ Por favor ingresa un link de PR válido antes de completar el ticket.');
    return;
  }

  try {
    // 2. ¡EL ARREGLO ESTÁ AQUÍ! Usamos la ruta oficial de tu API
    await api.tickets.complete(props.ticket.id, editedPrLink.value);

    // 3. Si el backend dice "OK", disparamos la magia visual
    confettiRef.value?.fireConfetti();
    currentStatus.value = TicketStatus.COMPLETED;
    
    // Le avisamos al tablero que el ticket está listo
    emit('ticketUpdated', {
      ticketId: props.ticket.id,
      action: 'complete',
      data: { prUrl: editedPrLink.value }
    });
    
    // Recargamos el historial para que aparezca el evento
    setTimeout(() => loadTicketEvents(), 200);

  } catch (error: any) {
    console.error("Error al completar el ticket:", error);
    const errorMsg = error.response?.data?.detail || error.message;
    dialogStore.alert("Error al completar el ticket: " + errorMsg);
  }
}

const handleQuestion = async (question: string) => {
  try {
    await api.tickets.raiseQuestion(props.ticket.id, question)
    currentStatus.value = TicketStatus.BLOCKED_QUESTION
    emit('ticketUpdated', { ticketId: props.ticket.id, action: 'question', data: { question } })
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error: any) {
    const msg = error.response?.data?.detail || error.message || 'Error al enviar la pregunta'
    dialogStore.alert('Error: ' + msg)
  }
}

const handleRedirect = (data: { toUserId: string; reason: string }) => {
  stopWork()
  emit('ticketUpdated', {
    ticketId: props.ticket.id,
    action: 'redirect',
    data
  })
  setTimeout(() => loadTicketEvents(), 200) // Recarga el historial
}

const handleResolve = async (resolution: string) => {
  try {
    await api.tickets.resolveQuestion(props.ticket.id, undefined, resolution)
    currentStatus.value = TicketStatus.IN_PROGRESS
    emit('ticketUpdated', { ticketId: props.ticket.id, action: 'resolve', data: { resolution } })
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error) {
    console.error('Error al resolver pregunta desde ActionDock:', error)
  }
}

// =====================================================================
// MÉTODOS PARA CS-023 (RESPONDER PREGUNTAS DE DESARROLLADORES)
// =====================================================================

/**
 * Resuelve una pregunta bloqueadora enviando la respuesta del admin al desarrollador
 */
const resolveQuestion = async () => {
  if (!resolutionAnswer.value.trim()) {
    dialogStore.alert('Por favor, escribe una respuesta antes de enviar.')
    return
  }

  isResolvingQuestion.value = true
  try {
    // Llamar API para resolver la pregunta del ticket bloqueado
    await api.tickets.resolveQuestion(props.ticket.id, undefined, resolutionAnswer.value)

    // Actualizar estado del ticket a IN_PROGRESS
    currentStatus.value = TicketStatus.IN_PROGRESS
    const answer = resolutionAnswer.value
    resolutionAnswer.value = ''

    // Notificar al componente padre
    emit('ticketUpdated', {
      ticketId: props.ticket.id,
      action: 'questionResolved',
      data: { resolution: answer }
    })

    showToast('¡Duda resuelta correctamente!')

    // Recargar eventos
    setTimeout(() => loadTicketEvents(), 200)
  } catch (error) {
    console.error('Error al resolver pregunta:', error)
    showToast('Hubo un error al enviar la respuesta.', 'error')
  } finally {
    isResolvingQuestion.value = false
  }
}

/**
 * Calcula el tiempo que lleva el ticket bloqueado
 */
const getBlockedDuration = (): string => {
  if (!props.ticket.blockedAt) return 'hace poco'

  const blockedTime = new Date(props.ticket.blockedAt).getTime()
  const now = Date.now()
  const diffMs = now - blockedTime

  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffDays > 0) return `${diffDays} día${diffDays !== 1 ? 's' : ''}`
  if (diffHours > 0) return `${diffHours} hora${diffHours !== 1 ? 's' : ''}`
  if (diffMinutes > 0) return `${diffMinutes} minuto${diffMinutes !== 1 ? 's' : ''}`

  return 'hace poco'
}

// =====================================================================
// EMITS
// =====================================================================

const emit = defineEmits<{
  close: []
  ticketUpdated: [data: any]
}>()

const handleClose = () => emit('close')

// =====================================================================
// TOAST DE CONFIRMACIÓN
// =====================================================================

const toastMessage = ref('')
const toastVisible = ref(false)
const toastType = ref<'success' | 'error'>('success')
let toastTimer: ReturnType<typeof setTimeout> | null = null

const showToast = (msg: string, type: 'success' | 'error' = 'success') => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = msg
  toastType.value = type
  toastVisible.value = true
  toastTimer = setTimeout(() => { toastVisible.value = false }, 3000)
}

onUnmounted(() => { if (toastTimer) clearTimeout(toastTimer) })

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.isOpen) handleClose()
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  loadTeamMembers()
})
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
/* Transición de panel deslizable desde la derecha */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}

/* Transición de fade para overlay */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Transición del toast — sube desde abajo */
.toast-up-enter-active,
.toast-up-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.toast-up-enter-from,
.toast-up-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>


