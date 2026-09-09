<template>
  <div class="flex flex-col h-screen bg-[var(--bg-app)]">
    <AppHeader />

    <div class="flex flex-1 overflow-hidden">

      <!-- Panel izquierdo: lista de tickets -->
      <div class="w-80 shrink-0 border-r border-[var(--border-subtle)] flex flex-col bg-[var(--bg-sidebar)] overflow-hidden">
        <!-- Cabecera -->
        <div class="p-4 border-b border-[var(--border-subtle)]">
          <div class="flex items-center justify-between mb-3">
            <h1 class="text-base font-semibold text-[var(--text-primary)]">{{ t('supportTicketsView.title') || 'Soporte' }}</h1>
            <button
              @click="showCreateForm = true"
              class="px-3 py-1.5 text-xs rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors font-medium"
            >
              {{ t('supportTicketsView.reportBugButton') || '+ Reportar Bug' }}
            </button>
          </div>

          <!-- Contador críticos -->
          <div v-if="store.criticalTickets.length > 0" class="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 rounded-lg px-3 py-2">
            <span>🔴</span>
            <span>{{ store.criticalTickets.length }} {{ t('supportTicketsView.criticalCountSuffix') || 'ticket(s) crítico(s)' }}</span>
          </div>
        </div>

        <!-- Lista scrollable -->
        <div class="flex-1 overflow-y-auto p-3">
          <SupportTicketList
            :selected-id="selectedTicket?.id"
            @select="onSelectTicket"
          />
        </div>
      </div>

      <!-- Panel derecho: detalle del ticket seleccionado -->
      <div class="flex-1 overflow-hidden">
        <SupportTicketPanel
          :ticket="selectedTicket"
          @close="selectedTicketId = null"
        />
      </div>
    </div>

    <!-- Modal de creación -->
    <SupportTicketForm
      v-if="showCreateForm"
      @close="showCreateForm = false"
      @created="onTicketCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Ticket } from '@/types'
import { useSupportTicketsStore } from '@/stores/supportTickets'
import AppHeader from '@/components/layout/AppHeader.vue'
import SupportTicketList from '@/components/support/SupportTicketList.vue'
import SupportTicketPanel from '@/components/support/SupportTicketPanel.vue'
import SupportTicketForm from '@/components/support/SupportTicketForm.vue'

const { t } = useI18n()
const store = useSupportTicketsStore()
const selectedTicketId = ref<string | null>(null)
// Computed reactivo: siempre lee el ticket vigente del store por id, de modo que
// cualquier mutación (investigar/resolver/asignar) se refleja al instante en el panel.
const selectedTicket = computed<Ticket | null>(
  () => store.tickets.find(t => t.id === selectedTicketId.value) ?? null
)
const showCreateForm = ref(false)

onMounted(() => {
  store.fetchAll()
})

function onSelectTicket(ticket: Ticket) {
  selectedTicketId.value = ticket.id
}

function onTicketCreated() {
  // El store ya tiene el nuevo ticket; seleccionarlo si es el primero
  if (store.tickets.length > 0 && !selectedTicketId.value) {
    selectedTicketId.value = store.tickets[0].id
  }
}
</script>
