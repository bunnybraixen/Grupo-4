<!--
  ============================================================================
  SupportOperationsView.vue — Soporte operacional (Admin / Dev Leader / Dev)
  ============================================================================
  - Cualquier rol levanta tickets con Título + Problema (el timer arranca solo).
  - Los activos muestran el cronómetro corriendo en vivo (tick por segundo).
  - Solo ADMIN / GROUP_LEADER ven el botón "Marcar como resuelto", que abre un
    bloque de texto donde describen los cambios realizados.
  - Los resueltos pasan a la pestaña "Archivados", donde se revisan sus
    detalles y cómo se arreglaron.
  ============================================================================
-->
<template>
  <div class="p-6 max-w-5xl mx-auto text-[var(--text-primary)]">
    <!-- Encabezado -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">Soporte</h1>
        <p class="mt-1 text-sm text-[var(--text-muted)]">
          Tickets operacionales con timer. Los líderes y el admin los resuelven.
        </p>
      </div>
      <button
        class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
        @click="showCreateForm = !showCreateForm"
      >
        {{ showCreateForm ? 'Cancelar' : '+ Nuevo ticket' }}
      </button>
    </div>

    <!-- Formulario de creación: título + problema -->
    <form
      v-if="showCreateForm"
      class="mb-6 space-y-3 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4"
      @submit.prevent="handleCreate"
    >
      <div>
        <label class="mb-1 block text-sm font-medium">Título <span class="text-red-500">*</span></label>
        <input
          v-model="form.title"
          type="text"
          required
          placeholder="Resumen breve del problema"
          class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] px-3 py-2 text-sm outline-none focus:border-blue-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium">Problema <span class="text-red-500">*</span></label>
        <textarea
          v-model="form.problem"
          rows="3"
          required
          placeholder="Describe qué está pasando y cómo afecta..."
          class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] px-3 py-2 text-sm outline-none focus:border-blue-500"
        ></textarea>
      </div>
      <p v-if="formError" class="text-sm text-red-500">{{ formError }}</p>
      <button
        type="submit"
        :disabled="creating || !form.title.trim() || !form.problem.trim()"
        class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {{ creating ? 'Creando...' : 'Crear ticket' }}
      </button>
    </form>

    <p v-if="store.error" class="mb-4 rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
      {{ store.error }}
    </p>

    <!-- Categorías: Activos / Archivados -->
    <div class="mb-4 flex gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="rounded-full border px-4 py-1.5 text-sm font-medium"
        :class="activeTab === tab.id
          ? 'border-blue-600 bg-blue-600 text-white'
          : 'border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-secondary)] hover:bg-[var(--bg-card-hover)]'"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
        <span class="ml-1 opacity-70">({{ tab.count }})</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="py-16 text-center text-sm text-[var(--text-muted)]">
      Cargando tickets...
    </div>

    <!-- ===== TICKETS ACTIVOS (timer corriendo) ===== -->
    <div v-else-if="activeTab === 'open'" class="space-y-3">
      <p v-if="store.openTickets.length === 0" class="py-12 text-center text-sm text-[var(--text-muted)]">
        No hay tickets de soporte activos.
      </p>
      <article
        v-for="ticket in store.openTickets"
        :key="ticket.id"
        class="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <h2 class="font-semibold">{{ ticket.title }}</h2>
            <p class="mt-1 whitespace-pre-wrap text-sm text-[var(--text-secondary)]">{{ ticket.problem }}</p>
            <p class="mt-2 text-xs text-[var(--text-muted)]">
              Levantado por {{ ticket.created_by?.full_name ?? '—' }}
              · {{ formatDate(ticket.created_at) }}
            </p>
          </div>
          <div class="flex shrink-0 flex-col items-end gap-2">
            <!-- Cronómetro en vivo -->
            <span class="rounded-lg bg-slate-700 px-3 py-1.5 font-mono text-sm font-semibold text-white">
              {{ store.formatElapsed(store.elapsedAt(ticket, now)) }}
            </span>
            <span class="flex items-center gap-1.5 text-xs text-emerald-500">
              <span class="h-2 w-2 animate-pulse rounded-full bg-emerald-500"></span>
              En curso
            </span>
            <button
              v-if="canResolve"
              class="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
              @click="openResolve(ticket)"
            >
              Marcar como resuelto
            </button>
          </div>
        </div>
      </article>
    </div>

    <!-- ===== ARCHIVADOS (resueltos, revisión de detalles) ===== -->
    <div v-else class="space-y-3">
      <p v-if="store.archivedTickets.length === 0" class="py-12 text-center text-sm text-[var(--text-muted)]">
        Aún no hay tickets archivados.
      </p>
      <article
        v-for="ticket in store.archivedTickets"
        :key="ticket.id"
        class="rounded-xl border border-amber-500/30 bg-[var(--bg-card)] p-4"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <h2 class="font-semibold">{{ ticket.title }}</h2>
              <span class="rounded-full bg-[var(--status-done-bg)] px-2 py-0.5 text-xs font-medium text-[var(--status-done-text)]">
                Resuelto
              </span>
            </div>
            <p class="mt-1 whitespace-pre-wrap text-sm text-[var(--text-secondary)]">{{ ticket.problem }}</p>

            <!-- Detalle: cómo se arregló -->
            <div class="mt-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] p-3">
              <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                Cambios realizados
              </p>
              <p class="whitespace-pre-wrap text-sm">{{ ticket.resolution_notes || '—' }}</p>
            </div>

            <p class="mt-2 text-xs text-[var(--text-muted)]">
              Levantado por {{ ticket.created_by?.full_name ?? '—' }} ·
              Resuelto por {{ ticket.resolved_by?.full_name ?? '—' }}
              · {{ ticket.resolved_at ? formatDate(ticket.resolved_at) : '' }}
            </p>
          </div>
          <!-- Duración total congelada -->
          <span class="shrink-0 rounded-lg bg-slate-700 px-3 py-1.5 font-mono text-sm font-semibold text-white">
            {{ store.formatElapsed(ticket.elapsed_seconds) }}
          </span>
        </div>
      </article>
    </div>

    <!-- ===== MODAL: RESOLVER TICKET ===== -->
    <div
      v-if="resolvingTicket"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="resolvingTicket = null"
    >
      <div class="w-full max-w-lg rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)] p-6">
        <h2 class="mb-1 text-lg font-semibold">Marcar como resuelto</h2>
        <p class="mb-4 text-sm text-[var(--text-muted)]">{{ resolvingTicket.title }}</p>

        <label class="mb-1 block text-sm font-medium">
          Cambios realizados <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="resolutionNotes"
          rows="5"
          placeholder="Describe los cambios que se hicieron para resolver el problema..."
          class="w-full rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-input)] px-3 py-2 text-sm outline-none focus:border-blue-500"
        ></textarea>
        <p v-if="resolveError" class="mt-2 text-sm text-red-500">{{ resolveError }}</p>

        <div class="mt-4 flex justify-end gap-3">
          <button
            class="rounded-lg border border-[var(--border-subtle)] px-4 py-2 text-sm"
            @click="resolvingTicket = null"
          >
            Cancelar
          </button>
          <button
            class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            :disabled="resolveLoading || resolutionNotes.trim().length < 10"
            @click="handleResolve"
          >
            {{ resolveLoading ? 'Guardando...' : 'Resolver y archivar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSupportOperationsStore } from '@/stores/supportOperations'
import type { OperationalTicket } from '@/types/operationalSupport'

const authStore = useAuthStore()
const store = useSupportOperationsStore()

/** Refresco de los cronómetros en vivo (1 tick por segundo) */
const now = ref(Date.now())
let tickId: number | undefined

const activeTab = ref<'open' | 'archived'>('open')
const showCreateForm = ref(false)
const creating = ref(false)
const formError = ref('')
const form = reactive({ title: '', problem: '' })

const resolvingTicket = ref<OperationalTicket | null>(null)
const resolutionNotes = ref('')
const resolveLoading = ref(false)
const resolveError = ref('')

/** Solo Dev Leader y Admin pueden resolver (el backend también lo exige) */
const canResolve = computed(() => authStore.isAdmin || authStore.isTeamLeader)

const tabs = computed(() => [
  { id: 'open' as const, label: 'Activos', count: store.openTickets.length },
  { id: 'archived' as const, label: 'Archivados', count: store.archivedTickets.length },
])

function formatDate(iso: string): string {
  const d = new Date(iso)
  return isNaN(d.getTime()) ? '' : d.toLocaleString()
}

async function handleCreate() {
  const title = form.title.trim()
  const problem = form.problem.trim()
  if (!title || !problem || creating.value) return

  creating.value = true
  formError.value = ''
  try {
    await store.create({ title, problem })
    form.title = ''
    form.problem = ''
    showCreateForm.value = false
    activeTab.value = 'open'
  } catch (err: any) {
    formError.value = err?.response?.data?.detail ?? 'No se pudo crear el ticket'
  } finally {
    creating.value = false
  }
}

function openResolve(ticket: OperationalTicket) {
  resolvingTicket.value = ticket
  resolutionNotes.value = ''
  resolveError.value = ''
}

async function handleResolve() {
  if (!resolvingTicket.value || resolveLoading.value) return
  const notes = resolutionNotes.value.trim()
  if (notes.length < 10) return

  resolveLoading.value = true
  resolveError.value = ''
  try {
    await store.resolve(resolvingTicket.value.id, notes)
    resolvingTicket.value = null
    activeTab.value = 'archived'
  } catch (err: any) {
    resolveError.value = err?.response?.data?.detail ?? 'No se pudo resolver el ticket'
  } finally {
    resolveLoading.value = false
  }
}

onMounted(() => {
  store.fetchAll()
  tickId = window.setInterval(() => {
    now.value = Date.now()
  }, 1000)
})

onUnmounted(() => {
  if (tickId !== undefined) window.clearInterval(tickId)
})
</script>


