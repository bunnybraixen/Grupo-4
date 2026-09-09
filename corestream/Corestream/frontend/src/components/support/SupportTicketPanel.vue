<template>
  <div v-if="ticket" class="h-full flex flex-col bg-[var(--bg-panel)] border-l border-[var(--border-subtle)] overflow-y-auto">
    <!-- Header -->
    <div class="p-5 border-b border-[var(--border-subtle)] sticky top-0 bg-[var(--bg-panel)] z-10">
      <div class="flex items-start justify-between gap-2 mb-3">
        <h2 class="text-base font-semibold text-[var(--text-primary)] leading-snug flex-1">
          {{ ticket.title }}
        </h2>
        <button
          @click="$emit('close')"
          class="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors shrink-0 mt-0.5"
        >
          ✕
        </button>
      </div>

      <!-- Badges: estado y severidad -->
      <div class="flex flex-wrap gap-2">
        <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', statusBadge(ticket.status)]">
          {{ statusLabel(ticket.status) }}
        </span>
        <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', severityBadge(ticket.severity)]">
          {{ severityIcon(ticket.severity) }} {{ severityLabel(ticket.severity) }}
        </span>
        <span v-if="ticket.assignee" class="text-xs px-2 py-0.5 rounded-full bg-[var(--bg-app)] text-[var(--text-secondary)]">
          👤 {{ ticket.assignee.fullName }}
        </span>
        <span v-if="ticket.linkedTicketTitle" class="text-xs px-2 py-0.5 rounded-full bg-[var(--bg-app)] text-[var(--text-secondary)]">
          🔗 {{ ticket.linkedTicketTitle }}<span v-if="ticket.originEpicTitle"> ({{ ticket.originEpicTitle }})</span>
        </span>
        <span v-if="investigatorName" class="text-xs px-2 py-0.5 rounded-full bg-[var(--bg-app)] text-[var(--text-secondary)]">
          🔍 {{ t('supportTicketsView.investigatedBy') || 'Investigado por' }}: {{ investigatorName }}
        </span>
      </div>
    </div>

    <!-- Contenido scrollable -->
    <div class="flex-1 p-5 space-y-5">

      <!-- Asignación (solo TEAM_LEADER) -->
      <div v-if="authStore.isTeamLeader && ticket.status !== 'RESOLVED'">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('supportTicketsView.assignToDeveloper') || 'Asignar a Developer' }}</p>
        <div class="flex gap-2">
          <select
            v-model="selectedAssigneeId"
            class="flex-1 px-3 py-2 text-sm rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-blue-500"
          >
            <option value="">{{ t('supportTicketsView.unassigned') || 'Sin asignar' }}</option>
            <option v-for="member in teamMembers" :key="member.id" :value="member.id">
              {{ member.fullName }}
            </option>
          </select>
          <button
            @click="handleAssign"
            :disabled="!selectedAssigneeId || isAssigning"
            class="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {{ isAssigning ? (t('supportTicketsView.assigning') || '...') : (t('supportTicketsView.assign') || 'Asignar') }}
          </button>
        </div>
      </div>

      <!-- Enlace de PR requerido para resolver -->
      <div v-if="ticket.status === 'INVESTIGATING'">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('actions.prLink') || 'Enlace de PR' }}</p>
        <input
          v-model="prLink"
          type="text"
          :placeholder="t('actions.prLinkPlaceholder') || 'https://github.com/repo/pull/123'"
          class="w-full px-3 py-2 text-sm rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-blue-500"
        />
        <p v-if="prLink && !prLinkValid" class="text-xs text-red-400 mt-1">
          {{ t('actions.invalidPr') || 'Enlace de PR inválido' }}
        </p>
      </div>

      <!-- PR de la solución (ticket ya resuelto) -->
      <div v-if="ticket.status === 'RESOLVED' && ticket.prLink">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('actions.prLink') || 'Enlace de PR' }}</p>
        <a :href="ticket.prLink" target="_blank" rel="noopener noreferrer" class="text-sm text-blue-400 hover:underline break-all">{{ ticket.prLink }}</a>
      </div>

      <!-- Acciones de estado -->
      <div v-if="ticket.status !== 'RESOLVED'" class="flex gap-2">
        <button
          v-if="ticket.status === 'REPORTED'"
          @click="handleInvestigate"
          :disabled="isTransitioning"
          class="flex-1 px-3 py-2 text-sm rounded-lg bg-[var(--status-progress-bg)] text-[var(--status-progress-text)] hover:opacity-90 disabled:opacity-50 transition-opacity font-medium"
        >
          {{ isTransitioning ? (t('supportTicketsView.processing') || 'Procesando...') : (t('supportTicketsView.startInvestigation') || '🔍 Iniciar Investigación') }}
        </button>
        <button
          v-if="ticket.status === 'INVESTIGATING'"
          @click="handleResolve"
          :disabled="isTransitioning || !prLinkValid"
          class="flex-1 px-3 py-2 text-sm rounded-lg bg-[var(--status-done-bg)] text-[var(--status-done-text)] hover:opacity-90 disabled:opacity-50 transition-opacity font-medium"
        >
          {{ isTransitioning ? (t('supportTicketsView.processing') || 'Procesando...') : (t('supportTicketsView.markResolved') || '✅ Marcar como Resuelto') }}
        </button>
      </div>

      <!-- Descripción -->
      <div v-if="ticket.description">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('supportTicketsView.description') || 'Descripción' }}</p>
        <p class="text-sm text-[var(--text-secondary)] whitespace-pre-wrap">{{ ticket.description }}</p>
      </div>

      <!-- Pasos de reproducción -->
      <div v-if="ticket.reproductionSteps">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('supportTicketsView.reproductionSteps') || 'Pasos de Reproducción' }}</p>
        <pre class="text-sm text-[var(--text-secondary)] bg-[var(--bg-app)] rounded-lg p-3 whitespace-pre-wrap font-mono overflow-x-auto">{{ ticket.reproductionSteps }}</pre>
      </div>

      <!-- Stack trace -->
      <div v-if="ticket.stackTrace">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('supportTicketsView.stackTrace') || 'Stack Trace' }}</p>
        <pre class="text-xs text-red-400 bg-[var(--bg-app)] rounded-lg p-3 whitespace-pre-wrap font-mono overflow-x-auto max-h-48">{{ ticket.stackTrace }}</pre>
      </div>

      <!-- Entorno -->
      <div v-if="ticket.browser || ticket.operatingSystem">
        <p class="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">{{ t('supportTicketsView.environment') || 'Entorno' }}</p>
        <div class="grid grid-cols-2 gap-2">
          <div v-if="ticket.browser" class="bg-[var(--bg-app)] rounded-lg p-3">
            <p class="text-xs text-[var(--text-muted)] mb-1">{{ t('supportTicketsView.browser') || 'Navegador' }}</p>
            <p class="text-sm text-[var(--text-primary)]">{{ ticket.browser }}</p>
          </div>
          <div v-if="ticket.operatingSystem" class="bg-[var(--bg-app)] rounded-lg p-3">
            <p class="text-xs text-[var(--text-muted)] mb-1">{{ t('supportTicketsView.operatingSystem') || 'Sistema Operativo' }}</p>
            <p class="text-sm text-[var(--text-primary)]">{{ ticket.operatingSystem }}</p>
          </div>
        </div>
      </div>

      <!-- Error de operación -->
      <div v-if="operationError" class="text-xs text-red-400 bg-red-500/10 rounded-lg p-3">
        {{ operationError }}
      </div>
    </div>
  </div>

  <!-- Estado vacío -->
  <div v-else class="h-full flex items-center justify-center bg-[var(--bg-panel)] border-l border-[var(--border-subtle)]">
    <div class="text-center text-[var(--text-muted)]">
      <p class="text-4xl mb-3">🐛</p>
      <p class="text-sm">{{ t('supportTicketsView.selectTicketPrompt') || 'Selecciona un ticket para ver los detalles' }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ticket, User } from '@/types'
import { useAuthStore } from '@/stores'
import { useSupportTicketsStore } from '@/stores/supportTickets'
import { api } from '@/services/api'

const props = defineProps<{ ticket: Ticket | null }>()
defineEmits<{ close: [] }>()

const { t } = useI18n()
const authStore = useAuthStore()
const store = useSupportTicketsStore()

const selectedAssigneeId = ref('')
const isAssigning = ref(false)
const isTransitioning = ref(false)
const operationError = ref('')
const teamMembers = ref<User[]>([])
const prLink = ref('')
const investigatorName = ref<string | null>(null)

const PLACEHOLDER_PR = /github\.com\/owner\/repo\/|gitlab\.com\/owner\/repo\/|bitbucket\.org\/owner\/repo\//
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

watch(() => props.ticket, async (newTicket) => {
  operationError.value = ''
  selectedAssigneeId.value = newTicket?.assigneeId ?? ''
  prLink.value = newTicket?.prLink ?? ''
  investigatorName.value = null

  if (newTicket && authStore.isTeamLeader) {
    try {
      const members = await api.team.list()
      teamMembers.value = members.filter((m: User) => m.role === 'DEVELOPER')
    } catch {
      // ignorar error al cargar equipo
    }
  }

  if (newTicket) {
    try {
      const events = await api.supportTickets.getEvents(newTicket.id)
      const investigationEvent = events
        .filter((e: any) => e.detail?.to_status === 'INVESTIGATING')
        .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0]
      investigatorName.value = investigationEvent?.user?.full_name ?? null
    } catch {
      // ignorar error al cargar el historial de eventos
    }
  }
}, { immediate: true })

async function handleAssign() {
  if (!selectedAssigneeId.value || !props.ticket) return
  isAssigning.value = true
  operationError.value = ''
  try {
    await store.assign(props.ticket.id, selectedAssigneeId.value)
  } catch (err: any) {
    operationError.value = err?.response?.data?.detail ?? 'Error al asignar'
  } finally {
    isAssigning.value = false
  }
}

async function handleInvestigate() {
  if (!props.ticket) return
  isTransitioning.value = true
  operationError.value = ''
  try {
    await store.investigate(props.ticket.id)
  } catch (err: any) {
    operationError.value = err?.response?.data?.detail ?? 'Error al cambiar estado'
  } finally {
    isTransitioning.value = false
  }
}

async function handleResolve() {
  if (!props.ticket || !prLinkValid.value) return
  isTransitioning.value = true
  operationError.value = ''
  try {
    await store.resolve(props.ticket.id, prLink.value)
  } catch (err: any) {
    operationError.value = err?.response?.data?.detail ?? 'Error al resolver'
  } finally {
    isTransitioning.value = false
  }
}

function statusBadge(status: string): string {
  // Variables CSS calibradas para modo claro y oscuro (global.css)
  const map: Record<string, string> = {
    REPORTED: 'bg-[var(--status-todo-bg)] text-[var(--status-todo-text)]',
    INVESTIGATING: 'bg-[var(--status-progress-bg)] text-[var(--status-progress-text)]',
    RESOLVED: 'bg-[var(--status-done-bg)] text-[var(--status-done-text)]',
  }
  return map[status] ?? 'bg-[var(--bg-app)] text-[var(--text-muted)]'
}

function statusLabel(status: string): string {
  const map: Record<string, string> = {
    REPORTED: t('supportTicketsView.statusReported') || 'Reportado',
    INVESTIGATING: t('supportTicketsView.statusInvestigating') || 'En Investigación',
    RESOLVED: t('supportTicketsView.statusResolved') || 'Resuelto',
  }
  return map[status] ?? status
}

function severityBadge(severity?: string): string {
  // Variables CSS calibradas para modo claro y oscuro (global.css)
  const map: Record<string, string> = {
    CRITICAL: 'bg-[var(--priority-urg-bg)] text-[var(--priority-urg-text)]',
    HIGH: 'bg-[var(--priority-high-bg)] text-[var(--priority-high-text)]',
    MEDIUM: 'bg-[var(--priority-med-bg)] text-[var(--priority-med-text)]',
    LOW: 'bg-[var(--priority-low-bg)] text-[var(--priority-low-text)]',
  }
  return map[severity ?? ''] ?? 'bg-[var(--bg-app)] text-[var(--text-muted)]'
}

function severityIcon(severity?: string): string {
  const map: Record<string, string> = { CRITICAL: '🔴', HIGH: '🟠', MEDIUM: '🟡', LOW: '🟢' }
  return map[severity ?? ''] ?? '⚪'
}

function severityLabel(severity?: string): string {
  const map: Record<string, string> = {
    CRITICAL: t('supportTicketsView.severityTextCritical') || 'Crítica',
    HIGH: t('supportTicketsView.severityTextHigh') || 'Alta',
    MEDIUM: t('supportTicketsView.severityTextMedium') || 'Media',
    LOW: t('supportTicketsView.severityTextLow') || 'Baja',
  }
  return map[severity ?? ''] ?? (t('supportTicketsView.severityNone') || 'Sin severidad')
}
</script>
