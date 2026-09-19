<!--
  Vista de Constructor (Admin)

  Permite a administradores crear y gestionar aplicaciones, épicas y tickets.
  Flujo: seleccionar aplicación -> crear épica -> crear tickets -> avanzar estado.
-->
<template>
  <div class="p-8 max-w-6xl mx-auto text-[var(--text-primary)]">
    <h1 class="text-3xl font-bold">Constructor de Aplicaciones</h1>
    <p class="mt-2 text-[var(--text-muted)]">
      Crea y gestiona aplicaciones, épicas y tickets
    </p>

    <!-- Selector de aplicación -->
    <div class="mt-6 flex flex-wrap items-center gap-3">
      <select
        v-model="selectedAppId"
        @change="fetchEpics()"
        class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 outline-none focus:border-[var(--teal)]"
      >
        <option value="" disabled>Selecciona una aplicación…</option>
        <option v-for="app in applicationsStore.applications" :key="app.id" :value="app.id">
          {{ app.name }}
        </option>
      </select>
      <button
        @click="showNewApp = !showNewApp"
        class="px-3 py-2 rounded-lg text-sm bg-[var(--teal)] hover:bg-[var(--teal-90)]"
      >
        + Nueva aplicación
      </button>
    </div>

    <!-- Formulario nueva aplicación -->
    <div v-if="showNewApp" class="mt-4 bg-[var(--bg-card)] p-4 rounded-xl border border-[var(--teal)]/50">
      <input
        v-model="newAppName"
        placeholder="Nombre de la aplicación…"
        class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
      />
      <textarea
        v-model="newAppDescription"
        placeholder="Descripción (opcional)"
        rows="2"
        class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
      ></textarea>
      <p v-if="appError" class="text-xs text-red-400 mb-2 font-medium">{{ appError }}</p>
      <div class="flex gap-2">
        <button
          :disabled="!newAppName.trim() || working"
          @click="createApp"
          class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
        >
          Crear aplicación
        </button>
        <button @click="showNewApp = false" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
      </div>
    </div>

    <!-- Nueva épica -->
    <div v-if="selectedAppId" class="mt-6">
      <div v-if="!showNewEpic">
        <button
          @click="showNewEpic = true"
          class="w-full py-3 border-2 border-dashed border-[var(--border-subtle)] rounded-xl text-[var(--text-muted)] hover:border-[var(--teal)] hover:text-[var(--teal)] transition-all font-medium"
        >
          + Añadir nueva Épica
        </button>
      </div>
      <div v-else class="bg-[var(--bg-card)] p-4 rounded-xl border border-[var(--teal)]/50 mb-4">
        <input
          v-model="newEpicTitle"
          @keyup.enter="createEpic"
          placeholder="Nombre de la épica…"
          class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2 mb-3 outline-none"
          autofocus
        />
        <div class="flex gap-2">
          <button
            :disabled="!newEpicTitle.trim() || working"
            @click="createEpic"
            class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
          >
            Guardar
          </button>
          <button @click="showNewEpic = false" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
        </div>
      </div>
      <!-- Cargando / vacío -->
      <div v-if="epicsStore.isLoading" class="text-center py-12 text-[var(--text-muted)]">Cargando épicas…</div>
      <div v-else-if="epicsStore.error" class="text-center py-8 text-red-400 text-sm">{{ epicsStore.error }}</div>
      <div v-else-if="epics.length === 0" class="text-center py-12 text-[var(--text-muted)]">
        Todavía no hay épicas en esta aplicación.
      </div>

      <!-- Lista de épicas -->
      <div
        v-for="epic in epics"
        :key="epic.id"
        class="mt-4 border rounded-xl overflow-hidden bg-[var(--bg-card)]/50 border-[var(--border-subtle)]"
      >
        <div class="p-4 flex items-center justify-between">
          <div>
            <h3 class="font-bold text-lg">{{ epic.title }}</h3>
            <p class="text-xs text-[var(--text-muted)] mt-1">
              {{ (epicTickets[epic.id] || []).length }} ticket(s)
            </p>
          </div>
          <button
            @click="openTicketFormFor = openTicketFormFor === epic.id ? null : epic.id"
            class="px-3 py-1.5 rounded-lg text-sm bg-[var(--teal)]/20 text-[var(--teal)] hover:bg-[var(--teal)]/30"
          >
            + Nuevo ticket
          </button>
        </div>

        <!-- Formulario nuevo ticket -->
        <div v-if="openTicketFormFor === epic.id" class="p-4 border-t border-[var(--border-subtle)] bg-[var(--bg-app)]/30">
          <input
            v-model="ticketForm.title"
            placeholder="Título del ticket *"
            class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 mb-2 outline-none"
          />
          <textarea
            v-model="ticketForm.description"
            placeholder="Descripción (opcional)"
            rows="2"
            class="w-full bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-2 mb-2 outline-none"
          ></textarea>
          <div class="flex flex-wrap gap-2 mb-3">
            <select
              v-model="ticketForm.priority"
              class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
            >
              <option value="LOW">Prioridad: Baja</option>
              <option value="MEDIUM">Prioridad: Media</option>
              <option value="HIGH">Prioridad: Alta</option>
              <option value="URGENT">Prioridad: Urgente</option>
            </select>
            <input
              v-model="ticketForm.dueDate"
              type="date"
              class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg px-3 py-2 text-sm outline-none"
            />
          </div>
          <div class="flex gap-2">
            <button
              :disabled="!ticketForm.title.trim() || working"
              @click="createTicket(epic)"
              class="bg-[var(--teal)] hover:bg-[var(--teal-90)] disabled:opacity-50 px-4 py-1.5 rounded-lg text-sm"
            >
              Crear ticket
            </button>
            <button @click="openTicketFormFor = null" class="text-[var(--text-muted)] px-4 py-1.5 text-sm">Cancelar</button>
          </div>
        </div>

        <!-- Tickets de la épica -->
        <div v-if="(epicTickets[epic.id] || []).length" class="border-t border-[var(--border-subtle)] divide-y divide-[var(--border-subtle)]">
          <div
            v-for="ticket in epicTickets[epic.id]"
            :key="ticket.id"
            class="p-3 flex flex-wrap items-center justify-between gap-2"
          >
            <div class="min-w-0">
              <p class="font-medium truncate">{{ ticket.title }}</p>
              <div class="flex flex-wrap items-center gap-2 mt-1 text-xs">
                <span :class="statusClass(ticket.status)" class="px-2 py-0.5 rounded-full font-medium">{{ statusLabel(ticket.status) }}</span>
                <span :class="priorityClass(ticket.priority)" class="px-2 py-0.5 rounded-full font-medium">{{ priorityLabel(ticket.priority) }}</span>
                <span v-if="ticket.dueDate" class="text-[var(--text-muted)]">📅 {{ ticket.dueDate.slice(0, 10) }}</span>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                v-if="ticket.status === 'TODO'"
                :disabled="working"
                @click="startTicket(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 disabled:opacity-50"
              >
                ▶ Iniciar
              </button>
              <button
                v-if="ticket.status === 'IN_PROGRESS'"
                :disabled="working"
                @click="completeTicket(ticket)"
                class="px-3 py-1 rounded-lg text-xs bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 disabled:opacity-50"
              >
                ✓ Completar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sin aplicaciones -->
    <div v-else-if="!showNewApp && applicationsStore.applications.length === 0" class="mt-10 text-center py-12 text-[var(--text-muted)]">
      No hay aplicaciones todavía. Crea la primera con «+ Nueva aplicación».
    </div>
  </div>
</template>
<script setup lang="ts">
/**
 * BuilderView (Admin) - WEB-08
 * Creación de aplicaciones -> épicas -> tickets y avance básico de estado.
 */
import { ref, computed, onMounted } from 'vue'
import { useApplicationsStore } from '@/stores/applications'
import { useEpicsStore } from '@/stores/epics'
import { useTicketsStore } from '@/stores/tickets'
import { api } from '@/services/api'
import type { Epic, Ticket } from '@/types'

type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'

const applicationsStore = useApplicationsStore()
const epicsStore = useEpicsStore()
const ticketsStore = useTicketsStore()

const selectedAppId = ref('')
const showNewApp = ref(false)
const newAppName = ref('')
const newAppDescription = ref('')
const appError = ref('')

const showNewEpic = ref(false)
const newEpicTitle = ref('')

const openTicketFormFor = ref<string | null>(null)
const ticketForm = ref<{ title: string; description: string; priority: Priority; dueDate: string }>({
  title: '',
  description: '',
  priority: 'MEDIUM',
  dueDate: ''
})

const epicTickets = ref<Record<string, Ticket[]>>({})
const working = ref(false)

const epics = computed(() => epicsStore.epics)

const loadTicketsFor = async (epicId: string): Promise<void> => {
  epicTickets.value[epicId] = await ticketsStore.fetchByEpic(epicId)
}

const fetchEpics = async (): Promise<void> => {
  if (!selectedAppId.value) return
  const list = await epicsStore.fetchByApp(selectedAppId.value)
  await Promise.all(list.map((epic) => loadTicketsFor(epic.id)))
}

const createApp = async (): Promise<void> => {
  working.value = true
  appError.value = ''
  try {
    const created = await api.applications.create({
      name: newAppName.value.trim(),
      description: newAppDescription.value.trim() || undefined
    })
    await applicationsStore.fetchAll()
    selectedAppId.value = created.id
    newAppName.value = ''
    newAppDescription.value = ''
    showNewApp.value = false
    await fetchEpics()
  } catch (err: any) {
    console.error('Error al crear aplicación:', err)
    if (err?.response?.status === 409) {
      appError.value = `Ya existe una aplicación con el nombre "${newAppName.value.trim()}". Por favor elige otro nombre o selecciónala en la lista.`
    } else {
      appError.value = err?.response?.data?.detail || 'Error al crear la aplicación.'
    }
  } finally {
    working.value = false
  }
}

const createEpic = async (): Promise<void> => {
  if (!newEpicTitle.value.trim()) return
  working.value = true
  try {
    await epicsStore.create({
      applicationId: selectedAppId.value,
      title: newEpicTitle.value.trim()
    })
    newEpicTitle.value = ''
    showNewEpic.value = false
    await fetchEpics()
  } catch (err) {
    console.error('Error al crear épica:', err)
  } finally {
    working.value = false
  }
}

const createTicket = async (epic: Epic): Promise<void> => {
  if (!ticketForm.value.title.trim()) return
  working.value = true
  try {
    await ticketsStore.create({
      epicId: epic.id,
      title: ticketForm.value.title.trim(),
      description: ticketForm.value.description.trim() || undefined,
      priority: ticketForm.value.priority,
      dueDate: ticketForm.value.dueDate || undefined
    })
    ticketForm.value = { title: '', description: '', priority: 'MEDIUM', dueDate: '' }
    openTicketFormFor.value = null
    await loadTicketsFor(epic.id)
  } catch (err) {
    console.error('Error al crear ticket:', err)
  } finally {
    working.value = false
  }
}

/** TODO -> IN_PROGRESS (POST /tickets/{id}/start vía api.tickets.updateStatus) */
const startTicket = async (ticket: Ticket): Promise<void> => {
  working.value = true
  try {
    await api.tickets.updateStatus(ticket.id, 'IN_PROGRESS')
    await loadTicketsFor(ticket.epicId)
  } catch (err) {
    console.error('Error al iniciar ticket:', err)
  } finally {
    working.value = false
  }
}

/** IN_PROGRESS -> DONE (POST /tickets/{id}/complete con pr_link opcional) */
const completeTicket = async (ticket: Ticket): Promise<void> => {
  const prLink = window.prompt('Enlace del Pull Request (opcional):')
  if (prLink === null) return
  working.value = true
  try {
    await api.tickets.complete(ticket.id, prLink)
    await loadTicketsFor(ticket.epicId)
  } catch (err) {
    console.error('Error al completar ticket:', err)
  } finally {
    working.value = false
  }
}

const statusLabel = (status: string): string =>
  ({ TODO: 'Por hacer', IN_PROGRESS: 'En progreso', BLOCKED: 'Bloqueado', REDIRECTED: 'Redirigido', DONE: 'Hecho' })[status] ?? status

const priorityLabel = (priority: string): string =>
  ({ LOW: 'Baja', MEDIUM: 'Media', HIGH: 'Alta', URGENT: 'Urgente' })[priority] ?? priority

const statusClass = (status: string): string =>
  ({
    TODO: 'bg-slate-500/20 text-slate-300',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-300',
    BLOCKED: 'bg-red-500/20 text-red-300',
    REDIRECTED: 'bg-amber-500/20 text-amber-300',
    DONE: 'bg-emerald-500/20 text-emerald-300'
  })[status] ?? 'bg-slate-500/20 text-slate-300'

const priorityClass = (priority: string): string =>
  ({
    LOW: 'bg-slate-500/20 text-slate-300',
    MEDIUM: 'bg-yellow-500/20 text-yellow-300',
    HIGH: 'bg-orange-500/20 text-orange-300',
    URGENT: 'bg-red-500/20 text-red-300'
  })[priority] ?? 'bg-slate-500/20 text-slate-300'

onMounted(async () => {
  try {
    await applicationsStore.fetchAll()
    if (applicationsStore.applications.length > 0) {
      selectedAppId.value = applicationsStore.applications[0].id
      await fetchEpics()
    }
  } catch (err) {
    console.error('Error cargando datos del builder:', err)
  }
})
</script>

