<!--
  ============================================================================
  IncidentDetailPanel.vue — Panel Lateral de Detalle del Incidente
  ============================================================================

  Panel deslizante desde la derecha (40% del ancho) que muestra todos los
  detalles de un incidente seleccionado. Similar al TicketSidePanel pero
  adaptado al flujo de incidentes con:

  - Header sticky: severidad, título, estado, categoría
  - Info bar: reportador, asignado, fecha, días abierto
  - Cuerpo scrollable: descripción, detalles técnicos, resolución, comentarios
  - Footer sticky: botones de acción contextuales según el estado actual

  El footer cambia dinámicamente según el estado del incidente:
    OPEN: "Iniciar Trabajo" + "Asignar"
    IN_PROGRESS: "Enviar a Revisión" + "Resolver"
    UNDER_REVIEW: "Resolver" + "Devolver"
    RESOLVED: "Cerrar" (admin) + "Reabrir"
    CLOSED: "Reabrir"
  ============================================================================
-->
<template>
  <!-- Overlay semitransparente + Panel deslizante -->
  <Teleport to="body">
    <Transition name="panel">
      <div v-if="isOpen && incident" class="fixed inset-0 z-50 flex justify-end">
        <!-- Fondo oscuro — clic para cerrar -->
        <div class="absolute inset-0 bg-black/30" @click="$emit('close')" />

        <!-- Panel principal (40% ancho, desliza desde derecha) -->
        <div class="relative w-full max-w-xl bg-white dark:bg-gray-900 shadow-2xl flex flex-col overflow-hidden">

          <!-- ===== HEADER STICKY ===== -->
          <div class="sticky top-0 z-10 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <!-- Fila 1: Severidad + Título + Cerrar -->
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-start gap-3 flex-1">
                <!-- Indicador de severidad grande -->
                <span
                  :class="['mt-1 w-3 h-3 rounded-full flex-shrink-0', severityConfig.dotClass]"
                  :title="severityConfig.label"
                />
                <div class="flex-1">
                  <h2 class="text-lg font-bold text-gray-900 dark:text-gray-100 leading-tight">
                    {{ incident.title }}
                  </h2>
                </div>
              </div>

              <!-- Botón cerrar -->
              <button
                class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400 hover:text-gray-600 transition-colors"
                @click="$emit('close')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Fila 2: Badges de categoría y estado -->
            <div class="flex items-center gap-2 mt-2">
              <span :class="['px-2 py-0.5 rounded text-xs font-medium', categoryConfig.bgColor, categoryConfig.textColor]">
                {{ categoryConfig.icon }} {{ categoryConfig.label }}
              </span>
              <span :class="['px-2 py-0.5 rounded text-xs font-medium', statusConfig.bgClass, statusConfig.textClass]">
                {{ statusConfig.label }}
              </span>
              <span class="text-xs text-gray-400">
                {{ incident.daysOpen || 0 }} {{ $t?.('incidents.daysOpen') || 'días abierto' }}
              </span>
            </div>
          </div>

          <!-- ===== INFO BAR ===== -->
          <div class="px-6 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700 grid grid-cols-2 gap-3 text-sm">
            <!-- Reportado por -->
            <div>
              <span class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ $t?.('incidents.reportedBy') || 'Reportado por' }}</span>
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center text-[10px] font-bold text-blue-700 dark:text-blue-200">
                  {{ getInitials(incident.reporter?.fullName || 'AD') }}
                </div>
                <span class="text-gray-800 dark:text-gray-200 font-medium">{{ incident.reporter?.fullName || 'Admin' }}</span>
              </div>
            </div>

            <!-- Asignado a -->
            <div>
              <span class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ $t?.('incidents.assignedTo') || 'Asignado a' }}</span>
              <div class="flex items-center gap-2">
                <template v-if="incident.assignee">
                  <div class="w-6 h-6 rounded-full bg-green-100 dark:bg-green-800 flex items-center justify-center text-[10px] font-bold text-green-700 dark:text-green-200">
                    {{ getInitials(incident.assignee.fullName || '') }}
                  </div>
                  <span class="text-gray-800 dark:text-gray-200 font-medium">{{ incident.assignee.fullName }}</span>
                </template>
                <template v-else>
                  <span class="text-gray-400 italic">{{ $t?.('incidents.unassigned') || 'Sin asignar' }}</span>
                </template>
              </div>
            </div>

            <!-- Creado -->
            <div>
              <span class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ $t?.('incidents.created') || 'Creado' }}</span>
              <span class="text-gray-800 dark:text-gray-200">{{ formatDateTime(incident.createdAt) }}</span>
            </div>

            <!-- Fecha límite -->
            <div>
              <span class="text-xs text-gray-500 dark:text-gray-400 block mb-1">{{ $t?.('incidents.dueDate') || 'Fecha límite' }}</span>
              <span :class="incident.isOverdue ? 'text-red-500 font-medium' : 'text-gray-800 dark:text-gray-200'">
                {{ incident.dueDate ? formatDate(incident.dueDate) : 'Sin fecha' }}
              </span>
            </div>
          </div>

          <!-- Banner de vencido -->
          <div
            v-if="incident.isOverdue"
            class="px-6 py-2 bg-red-50 dark:bg-red-900/30 border-b border-red-200 dark:border-red-800 flex items-center gap-2"
          >
            <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <span class="text-sm text-red-700 dark:text-red-300 font-medium">
              {{ $t?.('incidents.overdueWarning') || 'Este incidente está vencido por' }} {{ incident.daysOpen }} {{ $t?.('incidents.days') || 'días' }}
            </span>
          </div>

          <!-- ===== CUERPO SCROLLABLE ===== -->
          <div class="flex-1 overflow-y-auto px-6 py-4 space-y-5">

            <!-- Descripción -->
            <section>
              <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                {{ $t?.('incidents.description') || 'Descripción' }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap leading-relaxed">
                {{ incident.description }}
              </p>
            </section>

            <!-- Detalles Técnicos (colapsable, solo si hay datos) -->
            <section
              v-if="incident.stepsToReproduce || incident.expectedBehavior || incident.actualBehavior"
            >
              <button
                class="flex items-center gap-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 hover:text-blue-600 transition-colors"
                @click="showTechnicalDetails = !showTechnicalDetails"
              >
                <svg
                  :class="['w-4 h-4 transition-transform', showTechnicalDetails ? 'rotate-90' : '']"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
                {{ $t?.('incidents.technicalDetails') || 'Detalles Técnicos' }}
              </button>

              <div v-show="showTechnicalDetails" class="space-y-3 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
                <div v-if="incident.stepsToReproduce">
                  <span class="text-xs font-medium text-gray-500 uppercase">{{ $t?.('incidents.stepsToReproduce') || 'Pasos para reproducir' }}</span>
                  <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap mt-1">{{ incident.stepsToReproduce }}</p>
                </div>
                <div v-if="incident.expectedBehavior">
                  <span class="text-xs font-medium text-gray-500 uppercase">{{ $t?.('incidents.expectedBehavior') || 'Comportamiento esperado' }}</span>
                  <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap mt-1">{{ incident.expectedBehavior }}</p>
                </div>
                <div v-if="incident.actualBehavior">
                  <span class="text-xs font-medium text-gray-500 uppercase">{{ $t?.('incidents.actualBehavior') || 'Comportamiento actual' }}</span>
                  <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap mt-1">{{ incident.actualBehavior }}</p>
                </div>
                <div v-if="incident.environment" class="flex items-center gap-2">
                  <span class="text-xs font-medium text-gray-500">{{ $t?.('incidents.environment') || 'Entorno' }}:</span>
                  <span class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">{{ incident.environment }}</span>
                </div>
              </div>
            </section>

            <!-- Notas de Resolución (solo si resuelto/cerrado) -->
            <section v-if="incident.resolutionNotes">
              <h3 class="text-sm font-semibold text-green-700 dark:text-green-400 mb-2 flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ $t?.('incidents.resolutionNotes') || 'Notas de Resolución' }}
              </h3>
              <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800">
                <p class="text-sm text-green-800 dark:text-green-300 whitespace-pre-wrap">{{ incident.resolutionNotes }}</p>
                <p v-if="incident.fixedInVersion" class="text-xs text-green-600 dark:text-green-400 mt-2">
                  {{ $t?.('incidents.fixedInVersion') || 'Corregido en versión' }}: {{ incident.fixedInVersion }}
                </p>
              </div>
            </section>

            <!-- Sección de Comentarios -->
            <section>
              <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                {{ $t?.('incidents.comments') || 'Comentarios' }}
                <span class="text-gray-400 font-normal">({{ comments.length }})</span>
              </h3>

              <!-- Lista de comentarios -->
              <div class="space-y-3">
                <div
                  v-for="comment in comments"
                  :key="comment.id"
                  class="flex gap-3"
                >
                  <div class="w-7 h-7 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-[10px] font-bold text-gray-600 dark:text-gray-300 flex-shrink-0">
                    {{ getInitials(comment.userName) }}
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-medium text-gray-800 dark:text-gray-200">{{ comment.userName }}</span>
                      <span class="text-xs text-gray-400">{{ formatTimeAgo(comment.createdAt) }}</span>
                    </div>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">{{ comment.content }}</p>
                  </div>
                </div>

                <!-- Sin comentarios -->
                <p v-if="comments.length === 0" class="text-sm text-gray-400 italic py-2">
                  {{ $t?.('incidents.noComments') || 'Aún no hay comentarios' }}
                </p>
              </div>

              <!-- Input para agregar comentario -->
              <div class="mt-3 flex gap-2">
                <input
                  v-model="newComment"
                  type="text"
                  :placeholder="$t?.('incidents.addComment') || 'Escribe un comentario...'"
                  class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  @keydown.enter="submitComment"
                />
                <button
                  :disabled="!newComment.trim()"
                  class="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  @click="submitComment"
                >
                  {{ $t?.('common.send') || 'Enviar' }}
                </button>
              </div>
            </section>
          </div>

          <!-- ===== FOOTER STICKY — BOTONES DE ACCIÓN ===== -->
          <div class="sticky bottom-0 z-10 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center gap-2 flex-wrap">

            <!-- OPEN: Iniciar Trabajo + Asignar -->
            <template v-if="incident.status === 'OPEN' || incident.status === 'REOPENED'">
              <button
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                @click="handleAction('start')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                </svg>
                {{ $t?.('incidents.startWorking') || 'Iniciar Trabajo' }}
              </button>
              <button
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                @click="showAssignDropdown = !showAssignDropdown"
              >
                {{ $t?.('incidents.assign') || 'Asignar' }}
              </button>
            </template>

            <!-- IN_PROGRESS: Enviar a Revisión + Resolver -->
            <template v-else-if="incident.status === 'IN_PROGRESS'">
              <button
                class="flex-1 px-4 py-2 bg-amber-500 text-white rounded-lg text-sm font-medium hover:bg-amber-600 transition-colors flex items-center justify-center gap-2"
                @click="handleAction('review')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                {{ $t?.('incidents.sendToReview') || 'Enviar a Revisión' }}
              </button>
              <button
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                @click="showResolveForm = true"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ $t?.('incidents.resolve') || 'Resolver' }}
              </button>
            </template>

            <!-- UNDER_REVIEW: Resolver + Devolver -->
            <template v-else-if="incident.status === 'UNDER_REVIEW'">
              <button
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                @click="showResolveForm = true"
              >
                {{ $t?.('incidents.resolve') || 'Resolver' }}
              </button>
              <button
                class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                @click="handleAction('return')"
              >
                {{ $t?.('incidents.returnToProgress') || 'Devolver' }}
              </button>
            </template>

            <!-- RESOLVED: Cerrar (admin) + Reabrir -->
            <template v-else-if="incident.status === 'RESOLVED'">
              <button
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                @click="handleAction('close')"
              >
                {{ $t?.('incidents.close') || 'Cerrar Incidente' }}
              </button>
              <button
                class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm font-medium hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                @click="handleAction('reopen')"
              >
                {{ $t?.('incidents.reopen') || 'Reabrir' }}
              </button>
            </template>

            <!-- CLOSED: Reabrir -->
            <template v-else-if="incident.status === 'CLOSED'">
              <button
                class="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm font-medium hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors"
                @click="handleAction('reopen')"
              >
                {{ $t?.('incidents.reopen') || 'Reabrir Incidente' }}
              </button>
            </template>
          </div>

          <!-- ===== FORMULARIO DE RESOLUCIÓN (overlay) ===== -->
          <div
            v-if="showResolveForm"
            class="absolute inset-0 z-20 bg-white/95 dark:bg-gray-900/95 flex items-center justify-center p-6"
          >
            <div class="w-full max-w-md space-y-4">
              <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
                {{ $t?.('incidents.resolveIncident') || 'Resolver Incidente' }}
              </h3>
              <textarea
                v-model="resolutionNotes"
                :placeholder="$t?.('incidents.resolutionNotesPlaceholder') || 'Describe cómo se resolvió el problema (mín. 10 caracteres)...'"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 text-sm min-h-[120px] focus:ring-2 focus:ring-green-500"
              />
              <input
                v-model="fixedInVersion"
                type="text"
                :placeholder="$t?.('incidents.fixedInVersionPlaceholder') || 'Versión de corrección (opcional, ej: v2.1.3)'"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 text-sm"
              />
              <div class="flex gap-2">
                <button
                  class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg text-sm"
                  @click="showResolveForm = false"
                >
                  {{ $t?.('common.cancel') || 'Cancelar' }}
                </button>
                <button
                  :disabled="resolutionNotes.trim().length < 10"
                  class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  @click="handleResolve"
                >
                  {{ $t?.('incidents.confirmResolve') || 'Confirmar Resolución' }}
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
/**
 * Script del panel de detalle de incidente.
 *
 * Gestiona la visualización completa de un incidente y
 * los flujos de acción (resolver, cerrar, reabrir, etc.)
 * a través del store de incidentes.
 */
import { ref, computed, watch } from 'vue'
import type { Incident, IncidentComment } from '@/types/incidents'
import {
  CATEGORY_CONFIG,
  SEVERITY_CONFIG,
  STATUS_CONFIG,
  IncidentCategory,
  IncidentSeverity,
  IncidentStatus,
} from '@/types/incidents'
import { useIncidentsStore } from '@/stores/incidents'

// === Props y Emits ===

const props = defineProps<{
  incident: Incident
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'updated'): void
}>()

// === Store ===
const incidentsStore = useIncidentsStore()

// === Estado local ===
const showTechnicalDetails = ref(false)
const showResolveForm = ref(false)
const showAssignDropdown = ref(false)
const resolutionNotes = ref('')
const fixedInVersion = ref('')
const newComment = ref('')
const comments = ref<IncidentComment[]>([])

// === Configuraciones visuales computadas ===

const categoryConfig = computed(() =>
  CATEGORY_CONFIG[props.incident.category] || CATEGORY_CONFIG[IncidentCategory.NON_CRITICAL_ERROR]
)

const severityConfig = computed(() =>
  SEVERITY_CONFIG[props.incident.severity] || SEVERITY_CONFIG[IncidentSeverity.MEDIUM]
)

const statusConfig = computed(() =>
  STATUS_CONFIG[props.incident.status] || STATUS_CONFIG[IncidentStatus.OPEN]
)

// === Watchers ===

/** Cargar comentarios cuando se abre el panel o cambia el incidente */
watch(
  () => [props.isOpen, props.incident?.id],
  async ([open, id]) => {
    if (open && id) {
      try {
        comments.value = await incidentsStore.fetchComments(id as string)
      } catch {
        comments.value = []
      }
    }
  },
  { immediate: true }
)

// === Funciones de acción ===

/**
 * Maneja las acciones de cambio de estado del incidente.
 * Cada acción llama al método correspondiente del store.
 */
async function handleAction(action: string) {
  try {
    switch (action) {
      case 'start':
        await incidentsStore.start(props.incident.id)
        break
      case 'review':
        await incidentsStore.review(props.incident.id)
        break
      case 'close':
        await incidentsStore.close(props.incident.id)
        break
      case 'reopen':
        await incidentsStore.reopen(props.incident.id)
        break
      case 'return':
        // Devolver a IN_PROGRESS desde UNDER_REVIEW
        await incidentsStore.start(props.incident.id)
        break
    }
    emit('updated')
  } catch (error) {
    console.error(`Error ejecutando acción ${action}:`, error)
  }
}

/**
 * Confirma la resolución del incidente con las notas proporcionadas.
 */
async function handleResolve() {
  if (resolutionNotes.value.trim().length < 10) return
  try {
    await incidentsStore.resolve(
      props.incident.id,
      resolutionNotes.value.trim(),
      fixedInVersion.value.trim() || undefined
    )
    showResolveForm.value = false
    resolutionNotes.value = ''
    fixedInVersion.value = ''
    emit('updated')
  } catch (error) {
    console.error('Error resolviendo incidente:', error)
  }
}

/**
 * Envía un nuevo comentario al incidente.
 */
async function submitComment() {
  if (!newComment.value.trim()) return
  try {
    await incidentsStore.addComment(props.incident.id, newComment.value.trim())
    newComment.value = ''
    // Recargar comentarios
    comments.value = await incidentsStore.fetchComments(props.incident.id)
  } catch (error) {
    console.error('Error agregando comentario:', error)
  }
}

// === Funciones utilitarias ===

function getInitials(name: string): string {
  return name.split(' ').slice(0, 2).map((w) => w.charAt(0).toUpperCase()).join('')
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `hace ${minutes}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `hace ${hours}h`
  const days = Math.floor(hours / 24)
  return `hace ${days}d`
}
</script>

<style scoped>
/* Animación de entrada/salida del panel deslizante */
.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s ease;
}
.panel-enter-from,
.panel-leave-to {
  opacity: 0;
}
.panel-enter-from > div:last-child,
.panel-leave-to > div:last-child {
  transform: translateX(100%);
}
</style>
