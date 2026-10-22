<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
            {{ t('uploadsPage.tag') }}
          </p>
          <h1 class="text-3xl font-bold text-slate-900 dark:text-white">
            {{ t('uploadsPage.title') }}
          </h1>
        </div>

        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <!-- Buscador -->
          <div class="relative w-full sm:w-72">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('uploadsPage.searchPlaceholder')"
              class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 py-2 pl-9 text-sm text-slate-800 dark:text-white placeholder:text-slate-400 outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            />
            <svg
              class="absolute left-3 top-2.5 h-4 w-4 text-slate-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button
              v-if="searchQuery.trim()"
              @click="searchQuery = ''"
              class="absolute right-2.5 top-2.5 text-xs text-slate-400 hover:text-slate-600"
            >
              ✕
            </button>
          </div>

          <div class="rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-sm text-blue-700 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-200 text-center font-medium">
            {{ totalDocuments }} {{ t('codeDocsPage.visibleFiles') }}
          </div>
        </div>
      </header>

      <!-- Panel de subida con asignación a Ticket -->
      <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-700 dark:text-slate-300">
            {{ t('uploadsPage.uploadToTicket') }}
          </h2>

          <div class="flex items-center gap-2">
            <label class="text-xs font-medium text-slate-500 dark:text-slate-400 whitespace-nowrap">
              {{ t('uploadsPage.assignedTicket') }}
            </label>
            <select
              v-model="selectedTicketId"
              class="rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900 px-3 py-1.5 text-xs text-slate-800 dark:text-white outline-none focus:border-blue-500 max-w-xs truncate"
            >
              <option value="" disabled>{{ t('uploadsPage.selectTicket') }}</option>
              <option v-for="t in availableTickets" :key="t.id" :value="t.id">
                {{ t.title }} ({{ t.appName }})
              </option>
            </select>
          </div>
        </div>

        <div v-if="availableTickets.length === 0 && !isLoading" class="p-4 rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-900/40 dark:bg-amber-950/20 text-xs text-amber-700 dark:text-amber-300">
          {{ t('uploadsPage.noTicketsDeveloper') }}
        </div>

        <div v-else-if="!selectedTicketId" class="p-4 rounded-xl border border-dashed border-slate-300 dark:border-slate-700 text-center text-xs text-slate-500 dark:text-slate-400">
          {{ t('uploadsPage.selectTicketHint') }}
        </div>

        <FileUpload
          v-else
          :key="selectedTicketId"
          :ticket-id="selectedTicketId"
          @uploaded="onFileUploaded"
        />
      </div>

      <div v-if="isLoading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
        {{ t('uploadsPage.loadingFiles') }}
      </div>

      <div v-else-if="filteredGroupedDocuments.length === 0" class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
        {{ searchQuery.trim() ? t('uploadsPage.noSearchResults') : t('uploadsPage.noVisibleFiles') }}
      </div>

      <div v-else class="space-y-6">
        <div v-for="group in filteredGroupedDocuments" :key="group.applicationId || 'sin-proyecto'" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-4 dark:border-slate-700 dark:bg-slate-900/60">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                {{ t('uploadsPage.project') }}
              </p>
              <h2 class="mt-1 text-xl font-semibold text-slate-800 dark:text-white">
                {{ group.applicationName }}
              </h2>
            </div>
            <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200">
              {{ group.documents.length }} {{ group.documents.length === 1 ? t('uploadsPage.file') : t('uploadsPage.files') }}
            </span>
          </div>

          <div class="divide-y divide-slate-200 dark:divide-slate-700">
            <div v-for="doc in group.documents" :key="doc.id" class="flex flex-col gap-3 px-5 py-4 md:flex-row md:items-center md:justify-between">
              <div class="flex min-w-0 items-center gap-3">
                <div :class="['flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-xs font-bold text-white', getFileTypeColor(doc.filename)]">
                  {{ getFileExtDisplay(doc.filename) }}
                </div>

                <div class="min-w-0">
                  <p class="truncate font-medium text-slate-800 dark:text-white">{{ doc.filename }}</p>
                  <div class="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <span>{{ formatFileSize(doc.file_size ?? doc.fileSize ?? 0) }}</span>
                    <span>•</span>
                    <span>{{ formatDocType(doc.doc_type ?? doc.docType) }}</span>
                    <template v-if="doc.ticket_id || doc.ticketId">
                      <span>•</span>
                      <span class="font-medium text-blue-600 dark:text-blue-400">
                        {{ t('uploadsPage.ticketPrefix') }} {{ getTicketTitle(String(doc.ticket_id ?? doc.ticketId)) }}
                      </span>
                    </template>
                    <span>•</span>
                    <span>{{ formatDate(doc.created_at ?? doc.createdAt) }}</span>
                  </div>
                </div>
              </div>

              <div class="flex items-center gap-2 md:justify-end">
                <button
                  type="button"
                  @click="downloadDocument(doc)"
                  class="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100 dark:border-blue-800 dark:bg-blue-950/50 dark:text-blue-200 dark:hover:bg-blue-900/60"
                >
                  {{ t('uploadsPage.download') }}
                </button>
                <button
                  type="button"
                  @click="deleteDocument(doc)"
                  class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200 dark:hover:bg-red-900/60"
                >
                  {{ t('uploadsPage.delete') }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'
import { useAuthStore } from '@/stores/auth'
import FileUpload from '@/components/FileUpload.vue'

const { t } = useI18n()

type DocRow = {
  id: string
  filename: string
  file_size?: number
  fileSize?: number
  mime_type?: string
  mimeType?: string
  doc_type?: string
  docType?: string
  epic_id?: string | null
  epicId?: string | null
  ticket_id?: string | null
  ticketId?: string | null
  uploaded_by_id?: string | null
  uploadedById?: string | null
  created_at?: string
  createdAt?: string
}

type GroupedDocs = {
  applicationId: string | null
  applicationName: string
  documents: DocRow[]
}

type TicketOption = {
  id: string
  title: string
  appName: string
}

const dialogStore = useDialogStore()
const authStore = useAuthStore()

const allDocuments = ref<DocRow[]>([])
const appMap = ref<Map<string, { id: string; name: string }>>(new Map())
const epicMap = ref<Map<string, { id: string; applicationId?: string; title?: string }>>(new Map())
const ticketMap = ref<Map<string, { id: string; epicId?: string; title?: string }>>(new Map())
const availableTickets = ref<TicketOption[]>([])
const selectedTicketId = ref<string>('')
const searchQuery = ref<string>('')
const isLoading = ref(false)

const userRole = computed(() => authStore.user?.role || localStorage.getItem('userRole') || 'DEVELOPER')
const isDeveloper = computed(() => {
  const role = String(userRole.value || '').toUpperCase().replace('USERROLE.', '').replace('-', '_')
  return role === 'DEVELOPER'
})

const totalDocuments = computed(() => allDocuments.value.length)

const groupedDocuments = computed<GroupedDocs[]>(() => {
  const groups = new Map<string, GroupedDocs>()

  for (const doc of allDocuments.value) {
    const docAppId = resolveApplicationId(doc)
    const appId = docAppId || 'sin-proyecto'
    const appName = docAppId ? (appMap.value.get(docAppId)?.name ?? 'Proyecto sin nombre') : 'Sin proyecto'

    if (!groups.has(appId)) {
      groups.set(appId, { applicationId: docAppId, applicationName: appName, documents: [] })
    }
    groups.get(appId)!.documents.push(doc)
  }

  return Array.from(groups.values()).sort((a, b) => a.applicationName.localeCompare(b.applicationName))
})

const filteredGroupedDocuments = computed<GroupedDocs[]>(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return groupedDocuments.value

  const results: GroupedDocs[] = []
  for (const group of groupedDocuments.value) {
    const matchedDocs = group.documents.filter((doc) => {
      const name = (doc.filename || '').toLowerCase()
      const ext = getFileExtension(doc.filename).toLowerCase()
      const type = (doc.doc_type || doc.docType || '').toLowerCase()
      const app = group.applicationName.toLowerCase()
      const ticketTitle = (getTicketTitle(String(doc.ticket_id ?? doc.ticketId ?? '')) || '').toLowerCase()
      return name.includes(q) || ext.includes(q) || type.includes(q) || app.includes(q) || ticketTitle.includes(q)
    })
    if (matchedDocs.length > 0) {
      results.push({
        ...group,
        documents: matchedDocs,
      })
    }
  }
  return results
})

onMounted(async () => {
  await loadDocuments()
})

const normalize = <T>(value: any): T => value?.data ?? value?.items ?? value ?? []

const loadDocuments = async () => {
  isLoading.value = true

  try {
    const apps = normalize<any[]>(await api.applications.list())
    appMap.value = new Map(
      (apps || []).map((app: any) => [String(app.id), { id: String(app.id), name: app.name || 'Proyecto' }])
    )

    for (const app of apps || []) {
      const epics = normalize<any[]>(await api.epics.list(String(app.id)))
      for (const epic of epics || []) {
        epicMap.value.set(String(epic.id), {
          id: String(epic.id),
          applicationId: String(epic.applicationId || app.id),
          title: epic.title || 'Épica',
        })
      }
    }

    // Cargar tickets disponibles según rol
    const ticketOptions: TicketOption[] = []
    if (isDeveloper.value) {
      try {
        const myWorkbenchTickets = normalize<any[]>(await api.tickets.listMyWorkbench())
        for (const t of myWorkbenchTickets || []) {
          const appName = t.appName || appMap.value.get(String(t.applicationId))?.name || 'Mi Ticket'
          ticketOptions.push({
            id: String(t.id),
            title: t.title || 'Ticket',
            appName,
          })
          ticketMap.value.set(String(t.id), {
            id: String(t.id),
            epicId: t.epicId || t.epic_id,
            title: t.title,
          })
        }
      } catch (err) {
        console.error('Error cargando tickets de workbench:', err)
      }
    } else {
      // Team Leader / Group Leader / Admin: tickets de las épicas visibles
      for (const [epicId, epicInfo] of epicMap.value.entries()) {
        try {
          const epTickets = normalize<any[]>(await api.tickets.list({ epicId }))
          const appName = epicInfo.applicationId ? (appMap.value.get(epicInfo.applicationId)?.name || 'Proyecto') : 'Proyecto'
          for (const t of epTickets || []) {
            ticketOptions.push({
              id: String(t.id),
              title: t.title || 'Ticket',
              appName,
            })
            ticketMap.value.set(String(t.id), {
              id: String(t.id),
              epicId,
              title: t.title,
            })
          }
        } catch {
          // Continuar con siguientes épicas
        }
      }
    }

    availableTickets.value = ticketOptions
    if (ticketOptions.length > 0 && !selectedTicketId.value) {
      selectedTicketId.value = ticketOptions[0].id
    }

    const docs = normalize<DocRow[]>(await api.documents.list())
    allDocuments.value = Array.isArray(docs) ? docs : []

    // Asegurar títulos para tickets de documentos listados
    for (const doc of allDocuments.value) {
      const ticketId = String(doc.ticket_id ?? doc.ticketId ?? '')
      if (ticketId && !ticketMap.value.has(ticketId)) {
        try {
          const ticket = normalize<any>(await api.tickets.getById(ticketId))
          const currentTicket = ticket?.data ?? ticket
          if (currentTicket?.id) {
            ticketMap.value.set(String(currentTicket.id), {
              id: String(currentTicket.id),
              epicId: currentTicket.epicId || currentTicket.epic_id,
              title: currentTicket.title,
            })
          }
        } catch {
          // La vista sigue funcionando si el ticket no está disponible
        }
      }
    }
  } catch (error) {
    console.error('Error cargando documentación:', error)
    allDocuments.value = []
  } finally {
    isLoading.value = false
  }
}

const onFileUploaded = async () => {
  await loadDocuments()
}

const getTicketTitle = (ticketId: string): string => {
  if (!ticketId) return ''
  return ticketMap.value.get(ticketId)?.title || ticketId.slice(0, 8)
}

const resolveApplicationId = (doc: DocRow): string | null => {
  const epicId = String(doc.epic_id ?? doc.epicId ?? '')
  const ticketId = String(doc.ticket_id ?? doc.ticketId ?? '')

  if (epicId && epicMap.value.has(epicId)) {
    return epicMap.value.get(epicId)?.applicationId ?? null
  }

  if (ticketId && ticketMap.value.has(ticketId)) {
    const epicIdFromTicket = ticketMap.value.get(ticketId)?.epicId
    if (epicIdFromTicket && epicMap.value.has(epicIdFromTicket)) {
      return epicMap.value.get(epicIdFromTicket)?.applicationId ?? null
    }
  }

  return null
}

const downloadDocument = async (doc: DocRow) => {
  try {
    await api.documents.download(String(doc.id))
  } catch {
    window.open(`/api/documents/${doc.id}/download`, '_blank')
  }
}

const deleteDocument = async (doc: DocRow) => {
  if (!(await dialogStore.confirm('¿Eliminar este archivo?'))) return

  try {
    await api.documents.delete(String(doc.id))
    allDocuments.value = allDocuments.value.filter((item) => item.id !== doc.id)
  } catch (error) {
    console.error('Error al eliminar documento:', error)
  }
}

const formatDate = (value?: string) => {
  if (!value) return 'Sin fecha'
  return new Date(value).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 KB'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const value = bytes / 1024 ** i
  return `${value.toFixed(value >= 10 || i === 0 ? 0 : 1)} ${units[i]}`
}

const formatDocType = (type?: string) => {
  if (!type) return 'Documento'
  return type === 'CODE' ? 'Código' : 'Documentación'
}

const getFileExtension = (filename: string) => {
  const parts = filename.split('.')
  return parts.length > 1 ? `.${parts.pop()!.toLowerCase()}` : ''
}

const getFileTypeColor = (filename: string) => {
  const ext = getFileExtension(filename)
  if (['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.scala'].includes(ext)) return 'bg-blue-600'
  if (['.md', '.pdf', '.docx', '.txt', '.rst', '.doc'].includes(ext)) return 'bg-emerald-600'
  if (['.json', '.yaml', '.yml', '.xml', '.sql', '.csv', '.toml', '.env'].includes(ext)) return 'bg-violet-600'
  return 'bg-slate-600'
}

const getFileExtDisplay = (filename: string) => {
  const ext = getFileExtension(filename)
  return ext ? ext.replace('.', '').slice(0, 2).toUpperCase() : 'FI'
}
</script>
