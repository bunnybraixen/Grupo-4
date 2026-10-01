<!--
  SlaSettingsPanel - Configuración y alertas de SLA (NEW-06)

  Se muestra dentro de /admin/builder, en la pestaña "Sprints y SLA".
  Cubre lo que antes no tenía interfaz:
    - Configurar los tiempos objetivo de respuesta/resolución por prioridad y
      persistirlos (solo ADMIN; el backend exige ADMIN en el PUT).
    - Listar los tickets próximos al límite (AT_RISK) o incumplidos (BREACHED),
      con el umbral de alerta aplicado por el backend.

  El cálculo de SLA por ticket (tiempo transcurrido/restante y estado) lo hace
  `app/services/sla_service.py`; aquí solo se configura y se visualiza.
-->
<template>
  <section class="mt-6 space-y-6">
    <!-- ===================== CONFIGURACIÓN DE SLA ===================== -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-[var(--text-primary)]">Objetivos de SLA por prioridad</h2>
          <p class="mt-1 text-sm text-[var(--text-muted)]">
            Define el tiempo objetivo de <strong>respuesta</strong> y de
            <strong>resolución</strong> según la prioridad/severidad del ticket, y el
            <strong>umbral</strong> a partir del cual avisa «próximo a vencer».
          </p>
        </div>
        <div class="flex items-center gap-2">
          <span
            v-if="!isAdmin"
            class="rounded-full bg-[var(--bg-app)] px-2 py-0.5 text-[11px] text-[var(--text-muted)]"
          >
            Solo ADMIN puede editar
          </span>
          <button
            type="button"
            class="rounded-lg border border-[var(--border-subtle)] px-3 py-1.5 text-sm text-[var(--text-primary)]"
            @click="loadConfigs"
          >
            Recargar
          </button>
        </div>
      </div>

      <p
        v-if="saveMessage"
        class="mt-3 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-400"
      >
        {{ saveMessage }}
      </p>
      <p
        v-if="store.error"
        class="mt-3 rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-400"
      >
        {{ store.error }}
      </p>

      <div class="mt-4 overflow-x-auto">
        <table class="w-full min-w-[760px] text-sm">
          <thead>
            <tr class="text-left text-[var(--text-muted)]">
              <th class="py-2 pr-3 font-medium">Prioridad</th>
              <th class="py-2 pr-3 font-medium">Respuesta (min)</th>
              <th class="py-2 pr-3 font-medium">Resolución (min)</th>
              <th class="py-2 pr-3 font-medium">Umbral alerta (%)</th>
              <th class="py-2 pr-3 font-medium">Activa</th>
              <th class="py-2 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in rows"
              :key="row.priority"
              class="border-t border-[var(--border-subtle)]"
            >
              <td class="py-2 pr-3">
                <span class="font-semibold text-[var(--text-primary)]">{{ priorityLabel(row.priority) }}</span>
                <span
                  v-if="row.isDefault"
                  class="ml-2 rounded-full bg-[var(--bg-app)] px-2 py-0.5 text-[10px] text-[var(--text-muted)]"
                  title="Aún no hay fila persistida; se muestran los valores por defecto"
                >
                  por defecto
                </span>
              </td>
              <td class="py-2 pr-3">
                <input
                  v-model.number="row.responseMinutes"
                  type="number"
                  min="1"
                  max="525600"
                  :disabled="!isAdmin"
                  class="w-24 rounded border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2 py-1 text-sm text-[var(--text-primary)] disabled:opacity-60"
                />
              </td>
              <td class="py-2 pr-3">
                <input
                  v-model.number="row.resolutionMinutes"
                  type="number"
                  min="1"
                  max="525600"
                  :disabled="!isAdmin"
                  class="w-24 rounded border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2 py-1 text-sm text-[var(--text-primary)] disabled:opacity-60"
                />
              </td>
              <td class="py-2 pr-3">
                <input
                  v-model.number="row.warnThresholdPercent"
                  type="number"
                  min="1"
                  max="100"
                  :disabled="!isAdmin"
                  class="w-20 rounded border border-[var(--border-subtle)] bg-[var(--bg-app)] px-2 py-1 text-sm text-[var(--text-primary)] disabled:opacity-60"
                />
              </td>
              <td class="py-2 pr-3">
                <input
                  v-model="row.isActive"
                  type="checkbox"
                  :disabled="!isAdmin"
                  class="h-4 w-4 accent-[var(--teal)]"
                />
              </td>
              <td class="py-2">
                <button
                  v-if="isAdmin"
                  type="button"
                  :disabled="saving[row.priority]"
                  class="rounded-lg bg-[var(--teal)] px-3 py-1.5 text-sm text-white hover:bg-[var(--teal-90)] disabled:opacity-50"
                  @click="save(row)"
                >
                  {{ saving[row.priority] ? 'Guardando…' : 'Guardar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===================== ALERTAS DE SLA ===================== -->
    <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-4">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-[var(--text-primary)]">Tickets próximos al límite / incumplidos</h2>
          <p class="mt-1 text-sm text-[var(--text-muted)]">
            Tickets cuyo SLA está <strong>próximo a vencer</strong> (según el umbral) o ya
            <strong>incumplido</strong>. Ordenados por urgencia.
          </p>
        </div>
        <button
          type="button"
          class="rounded-lg border border-[var(--border-subtle)] px-3 py-1.5 text-sm text-[var(--text-primary)]"
          @click="loadAlerts"
        >
          Actualizar
        </button>
      </div>

      <div v-if="alertsLoading" class="py-6 text-center text-sm text-[var(--text-muted)]">
        Calculando SLA…
      </div>

      <p
        v-else-if="!store.slaAlerts.length"
        class="mt-4 rounded-lg border border-dashed border-[var(--border-subtle)] px-3 py-4 text-center text-sm text-[var(--text-muted)]"
      >
        No hay tickets en riesgo ni incumplidos para el filtro actual. 👍
      </p>

      <ul v-else class="mt-4 space-y-2">
        <li
          v-for="alert in store.slaAlerts"
          :key="alert.ticketId"
          class="flex flex-wrap items-center gap-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-app)]/60 px-3 py-2"
        >
          <SlaBadge :status="alert" />
          <span class="min-w-0 flex-1 truncate text-sm text-[var(--text-primary)]">
            {{ alert.title || 'Ticket sin título' }}
          </span>
          <span class="text-[11px] text-[var(--text-muted)]">{{ priorityLabel(alert.priority) }}</span>
          <span class="text-[11px] text-[var(--text-muted)]">· {{ alert.epicTitle || 'Sin épica' }}</span>
          <span class="text-[11px] text-[var(--text-muted)]">· {{ alert.sprintName || 'Sin Sprint' }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
/**
 * SlaSettingsPanel - Configuración de objetivos de SLA + alertas (NEW-06).
 */
import { onMounted, ref, watch } from 'vue'
import { useSprintsStore } from '@/stores/sprints'
import SlaBadge from '@/components/shared/SlaBadge.vue'

const props = defineProps<{
  /** Solo ADMIN puede modificar los objetivos (el backend lo exige) */
  isAdmin: boolean
  /** Proyecto activo del Builder: filtra las alertas */
  applicationId?: string
}>()

const store = useSprintsStore()

/** Fila editable de la tabla de configuración (borrador de una prioridad) */
interface ConfigRow {
  priority: string
  isDefault: boolean
  responseMinutes: number
  resolutionMinutes: number
  warnThresholdPercent: number
  isActive: boolean
}

const rows = ref<ConfigRow[]>([])
const saving = ref<Record<string, boolean>>({})
const saveMessage = ref('')
const alertsLoading = ref(false)

/** Reconstruye las filas editables a partir del store */
const seedRows = (): void => {
  rows.value = store.slaConfigs.map((cfg) => ({
    priority: cfg.priority,
    isDefault: cfg.isDefault,
    responseMinutes: cfg.responseMinutes,
    resolutionMinutes: cfg.resolutionMinutes,
    warnThresholdPercent: cfg.warnThresholdPercent,
    isActive: cfg.isActive
  }))
}

/** Carga la configuración de SLA por prioridad */
const loadConfigs = async (): Promise<void> => {
  saveMessage.value = ''
  try {
    await store.fetchSlaConfigs()
    seedRows()
  } catch {
    // store.error ya contiene el detalle
  }
}

/** Carga las alertas de SLA del proyecto activo */
const loadAlerts = async (): Promise<void> => {
  alertsLoading.value = true
  try {
    await store.fetchSlaAlerts({ applicationId: props.applicationId || undefined, limit: 200 })
  } catch {
    // store.error ya contiene el detalle
  } finally {
    alertsLoading.value = false
  }
}

/** Persiste los objetivos de una prioridad */
const save = async (row: ConfigRow): Promise<void> => {
  saving.value = { ...saving.value, [row.priority]: true }
  saveMessage.value = ''
  try {
    await store.updateSlaConfig(row.priority, {
      responseMinutes: row.responseMinutes,
      resolutionMinutes: row.resolutionMinutes,
      warnThresholdPercent: row.warnThresholdPercent,
      isActive: row.isActive
    })
    saveMessage.value = `Objetivos de prioridad «${priorityLabel(row.priority)}» guardados.`
    await loadConfigs()
  } catch {
    // store.error ya contiene el detalle
  } finally {
    saving.value = { ...saving.value, [row.priority]: false }
  }
}

/** Etiqueta en español de una prioridad */
const priorityLabel = (priority: string): string =>
  ({ LOW: 'Baja', MEDIUM: 'Media', HIGH: 'Alta', URGENT: 'Urgente' })[priority] ?? priority

onMounted(() => {
  void loadConfigs()
  void loadAlerts()
})

// Si cambia el proyecto activo del Builder, refresca las alertas
watch(
  () => props.applicationId,
  () => {
    void loadAlerts()
  }
)
</script>
