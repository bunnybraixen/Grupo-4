<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Lista de Aplicaciones (Vista Constructor) -->
  <!-- ================================================================ -->
  <!-- Sidebar izquierdo que muestra todas las aplicaciones del usuario -->
  <!-- Cada aplicación puede ser seleccionada para ver/editar sus épicas -->
  <!-- Incluye: filtrado, búsqueda, indicadores de estado, y crear nueva -->
  <!-- ================================================================ -->
  
  <div class="flex flex-col h-full bg-slate-900 border-r border-slate-700">
    <!-- ================================================================ -->
    <!-- SECCIÓN: Encabezado -->
    <!-- ================================================================ -->
    <!-- Título y opciones de ordenamiento de aplicaciones -->
    <!-- ================================================================ -->
    <div class="p-4 border-b border-slate-700">
      <h2 class="text-lg font-bold text-white mb-3">Aplicaciones</h2>
      
      <!-- Barra de búsqueda y filtrado -->
      <div class="relative mb-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar aplicación..."
          class="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
        />
        <!-- Icono de búsqueda -->
        <Icon icon="mdi:magnify" class="absolute right-3 top-2.5 text-slate-400" />
      </div>

      <!-- Opciones de ordenamiento -->
      <div class="flex gap-2 text-xs">
        <button
          @click="sortBy = 'name'"
          :class="[
            'px-2 py-1 rounded transition-colors',
            sortBy === 'name'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          ]"
        >
          Por Nombre
        </button>
        <button
          @click="sortBy = 'pending'"
          :class="[
            'px-2 py-1 rounded transition-colors',
            sortBy === 'pending'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          ]"
        >
          Por Pendientes
        </button>
        <button
          @click="sortBy = 'delayed'"
          :class="[
            'px-2 py-1 rounded transition-colors',
            sortBy === 'delayed'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          ]"
        >
          Por Atrasados
        </button>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Lista de Aplicaciones -->
    <!-- ================================================================ -->
    <!-- Renderiza todas las aplicaciones filtradas y ordenadas -->
    <!-- Cada aplicación es un botón seleccionable -->
    <!-- ================================================================ -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="filteredAndSortedApps.length === 0" class="p-4 text-center text-slate-400">
        <Icon icon="mdi:inbox-outline" class="text-4xl mx-auto mb-2" />
        <p>No hay aplicaciones</p>
      </div>

      <div v-else>
        <button
          v-for="app in filteredAndSortedApps"
          :key="app.id"
          @click="selectApp(app)"
          :class="[
            'w-full px-4 py-3 border-l-4 transition-all duration-200 hover:bg-slate-800',
            selectedAppId === app.id
              ? 'border-l-blue-500 bg-slate-800'
              : 'border-l-transparent bg-slate-900 hover:bg-slate-800'
          ]"
        >
          <!-- Contenedor flex para alineación de contenido -->
          <div class="flex items-center gap-3">
            <!-- Círculo de color con icono de la aplicación -->
            <div
              :style="{ backgroundColor: app.color }"
              class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
            >
              <Icon :icon="app.icon" class="text-white" />
            </div>

            <!-- Nombre y meta-información de la aplicación -->
            <div class="flex-1 text-left min-w-0">
              <p class="text-white font-medium truncate">{{ app.name }}</p>
              <p class="text-xs text-slate-400">{{ app.epicCount }} épicas</p>
            </div>

            <!-- Indicadores de estado: tickets pendientes y atrasados -->
            <div class="flex gap-2 flex-shrink-0">
              <!-- Badge: cantidad de tickets pendientes -->
              <span
                v-if="app.pendingCount > 0"
                class="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-yellow-500 text-yellow-900 rounded-full"
              >
                {{ app.pendingCount }}
              </span>

              <!-- Badge: cantidad de tickets atrasados (en rojo) -->
              <span
                v-if="app.delayedCount > 0"
                class="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-red-500 text-white rounded-full"
              >
                {{ app.delayedCount }}
              </span>
            </div>
          </div>
        </button>
      </div>
    </div>

    <!-- ================================================================ -->
    <!-- SECCIÓN: Pie de página -->
    <!-- ================================================================ -->
    <!-- Botón para crear nueva aplicación -->
    <!-- ================================================================ -->
    <div class="p-4 border-t border-slate-700">
      <button
        v-if="!isCreatingApp"
        @click="isCreatingApp = true"
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        <Icon icon="mdi:plus" />
        Nueva Aplicación
      </button>

      <!-- Input en línea para crear nueva aplicación -->
      <div v-else class="flex gap-2">
        <input
          v-model="newAppName"
          @keydown.enter="createNewApp"
          @keydown.escape="isCreatingApp = false"
          type="text"
          placeholder="Nombre..."
          autofocus
          class="flex-1 px-3 py-2 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
        />
        <button
          @click="createNewApp"
          class="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
        >
          <Icon icon="mdi:check" />
        </button>
        <button
          @click="isCreatingApp = false"
          class="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
        >
          <Icon icon="mdi:close" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useApplicationsStore } from '@/stores/applications'

// =====================================================================
// DEFINICIÓN DE TIPOS
// =====================================================================

interface Application {
  id: string
  name: string
  color: string
  icon: string
  epicCount: number
  pendingCount: number
  delayedCount: number
}

// =====================================================================
// ESTADO LOCAL (COMPOSABLE)
// =====================================================================

// Query de búsqueda para filtrar aplicaciones
const searchQuery = ref('')

// Campo de ordenamiento actual
const sortBy = ref<'name' | 'pending' | 'delayed'>('name')

// ID de la aplicación actualmente seleccionada
const selectedAppId = ref<string | null>(null)

// Control de creación de nueva aplicación
const isCreatingApp = ref(false)

// Nombre de la nueva aplicación siendo creada
const newAppName = ref('')

// =====================================================================
// STORE Y DATOS
// =====================================================================

// Acceso al store de aplicaciones
const applicationsStore = useApplicationsStore()

// =====================================================================
// PROPIEDADES COMPUTADAS
// =====================================================================

/**
 * Aplicaciones filtradas por búsqueda y ordenadas
 * Combina filtrado por nombre y ordenamiento según selección del usuario
 */
const filteredAndSortedApps = computed(() => {
  // Filtrar por query de búsqueda
  let filtered = applicationsStore.applications.filter(app =>
    app.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )

  // Ordenar según la selección del usuario
  switch (sortBy.value) {
    case 'pending':
      // Ordenar por cantidad de tickets pendientes (descendente)
      return filtered.sort((a, b) => b.pendingCount - a.pendingCount)
    case 'delayed':
      // Ordenar por cantidad de tickets atrasados (descendente)
      return filtered.sort((a, b) => b.delayedCount - a.delayedCount)
    case 'name':
    default:
      // Ordenar alfabéticamente por nombre
      return filtered.sort((a, b) => a.name.localeCompare(b.name))
  }
})

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Selecciona una aplicación y emite evento
 * Carga las épicas asociadas a la aplicación seleccionada
 * @param app - Aplicación seleccionada
 */
const selectApp = (app: Application) => {
  selectedAppId.value = app.id
  emit('select', app)
}

/**
 * Crea una nueva aplicación con el nombre ingresado
 * Valida que el nombre no esté vacío
 * Limpia el estado de creación después de completar
 */
const createNewApp = () => {
  // Validación: nombre no vacío y con al menos 1 carácter
  if (newAppName.value.trim().length === 0) {
    return
  }

  // Llamar al store para crear la aplicación
  applicationsStore.createApplication(newAppName.value)

  // Limpiar estado de creación
  newAppName.value = ''
  isCreatingApp.value = false
}

// =====================================================================
// EMITS
// =====================================================================

// Emite cuando se selecciona una aplicación
const emit = defineEmits<{
  select: [app: Application]
}>()
</script>

<style scoped>
/* Estilos personalizados si es necesario */
</style>
