<template>
  <!-- Barra lateral izquierda para la vista Builder (Admin) -->
  <!-- Muestra lista de aplicaciones reales desde la API -->
  <aside class="w-64 bg-[var(--bg-sidebar)] border-r border-[var(--border-subtle)] flex flex-col h-screen">

    <!-- Encabezado de la barra lateral -->
    <div class="p-4 border-b border-[var(--border-subtle)]">
      <h2 class="text-sm font-semibold text-[var(--text-primary)] mb-3">{{ t('sidebar.applications') }}</h2>

      <!-- Controles de ordenamiento -->
      <div class="flex gap-2">
        <button
          v-for="sort in sortOptions"
          :key="sort.id"
          @click="currentSort = sort.id"
          :class="[
            'px-2 py-1 text-xs rounded-md font-medium transition-colors',
            currentSort === sort.id
              ? 'bg-[var(--accent-cold-2)]/20 text-[var(--accent-cold-2)]'
              : 'bg-[var(--bg-panel)] text-[var(--text-secondary)] hover:bg-[var(--bg-card)]'
          ]"
          :title="`${t('sidebar.sortByLabel')} ${sort.label}`"
        >
          {{ sort.label }}
        </button>
      </div>
    </div>

    <!-- Lista de aplicaciones desde API -->
    <div class="flex-1 overflow-y-auto px-2 py-3 space-y-2">
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-8 text-red-500">
        <p class="text-sm">{{ error }}</p>
        <button @click="loadApplications" class="mt-2 text-xs underline">{{ t('sidebar.retry') }}</button>
      </div>

      <!-- Aplicaciones -->
      <button
        v-for="app in sortedApplications"
        :key="app.id"
        @click="selectApplication(app.id)"
        :class="[
          'w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative',
          selectedAppId === app.id
            ? 'bg-[var(--accent-cold-2)]/10'
            : 'hover:bg-[var(--bg-panel)]'
        ]"
      >
        <!-- Indicador de color -->
        <div
          class="w-3 h-3 rounded-full flex-shrink-0"
          :style="{ backgroundColor: app.color }"
        ></div>

        <!-- Nombre -->
        <div class="flex-1 text-left min-w-0">
          <p :class="[
            'text-sm font-medium truncate',
            selectedAppId === app.id
              ? 'text-[var(--accent-cold-2)]'
              : 'text-[var(--text-primary)]'
          ]" :title="app.name">
            {{ app.name }}
          </p>
        </div>

        <!-- Insignias de estado -->
        <div class="flex gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
          <span
            v-if="app.pendingCount > 0"
            class="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-100 dark:bg-amber-900 text-amber-700 dark:text-amber-200"
          >
            {{ app.pendingCount }}
          </span>
          <span
            v-if="app.delayedCount > 0"
            class="px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200"
          >
            {{ app.delayedCount }}
          </span>
        </div>
      </button>

      <!-- Estado vacío -->
      <div v-if="!isLoading && !error && sortedApplications.length === 0" class="text-center py-8 text-[var(--text-secondary)]">
        <p class="text-sm">{{ t('sidebar.noApps') }}</p>
      </div>
    </div>

    <!-- Pie de la barra lateral -->
    <div class="p-4 border-t border-[var(--border-subtle)]">
      <!-- Botón para crear nueva aplicación -->
      <button
        @click="showCreateAppModal = true"
        class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-[var(--accent-cold-2)] hover:bg-[var(--accent-cold-1)] text-white rounded-lg font-medium transition-colors text-sm"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ t('sidebar.newApp') }}
      </button>

      <!-- Modal para crear nueva aplicación -->
      <div v-if="showCreateAppModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-[var(--bg-card)] rounded-lg shadow-lg w-full max-w-md">
          <div class="p-6 border-b border-[var(--border-subtle)]">
            <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ t('sidebar.newApp') }}</h3>
          </div>

          <div class="p-6 space-y-4">
            <!-- Campo de nombre -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-primary)] mb-2">
                {{ t('sidebar.applicationName') }}
              </label>
              <input
                v-model="newAppForm.name"
                type="text"
                class="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-panel)] text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-cold-2)]"
                :placeholder="t('sidebar.applicationExample')"
              />
            </div>

            <!-- Campo de descripción -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-primary)] mb-2">
                {{ t('sidebar.description') }}
              </label>
              <textarea
                v-model="newAppForm.description"
                class="w-full px-3 py-2 border border-[var(--border-subtle)] rounded-lg bg-[var(--bg-panel)] text-[var(--text-primary)] placeholder-[var(--text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-cold-2)] resize-none"
                rows="3"
                :placeholder="t('sidebar.descriptionPlaceholder')"
              ></textarea>
            </div>

            <!-- Selector de color -->
            <div>
              <label class="block text-sm font-medium text-[var(--text-primary)] mb-3">
                {{ t('sidebar.distinctiveColor') }}
              </label>
              <div class="flex gap-2">
                <button
                  v-for="color in availableColors"
                  :key="color"
                  @click="newAppForm.color = color"
                  :class="[
                    'w-8 h-8 rounded-lg ring-2 transition-all',
                    newAppForm.color === color ? 'ring-[var(--text-primary)] ring-offset-2' : 'ring-transparent'
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
              class="flex-1 px-4 py-2 border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] hover:bg-[var(--bg-panel)] font-medium transition-colors"
            >
              {{ t('common.cancel') }}
            </button>
            <button
              @click="createApplication"
              :disabled="!newAppForm.name.trim() || isCreating"
              :class="[
                'flex-1 px-4 py-2 rounded-lg font-medium transition-colors text-white',
                newAppForm.name.trim() && !isCreating
                  ? 'bg-[var(--accent-cold-2)] hover:bg-[var(--accent-cold-1)]'
                  : 'bg-[var(--bg-panel)] text-[var(--text-secondary)] cursor-not-allowed'
              ]"
            >
              {{ isCreating ? t('sidebar.creating') : t('sidebar.create') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useApplicationsStore } from '@/stores'
import { useDialogStore } from '@/stores/dialog'

// Interfaces
interface Application {
  id: string
  name: string
  color: string
  description: string
  pendingCount: number
  delayedCount: number
}

interface SortOption {
  id: 'name' | 'pending' | 'delayed'
  label: string
}

const { t } = useI18n()
const appsStore = useApplicationsStore()
const dialogStore = useDialogStore()

// Estado reactivo
const selectedAppId = ref<string | null>(null)
const currentSort = ref<'name' | 'pending' | 'delayed'>('name')
const showCreateAppModal = ref(false)
const isCreating = ref(false)
const isLoading = ref(false)
const error = ref<string | null>(null)
const applications = ref<Application[]>([])

// Formulario
const newAppForm = ref({
  name: '',
  description: '',
  color: '#3B82F6'
})

// Opciones de ordenamiento — computed para reactividad i18n
const sortOptions = computed<SortOption[]>(() => [
  { id: 'name', label: t('sidebar.sortNameLabel') },
  { id: 'pending', label: t('sidebar.sortPendingLabel') },
  { id: 'delayed', label: t('sidebar.sortDelayedLabel') },
])

const availableColors = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#EC4899', '#06B6D4', '#6366F1'
]

// Propiedades computadas
const sortedApplications = computed(() => {
  const sorted = [...applications.value]
  
  switch (currentSort.value) {
    case 'name':
      return sorted.sort((a, b) => a.name.localeCompare(b.name))
    case 'pending':
      return sorted.sort((a, b) => b.pendingCount - a.pendingCount)
    case 'delayed':
      return sorted.sort((a, b) => b.delayedCount - a.delayedCount)
    default:
      return sorted
  }
})

// Métodos
const router = useRouter()

const loadApplications = async () => {
  isLoading.value = true
  error.value = null

  try {
    await appsStore.fetchAll()
    applications.value = appsStore.applications.map((app: any) => ({
      id: app.id,
      name: app.name,
      color: app.color || '#3B82F6',
      description: app.description || '',
      pendingCount: app.pendingCount || 0,
      delayedCount: app.delayedCount || 0
    }))
  } catch (err) {
    console.error('Error loading applications:', err)
    error.value = t('sidebar.loadError')
  } finally {
    isLoading.value = false
  }
}

const selectApplication = (appId: string) => {
  selectedAppId.value = appId
  router.push({ query: { appId } })
  appsStore.selectAppById(appId)
}

const createApplication = async () => {
  if (!newAppForm.value.name.trim() || isCreating.value) {
    return
  }

  isCreating.value = true

  try {
    const created = await appsStore.create({
      name: newAppForm.value.name,
      description: newAppForm.value.description,
      color: newAppForm.value.color,
      icon: 'star',
    })

    applications.value.push({
      id: created.id,
      name: created.name,
      color: created.color || '#3B82F6',
      description: created.description || '',
      pendingCount: 0,
      delayedCount: 0,
    })

    newAppForm.value = { name: '', description: '', color: '#3B82F6' }
    showCreateAppModal.value = false

    selectApplication(created.id)
  } catch (err) {
    console.error('Error creating application:', err)
    dialogStore.alert('Error al crear aplicación. Por favor intenta nuevamente.')
  } finally {
    isCreating.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') showCreateAppModal.value = false
}

// Lifecycle
onMounted(() => {
  loadApplications()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="postcss">
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  @apply bg-transparent;
}

::-webkit-scrollbar-thumb {
  @apply bg-slate-300 dark:bg-slate-600 rounded-full hover:bg-slate-400 dark:hover:bg-slate-500;
}

:deep(*) {
  @apply transition-all duration-200;
}
</style>
