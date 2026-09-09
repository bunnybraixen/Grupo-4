<!--
  Vista de Carga de Documentos (Admin / Team Leader)

  Interfaz para cargar archivos de código y documentación.
  El administrador puede asociar archivos a cualquier épica o ticket del sistema.
-->
<template>
  <div class="flex-1 overflow-auto bg-slate-50 dark:bg-slate-900 min-h-screen">
    <AppHeader />
    <div class="p-6 lg:p-8">
    <!-- Encabezado -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-1 text-slate-800 dark:text-white">
        Gestión de Archivos
      </h1>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        Sube archivos de código, documentación y datos. Puedes asociarlos a cualquier épica o ticket del sistema.
      </p>
    </div>

    <!-- Selectores de asociación -->
    <div class="mb-6 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5">
      <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
        Asociar archivos a (opcional)
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Selector de Aplicación -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Aplicación
          </label>
          <select
            v-model="selectedAppId"
            @change="onAppChange"
            class="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Todas las aplicaciones</option>
            <option v-for="app in applications" :key="app.id" :value="app.id">
              {{ app.name }}
            </option>
          </select>
        </div>

        <!-- Selector de Épica -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Épica
          </label>
          <select
            v-model="selectedEpicId"
            :disabled="filteredEpics.length === 0"
            @change="onEpicChange"
            class="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="">Sin épica</option>
            <option v-for="epic in filteredEpics" :key="epic.id" :value="epic.id">
              {{ epic.title }}
            </option>
          </select>
        </div>

        <!-- Selector de Ticket -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Ticket
          </label>
          <select
            v-model="selectedTicketId"
            :disabled="filteredTickets.length === 0"
            class="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <option value="">Sin ticket</option>
            <option v-for="ticket in filteredTickets" :key="ticket.id" :value="ticket.id">
              {{ ticket.title }}
            </option>
          </select>
        </div>

      </div>

      <div v-if="isLoadingContext" class="mt-3 text-xs text-slate-400">
        Cargando datos del sistema...
      </div>
    </div>

    <!-- Componente de upload -->
    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 p-6">
      <FileUpload
        :epicId="selectedEpicId || undefined"
        :ticketId="selectedTicketId || undefined"
        @uploaded="onFileUploaded"
      />
    </div>

    <!-- Guía e info -->
    <div class="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5">
        <h3 class="text-base font-semibold text-slate-800 dark:text-white mb-3">
          Guía Rápida
        </h3>
        <div class="space-y-3 text-sm text-slate-600 dark:text-slate-300">
          <div class="flex gap-3">
            <span class="shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full font-semibold text-xs">1</span>
            <div>
              <p class="font-medium text-slate-800 dark:text-white">Selecciona la asociación</p>
              <p class="text-xs mt-0.5">Elige opcionalmente una aplicación, épica o ticket para vincular el archivo.</p>
            </div>
          </div>
          <div class="flex gap-3">
            <span class="shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full font-semibold text-xs">2</span>
            <div>
              <p class="font-medium text-slate-800 dark:text-white">Arrastra o selecciona</p>
              <p class="text-xs mt-0.5">Sube el archivo desde el área de carga. El progreso se muestra en tiempo real.</p>
            </div>
          </div>
          <div class="flex gap-3">
            <span class="shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-full font-semibold text-xs">3</span>
            <div>
              <p class="font-medium text-slate-800 dark:text-white">Gestiona archivos</p>
              <p class="text-xs mt-0.5">Descarga o elimina archivos desde la lista inferior al componente.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-5">
        <h3 class="text-base font-semibold text-slate-800 dark:text-white mb-3">
          Especificaciones
        </h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-slate-600 dark:text-slate-400">Tamaño máximo</span>
            <span class="font-medium text-slate-800 dark:text-white">25 MB por archivo</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-600 dark:text-slate-400">Tipos permitidos</span>
            <span class="font-medium text-slate-800 dark:text-white">Código, docs, datos</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-600 dark:text-slate-400">Almacenamiento</span>
            <span class="font-medium text-slate-800 dark:text-white">Persistente</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-600 dark:text-slate-400">Registro en BD</span>
            <span class="font-medium text-green-600 dark:text-green-400">Sí</span>
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { api } from '@/services/api'
import type { Application, Epic, Ticket } from '@/types'
import AppHeader from '@/components/layout/AppHeader.vue'

const FileUpload = defineAsyncComponent(() => 
  import('@/components/FileUpload.vue')
)

const selectedAppId = ref('')
const selectedEpicId = ref('')
const selectedTicketId = ref('')
const applications = ref<Application[]>([])
const allEpics = ref<Epic[]>([])
const epicTickets = ref<Ticket[]>([])
const isLoadingContext = ref(false)

const filteredEpics = computed(() =>
  selectedAppId.value
    ? allEpics.value.filter((e) => e.applicationId === selectedAppId.value)
    : allEpics.value
)

const filteredTickets = computed(() => epicTickets.value)

onMounted(async () => {
  await loadContextData()
})

const loadContextData = async () => {
  isLoadingContext.value = true
  try {
    const apps = await api.applications.list()
    applications.value = Array.isArray(apps) ? apps : []

    for (const app of applications.value) {
      try {
        const epics = await api.epics.list(app.id)
        allEpics.value.push(...(Array.isArray(epics) ? epics : []))
      } catch {
        // continuar si falla una app
      }
    }
  } catch (e) {
    console.error('Error cargando contexto admin:', e)
  } finally {
    isLoadingContext.value = false
  }
}

const onAppChange = () => {
  selectedEpicId.value = ''
  selectedTicketId.value = ''
  epicTickets.value = []
}

const onEpicChange = async () => {
  selectedTicketId.value = ''
  epicTickets.value = []
  if (!selectedEpicId.value) return
  try {
    const res = await api.tickets.list({ epicId: selectedEpicId.value })
    const raw = (res as any)?.data?.items ?? (res as any)?.data ?? []
    epicTickets.value = Array.isArray(raw) ? raw : []
  } catch {
    // no bloquear la UI si falla la carga de tickets
  }
}

const onFileUploaded = () => {
  // El componente FileUpload actualiza su lista interna automáticamente
}
</script>

<style scoped>
:deep(code) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}
</style>
