<template>
  <div class="fixed inset-0 z-[110] flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="w-full max-w-lg bg-[var(--bg-panel)] rounded-xl shadow-xl border border-[var(--border-subtle)] p-6 mx-4 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between mb-5">
        <h2 class="text-lg font-semibold text-[var(--text-primary)]">{{ t('supportTicketsView.formTitle') || 'Reportar Bug de Soporte' }}</h2>
        <button
          type="button"
          @click="$emit('close')"
          class="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
        >
          ✕
        </button>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Título -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
            {{ t('supportTicketsView.fieldTitle') || 'Título' }} <span class="text-red-400">*</span>
          </label>
          <input
            v-model="form.title"
            type="text"
            required
            :placeholder="t('supportTicketsView.titlePlaceholder') || 'Descripción breve del bug'"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500"
          />
        </div>

        <!-- Descripción -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.description') || 'Descripción' }}</label>
          <textarea
            v-model="form.description"
            rows="3"
            :placeholder="t('supportTicketsView.descriptionPlaceholder') || 'Explica el comportamiento inesperado...'"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500 resize-none"
          />
        </div>

        <!-- Severidad -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.severityLabel') || 'Severidad' }}</label>
          <select
            v-model="form.severity"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-blue-500"
          >
            <option value="CRITICAL">{{ t('supportTicketsView.severityCritical') || '🔴 Crítica' }}</option>
            <option value="HIGH">{{ t('supportTicketsView.severityHigh') || '🟠 Alta' }}</option>
            <option value="MEDIUM">{{ t('supportTicketsView.severityMedium') || '🟡 Media' }}</option>
            <option value="LOW">{{ t('supportTicketsView.severityLow') || '🟢 Baja' }}</option>
          </select>
        </div>

        <!-- Ticket / épica relacionada -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.linkedTicketLabel') || 'Ticket relacionado (opcional)' }}</label>
          <select
            v-model="form.linkedTicketId"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] focus:outline-none focus:border-blue-500"
          >
            <option value="">{{ t('supportTicketsView.linkedTicketNone') || 'Ninguno' }}</option>
            <option v-for="linkable in linkableTickets" :key="linkable.id" :value="linkable.id">
              {{ linkable.title }}<template v-if="linkable.epicTitle"> — {{ linkable.epicTitle }}</template>
            </option>
          </select>
        </div>

        <!-- Pasos de reproducción -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.reproductionSteps') || 'Pasos de Reproducción' }}</label>
          <textarea
            v-model="form.reproductionSteps"
            rows="4"
            :placeholder="t('supportTicketsView.reproductionStepsPlaceholder') || '1. Ir a ...\n2. Hacer clic en ...\n3. Observar que ...'"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500 resize-none font-mono text-sm"
          />
        </div>

        <!-- Stack trace -->
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.stackTrace') || 'Stack Trace' }}</label>
          <textarea
            v-model="form.stackTrace"
            rows="4"
            :placeholder="t('supportTicketsView.stackTracePlaceholder') || 'Pega aquí el stack trace del error...'"
            class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500 resize-none font-mono text-sm"
          />
        </div>

        <!-- Navegador y SO en grid -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.browser') || 'Navegador' }}</label>
            <input
              v-model="form.browser"
              type="text"
              :placeholder="t('supportTicketsView.browserPlaceholder') || 'Chrome 120, Firefox 121...'"
              class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">{{ t('supportTicketsView.operatingSystem') || 'Sistema Operativo' }}</label>
            <input
              v-model="form.operatingSystem"
              type="text"
              :placeholder="t('supportTicketsView.osPlaceholder') || 'Windows 11, macOS 14...'"
              class="w-full px-3 py-2 rounded-lg bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>

        <!-- Botones -->
        <div class="flex gap-3 pt-2">
          <button
            type="button"
            @click="$emit('close')"
            class="flex-1 px-4 py-2 rounded-lg border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:bg-[var(--bg-app)] transition-colors"
          >
            {{ t('supportTicketsView.cancel') || 'Cancelar' }}
          </button>
          <button
            type="submit"
            :disabled="isSubmitting || !form.title.trim()"
            class="flex-1 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ isSubmitting ? (t('supportTicketsView.submitting') || 'Reportando...') : (t('supportTicketsView.submitReport') || 'Reportar Bug') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ticket } from '@/types'
import { useSupportTicketsStore } from '@/stores/supportTickets'
import { api } from '@/services/api'

const emit = defineEmits<{
  close: []
  created: []
}>()

const { t } = useI18n()
const store = useSupportTicketsStore()
const isSubmitting = ref(false)
const linkableTickets = ref<Ticket[]>([])

const form = reactive({
  title: '',
  description: '',
  severity: 'MEDIUM',
  reproductionSteps: '',
  stackTrace: '',
  browser: '',
  operatingSystem: '',
  linkedTicketId: '',
})

onMounted(async () => {
  try {
    linkableTickets.value = await api.supportTickets.listLinkableTickets()
  } catch {
    // ignorar error al cargar la lista de tickets vinculables
  }
})

async function handleSubmit() {
  if (!form.title.trim() || isSubmitting.value) return
  isSubmitting.value = true
  try {
    await store.create({
      title: form.title.trim(),
      description: form.description.trim() || undefined,
      severity: form.severity,
      reproductionSteps: form.reproductionSteps.trim() || undefined,
      stackTrace: form.stackTrace.trim() || undefined,
      browser: form.browser.trim() || undefined,
      operatingSystem: form.operatingSystem.trim() || undefined,
      linkedTicketId: form.linkedTicketId || undefined,
    })
    emit('created')
    emit('close')
  } finally {
    isSubmitting.value = false
  }
}
</script>
