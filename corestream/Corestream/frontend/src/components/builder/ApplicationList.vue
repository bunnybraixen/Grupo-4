<!--
  Componente: ApplicationList (Sidebar)
  
  Muestra la lista de aplicaciones en un sidebar a la izquierda.
  Permite:
  - Ver todas las apps disponibles
  - Seleccionar una app (click)
  - Crear nueva app (botón + Nuevo)
  - Eliminar app (botón X - solo para admins)
  
  DEPENDENCIAS EXTERNAS:
  - useApplicationsStore: Para obtener/gestionar aplicaciones
  - useAuthStore: Para verificar si es admin
  
  Estilos: Tailwind CSS
-->

<template>
  <div class="w-64 bg-white border-r border-gray-200 h-screen overflow-y-auto flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-gray-200">
      <h2 class="text-xl font-bold text-gray-900">Aplicaciones</h2>
      <p class="text-sm text-gray-500 mt-1">{{ applications.length }} total</p>
    </div>

    <!-- Lista de Aplicaciones -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="applications.length === 0" class="p-6 text-center">
        <p class="text-gray-500 text-sm">No hay aplicaciones</p>
      </div>

      <div v-else class="space-y-2 p-4">
        <div
          v-for="app in applications"
          :key="app.id"
          @click="handleSelectApp(app)"
          class="group relative p-3 rounded-lg cursor-pointer transition-all"
          :class="[
            selectedApp?.id === app.id
              ? 'bg-blue-50 border-l-4 border-blue-500'
              : 'hover:bg-gray-50 border-l-4 border-transparent'
          ]"
        >
          <!-- Contenido principal -->
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h3 class="font-medium text-gray-900 truncate">{{ app.name }}</h3>
              <p class="text-xs text-gray-500 mt-1">
                {{ app.epicCount || 0 }} épicas · {{ (app.pendingCount || 0) + (app.delayedCount || 0) }} pendientes
              </p>
            </div>

            <!-- Botón Delete (solo para admins) -->
            <button
              v-if="isAdminOrLeader"
              @click.stop="handleDeleteApp(app.id)"
              class="opacity-0 group-hover:opacity-100 ml-2 p-1 text-gray-400 hover:text-red-600 transition-all"
              title="Eliminar aplicación"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          <!-- Progress bar -->
          <div class="mt-2 h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-green-500 transition-all"
              :style="{ width: `${(app as any).progress || 0}%` }"
            />
          </div>

          <!-- ═════════════════════════════════════════════════════════════ -->
          <!-- BADGES DINÁMICOS: Pendientes y Retrasados (FIX-004) -->
          <!-- ═════════════════════════════════════════════════════════════ -->
          <div class="mt-3 flex gap-2 flex-wrap">
            <!-- Badge PENDIENTES (TODO tasks) -->
            <span
              v-if="(app.pendingCount || 0) > 0"
              class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-yellow-100 text-yellow-800"
              :title="`${app.pendingCount} tareas pendientes (TODO)`"
            >
              <span class="text-sm">📋</span>
              {{ app.pendingCount }} pendientes
            </span>

            <!-- Badge RETRASADOS (Overdue) - CON PULSO PARA URGENCIA -->
            <span
              v-if="(app.delayedCount || 0) > 0"
              class="inline-flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-red-100 text-red-800 animate-pulse"
              :title="`${app.delayedCount} tareas retrasadas`"
            >
              <span class="text-sm">⏰</span>
              {{ app.delayedCount }} retrasados
            </span>

            <!-- Estado de Éxito: Mostrar si no hay pendientes ni retrasados -->
            <span
              v-if="(app.pendingCount || 0) === 0 && (app.delayedCount || 0) === 0"
              class="inline-flex items-center text-xs text-green-600 font-semibold"
            >
              ✓ Todo al día
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Botón Crear App -->
    <div class="p-4 border-t border-gray-200">
      <button
        @click="showCreateDialog = true"
        class="w-full py-2 px-4 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors text-sm"
      >
        + Nueva Aplicación
      </button>
    </div>

    <!-- Dialog Create Application -->
    <div v-if="showCreateDialog" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96 shadow-xl">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Nueva Aplicación</h3>

        <form @submit.prevent="handleCreateApp" class="space-y-4">
          <!-- Name Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              v-model="newAppForm.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Mi Aplicación"
              required
            />
          </div>

          <!-- Description Input -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descripción (opcional)</label>
            <textarea
              v-model="newAppForm.description"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe el propósito de la aplicación..."
              rows="3"
            />
          </div>

          <!-- Color Picker -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
            <div class="flex gap-2">
              <input
                v-model="newAppForm.color"
                type="color"
                class="w-10 h-10 rounded cursor-pointer"
              />
              <input
                type="text"
                v-model="newAppForm.color"
                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                placeholder="#2563EB"
              />
            </div>
          </div>

          <!-- Buttons -->
          <div class="flex gap-2 pt-4">
            <button
              type="submit"
              class="flex-1 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
              :disabled="isLoadingCreate"
            >
              {{ isLoadingCreate ? 'Creando...' : 'Crear' }}
            </button>
            <button
              type="button"
              @click="showCreateDialog = false"
              class="flex-1 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-medium transition-colors"
            >
              Cancelar
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="createError" class="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
            {{ createError }}
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useApplicationsStore } from '@/stores'
import { useAuthStore } from '@/stores'
import type { Application } from '@/types'
import { useDialogStore } from '@/stores/dialog'

// Store
const appsStore = useApplicationsStore()
const authStore = useAuthStore()
const dialogStore = useDialogStore()

// Computed
const applications = computed(() => appsStore.sortedByName)
const selectedApp = computed(() => appsStore.selectedApp)
// Borrar aplicación es ADMIN+TEAM_LEADER en el backend (_MANAGERS, applications.py)
const isAdminOrLeader = computed(() => ['ADMIN', 'TEAM_LEADER'].includes(authStore.user?.role ?? ''))

// State
const showCreateDialog = ref(false)
const isLoadingCreate = ref(false)
const createError = ref('')
const newAppForm = ref({
  name: '',
  description: '',
  color: '#2563EB',
  icon: 'folder'
})

// Methods
const handleSelectApp = (app: Application) => {
  appsStore.selectApp(app)
}

const handleCreateApp = async () => {
  if (!newAppForm.value.name.trim()) {
    createError.value = 'El nombre es requerido'
    return
  }

  isLoadingCreate.value = true
  createError.value = ''

  try {
    await appsStore.create({
      name: newAppForm.value.name,
      description: newAppForm.value.description,
      color: newAppForm.value.color,
      icon: newAppForm.value.icon
    })

    // Reset form
    newAppForm.value = {
      name: '',
      description: '',
      color: '#2563EB',
      icon: 'folder'
    }
    showCreateDialog.value = false
  } catch (error) {
    createError.value = error instanceof Error ? error.message : 'Error al crear aplicación'
  } finally {
    isLoadingCreate.value = false
  }
}

const handleDeleteApp = async (appId: string) => {
  if (await dialogStore.confirm('¿Estás seguro de que quieres eliminar esta aplicación? Esto eliminará todos sus épicos y tareas.')) {
    try {
      await appsStore.remove(appId)
    } catch (error) {
      console.error('Error al eliminar aplicación:', error)
    }
  }
}
</script>
