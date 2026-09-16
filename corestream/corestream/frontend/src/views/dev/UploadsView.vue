<!--
  Vista de Gestión de Archivos (Developer / Team Leader)

  Permite subir, descargar y eliminar documentos asociados a épicas o tickets.
  Los archivos quedan registrados en la base de datos con trazabilidad completa.
-->
<template>
  <div class="flex flex-col min-h-screen bg-slate-50 dark:bg-gray-950">
    <AppHeader />

    <div class="flex-1 overflow-auto p-6 lg:p-8">
      <!-- Encabezado -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Mis Archivos</h1>
        <p class="mt-1 text-gray-600 dark:text-gray-400">
          Sube y gestiona documentos de código o documentación asociados a tu trabajo
        </p>
      </div>

      <!-- Selectores de asociación -->
      <div class="mb-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-sm">
        <h2 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Asociar archivos a (opcional)
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Selector de Épica -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Épica
            </label>
            <select
              v-model="selectedEpicId"
              @change="selectedTicketId = ''"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sin épica seleccionada</option>
              <option v-for="epic in epics" :key="epic.id" :value="epic.id">
                {{ epic.title }}
              </option>
            </select>
          </div>

          <!-- Selector de Ticket -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Ticket
            </label>
            <select
              v-model="selectedTicketId"
              @change="selectedEpicId = ''"
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Sin ticket seleccionado</option>
              <option v-for="ticket in workbenchTickets" :key="ticket.id" :value="ticket.id">
                {{ ticket.title }}
              </option>
            </select>
          </div>
        </div>

        <p v-if="selectedEpicId || selectedTicketId" class="mt-3 text-xs text-blue-600 dark:text-blue-400">
          Los archivos que subas se asociarán a
          <strong>{{ selectedEpicId ? epicLabel : ticketLabel }}</strong>.
          Cambia el selector para ver/subir archivos de otra épica o ticket.
        </p>
        <p v-else class="mt-3 text-xs text-gray-500 dark:text-gray-400">
          Si no seleccionas ninguna asociación, el archivo no quedará vinculado a ningún elemento de trabajo.
        </p>
      </div>

      <!-- Componente de carga -->
      <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-6 shadow-sm">
        <FileUpload
          :epicId="selectedEpicId || undefined"
          :ticketId="selectedTicketId || undefined"
          @uploaded="onFileUploaded"
          @deleted="onFileDeleted"
        />
      </div>

      <!-- Estado de carga de contexto -->
      <div v-if="isLoadingContext" class="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
        Cargando épicas y tickets...
      </div>

      <!-- Ayuda -->
      <div class="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-5">
        <div class="flex gap-3">
          <span class="text-xl shrink-0">💡</span>
          <div class="text-sm text-blue-800 dark:text-blue-300">
            <p class="font-semibold mb-1">Consejos</p>
            <ul class="list-disc list-inside space-y-1 text-xs">
              <li>Asocia los archivos a un ticket o épica para encontrarlos fácilmente desde el tablero.</li>
              <li>Los archivos persisten entre reinicios del sistema.</li>
              <li>Tamaño máximo: 25 MB por archivo.</li>
              <li>Tipos soportados: código (.py, .js, .ts…), documentación (.md, .pdf…) y datos (.json, .csv…).</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { api } from '@/services/api'
import type { Epic, Ticket } from '@/types'

const FileUpload = defineAsyncComponent(() => 
  import('@/components/FileUpload.vue')
)

const selectedEpicId = ref('')
const selectedTicketId = ref('')
const epics = ref<Epic[]>([])
const workbenchTickets = ref<Ticket[]>([])
const isLoadingContext = ref(false)

const epicLabel = computed(() => {
  const e = epics.value.find((ep) => ep.id === selectedEpicId.value)
  return e?.title ?? selectedEpicId.value
})

const ticketLabel = computed(() => {
  const t = workbenchTickets.value.find((tk) => tk.id === selectedTicketId.value)
  return t?.title ?? selectedTicketId.value
})

onMounted(async () => {
  await loadContextData()
})

const loadContextData = async () => {
  isLoadingContext.value = true
  try {
    // Cargar tickets asignados al usuario actual
    const tickets = await api.tickets.listMyWorkbench()
    workbenchTickets.value = Array.isArray(tickets) ? tickets : []
  } catch (e) {
    console.error('Error cargando workbench tickets:', e)
  }

  try {
    // Cargar épicas de todas las aplicaciones disponibles
    const apps = await api.applications.list()
    const appList = Array.isArray(apps) ? apps : []

    for (const app of appList) {
      try {
        const appEpics = await api.epics.list(app.id)
        const epicList = Array.isArray(appEpics) ? appEpics : []
        epics.value.push(...epicList)
      } catch {
        // Si falla la carga de épicas de una app, continuar con las demás
      }
    }
  } catch (e) {
    console.error('Error cargando aplicaciones/épicas:', e)
  } finally {
    isLoadingContext.value = false
  }
}

const onFileUploaded = () => {
  // El componente FileUpload ya actualiza su propia lista interna
}

const onFileDeleted = () => {
  // El componente FileUpload ya actualiza su propia lista interna
}
</script>
