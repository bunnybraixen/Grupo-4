<template>
  <!-- Barra lateral izquierda para la vista Builder (Admin) -->
  <!-- Muestra lista de aplicaciones con insignias de estado y opciones de ordenamiento -->
  <aside class="w-64 bg-[var(--bg-sidebar)] border-r border-[var(--border-subtle)] flex flex-col h-screen">
    
    <!-- Encabezado de la barra lateral -->
    <div class="p-4 border-b border-[var(--border-subtle)]">
      <h2 class="text-sm font-semibold text-[var(--text-primary)] mb-3">{{ t('sidebar.applications') }}</h2>
      
      <!-- Controles de ordenamiento -->
      <!-- Permite ordenar las aplicaciones por nombre, tickets pendientes o tickets retrasados -->
      <div class="flex gap-2">
        <button
          v-for="sort in sortOptions"
          :key="sort.id"
          @click="currentSort = sort.id"
          :class="[
            'px-2 py-1 text-xs rounded-md font-medium transition-colors',
            currentSort === sort.id
              ? 'bg-lime/20 text-lime'
              : 'bg-[var(--bg-panel)] text-[var(--text-secondary)] hover:bg-[var(--border-subtle)]'
          ]"
          :title="`Ordenar por ${sort.label}`"
        >
          {{ sort.label }}
        </button>
      </div>
    </div>

    <!-- Lista de aplicaciones -->
    <!-- Muestra cada aplicación con su color distintivo, nombre y badges de estado -->
    <div class="flex-1 overflow-y-auto px-2 py-3 space-y-2">
      <!-- Elemento de aplicación individual -->
      <button
        v-for="app in sortedApplications"
        :key="app.id"
        @click="selectApplication(app.id)"
        :class="[
          'w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative',
          selectedAppId === app.id
            ? 'bg-lime/10'
            : 'hover:bg-[var(--bg-panel)]'
        ]"
      >
        <!-- Indicador de color de la aplicación -->
        <!-- Cada aplicación tiene un color único para identificación visual rápida -->
        <div
          class="w-3 h-3 rounded-full flex-shrink-0"
          :style="{ backgroundColor: app.color }"
          :title="`Color de ${app.name}`"
        ></div>

        <!-- Nombre de la aplicación -->
        <div class="flex-1 text-left min-w-0">
          <p :class="[
            'text-sm font-medium truncate',
            selectedAppId === app.id
              ? 'text-lime'
              : 'text-[var(--text-primary)]'
          ]">
            {{ app.name }}
          </p>
        </div>

        <!-- Insignias de estado de la aplicación -->
        <!-- Se muestran a la derecha indicando tickets pendientes y retrasados -->
        <div class="flex gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          <!-- Insignia de tickets pendientes (naranja) -->
          <span
            v-if="app.pendingCount > 0"
            class="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-200"
            :title="`${app.pendingCount} tickets pendientes`"
          >
            {{ app.pendingCount }}
          </span>
          <!-- Insignia de tickets retrasados (rojo) -->
          <span
            v-if="app.delayedCount > 0"
            class="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200"
            :title="`${app.delayedCount} tickets retrasados`"
          >
            {{ app.delayedCount }}
          </span>
        </div>

        <!-- Insignias siempre visibles en móvil -->
        <div class="flex gap-1 flex-shrink-0 md:hidden">
          <span v-if="app.pendingCount > 0" class="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-200">
            {{ app.pendingCount }}
          </span>
          <span v-if="app.delayedCount > 0" class="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200">
            {{ app.delayedCount }}
          </span>
        </div>
      </button>

      <!-- Estado vacío -->
      <!-- Se muestra cuando no hay aplicaciones disponibles -->
      <div v-if="sortedApplications.length === 0" class="text-center py-8 text-[var(--text-muted)]">
        <p class="text-sm">{{ t('sidebar.noApps') }}</p>
      </div>
    </div>

    <!-- Pie de la barra lateral -->
    <div class="p-4 border-t border-[var(--border-subtle)]">
      <!-- Botón para crear nueva aplicación -->
      <!-- Abre un diálogo modal para la creación de una nueva aplicación -->
      <button
        @click="showCreateAppModal = true"
        class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-lime hover:bg-lime-90 dark:bg-lime dark:hover:bg-lime-90 text-dark-gray rounded-lg font-medium transition-colors text-sm"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ t('sidebar.newApp') }}
      </button>

      <!-- Modal para crear nueva aplicación (se abre cuando showCreateAppModal es true) -->
      <!-- Incluye campos para nombre, descripción y selección de color -->
      <div v-if="showCreateAppModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-[var(--bg-modal)] rounded-lg shadow-lg w-full max-w-md">
          <div class="p-6 border-b border-[var(--border-subtle)]">
            <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ t('sidebar.newApp') }}</h3>
          </div>
          
          <div class="p-6 space-y-4">
            <!-- Campo de nombre -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                {{ t('sidebar.applicationName') }}
              </label>
              <input
                v-model="newAppForm.name"
                type="text"
                class="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-input)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-lime"
                :placeholder="t('sidebar.applicationExample')"
              />
            </div>

            <!-- Campo de descripción -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                {{ t('sidebar.description') }}
              </label>
              <textarea
                v-model="newAppForm.description"
                class="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-input)] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-lime resize-none"
                rows="3"
                :placeholder="t('sidebar.descriptionPlaceholder')"
              ></textarea>
            </div>

            <!-- Selector de color -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                {{ t('sidebar.distinctiveColor') }}
              </label>
              <div class="flex gap-2">
                <button
                  v-for="color in availableColors"
                  :key="color"
                  @click="newAppForm.color = color"
                  :class="[
                    'w-8 h-8 rounded-lg ring-2 transition-all',
                    newAppForm.color === color ? 'ring-slate-900 dark:ring-white ring-offset-2' : 'ring-transparent'
                  ]"
                  :style="{ backgroundColor: color }"
                ></button>
              </div>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="p-6 border-t border-[var(--border-subtle)] flex gap-3">
            <button
              @click="showCreateAppModal = false"
              class="flex-1 px-4 py-2 border border-[var(--border-subtle)] rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-panel)] font-medium transition-colors"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="createApplication"
              :disabled="!newAppForm.name.trim()"
              :class="[
                'flex-1 px-4 py-2 rounded-lg font-medium transition-colors text-dark-gray',
                newAppForm.name.trim()
                  ? 'bg-lime hover:bg-lime-90 dark:bg-lime dark:hover:bg-lime-90'
                  : 'bg-slate-300 dark:bg-[var(--bg-card)] cursor-not-allowed'
              ]"
            >
              {{ t('sidebar.create') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
/**
 * Componente AppSidebar - Barra lateral de aplicaciones para Builder
 * 
 * Responsabilidades:
 * - Mostrar lista de todas las aplicaciones disponibles
 * - Permitir selección de una aplicación para ver sus epics
 * - Mostrar badges con contador de tickets pendientes y retrasados
 * - Permitir ordenamiento por nombre, pendientes o retrasados
 * - Proporcionar botón para crear nueva aplicación
 * - Modal para creación de aplicación con selección de color
 * 
 * Esta es la principal herramienta de navegación para administradores
 * en la vista Builder, permitiendo gestionar múltiples aplicaciones
 * desde una sola interfaz.
 */

import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore, useThemeStore } from '@/stores'
import { useDialogStore } from '@/stores/dialog'

// ============================================================================
// INTERFACES Y TIPOS
// ============================================================================

/**
 * Interfaz para una aplicación en CoreStream
 * Representa una aplicación de nivel superior que contiene epics
 */
interface Application {
  id: string
  name: string
  color: string
  description: string
  pendingCount: number      // Número de tickets en estado TODO
  delayedCount: number      // Número de tickets vencidos
}

/**
 * Interfaz para opciones de ordenamiento
 */
interface SortOption {
  id: 'name' | 'pending' | 'delayed'
  label: string
}

// ============================================================================
// ESTADOS REACTIVOS
// ============================================================================

/**
 * Aplicación seleccionada actualmente
 * Su valor se emite al componente padre para cargar los epics
 */
const selectedAppId = ref<string | null>(null)

/**
 * Opción de ordenamiento actualmente seleccionada
 */
const currentSort = ref<'name' | 'pending' | 'delayed'>('name')

/**
 * Mostrar/ocultar el modal de creación de aplicación
 */
const showCreateAppModal = ref(false)

/**
 * Formulario para crear nueva aplicación
 * Se reinicia cuando se cierra el modal
 */
const newAppForm = ref({
  name: '',
  description: '',
  color: '#3B82F6' // Color azul por defecto
})

// ============================================================================
// DATOS ESTÁTICOS Y DE PRUEBA
// ============================================================================

/**
 * Lista de aplicaciones disponibles
 * En una aplicación real, esto vendría de una API o store global
 */
const applications = ref<Application[]>([
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    name: 'Sistema de Autenticación',
    color: '#3B82F6',
    description: 'Gestión de usuarios y autenticación',
    pendingCount: 5,
    delayedCount: 2
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440002',
    name: 'Panel de Administración',
    color: '#10B981',
    description: 'Dashboard para administradores',
    pendingCount: 3,
    delayedCount: 0
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440003',
    name: 'Base de Datos',
    color: '#F59E0B',
    description: 'Optimización y mantenimiento',
    pendingCount: 8,
    delayedCount: 1
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440004',
    name: 'Integraciones API',
    color: '#EF4444',
    description: 'Conexiones con servicios externos',
    pendingCount: 2,
    delayedCount: 3
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440005',
    name: 'Frontend Web',
    color: '#8B5CF6',
    description: 'Interfaz de usuario principal',
    pendingCount: 6,
    delayedCount: 1
  }
])

/**
 * Opciones de ordenamiento disponibles - computed para soporte i18n
 */
const sortOptions = computed<SortOption[]>(() => [
  { id: 'name', label: t('sidebar.sortByName') },
  { id: 'pending', label: t('sidebar.sortByPending') },
  { id: 'delayed', label: t('sidebar.sortByDelayed') }
])

/**
 * Colores disponibles para las nuevas aplicaciones
 * Proporciona una paleta de colores predeterminada
 */
const availableColors = [
  '#3B82F6', // Azul
  '#10B981', // Verde
  '#F59E0B', // Ámbar
  '#EF4444', // Rojo
  '#8B5CF6', // Púrpura
  '#EC4899', // Rosa
  '#06B6D4', // Cian
  '#6366F1'  // Indigo
]

// ============================================================================
// PROPIEDADES COMPUTADAS
// ============================================================================

/**
 * Aplicaciones ordenadas según la opción de ordenamiento seleccionada
 * Realiza el ordenamiento necesario basado en currentSort
 */
const sortedApplications = computed(() => {
  const sorted = [...applications.value]
  
  switch (currentSort.value) {
    case 'name':
      // Ordenar alfabéticamente por nombre
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    
    case 'pending':
      // Ordenar por mayor cantidad de pendientes primero
      return sorted.sort((a, b) => b.pendingCount - a.pendingCount)
    
    case 'delayed':
      // Ordenar por mayor cantidad de retrasados primero
      return sorted.sort((a, b) => b.delayedCount - a.delayedCount)
    
    default:
      return sorted
  }
})

// ============================================================================
// FUNCIONES
// ============================================================================

/**
 * Selecciona una aplicación
 * En una aplicación real, esto emitiría un evento al componente padre
 * para que cargue los epics de esa aplicación
 *
 * @param appId - ID de la aplicación a seleccionar
 */
const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const dialogStore = useDialogStore()
const selectApplication = (appId: string) => {
  selectedAppId.value = appId
  // Navegamos a la misma ruta pero con el ID en el query param
  router.push({ query: { appId } })
}

/**
 * Crear una nueva aplicación
 * Envía al servidor y actualiza la lista local
 */
const createApplication = async () => {
  if (!newAppForm.value.name.trim()) {
    return
  }

  try {
    // Importar API service
    const { api } = await import('@/services/api')
    
    // Crear aplicación en el backend
    const response = await api.applications.create({
      name: newAppForm.value.name,
      description: newAppForm.value.description,
      color: newAppForm.value.color,
      icon: 'star',
      isActive: true
    } as any)

    // Convertir respuesta al formato local
    const newApp: Application = {
      id: response.id,
      name: response.name,
      color: response.color,
      description: response.description || '',
      pendingCount: 0,
      delayedCount: 0
    }

    // Agregar a la lista
    applications.value.push(newApp)

    // Limpiar formulario y cerrar modal
    newAppForm.value = {
      name: '',
      description: '',
      color: '#3B82F6'
    }
    showCreateAppModal.value = false

    // Seleccionar automáticamente la nueva aplicación
    selectApplication(newApp.id)

    console.log('Nueva aplicación creada exitosamente:', newApp)
  } catch (error) {
    console.error('Error al crear aplicación:', error)
    dialogStore.alert('Error al crear aplicación. Por favor intenta nuevamente.')
  }
}
</script>

<style scoped lang="postcss">
/**
 * Estilos específicos del componente AppSidebar
 */

/* Scrollbar personalizada para mejor visual en el listado */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  @apply bg-transparent;
}

::-webkit-scrollbar-thumb {
  @apply bg-slate-300 dark:bg-dark-gray-60 rounded-full hover:bg-slate-400 dark:hover:bg-[var(--border-color)];
}

/* Animación suave para transiciones */
:deep(*) {
  @apply transition-all duration-200;
}
</style>
