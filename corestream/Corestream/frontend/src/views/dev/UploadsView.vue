<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">
            Mis Cargas
          </p>
          <h1 class="text-3xl font-bold text-slate-900 dark:text-white">
            Archivos de mis tickets
          </h1>
        </div>
        <div class="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm text-blue-700 dark:border-blue-800 dark:bg-blue-950/40 dark:text-blue-200">
          {{ totalDocuments }} documentos visibles
        </div>
      </header>

      <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
          Subir archivo
        </h2>
        <FileUpload />
      </div>

      <div v-if="isLoading" class="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
        Cargando tus archivos...
      </div>

      <div v-else-if="groupedDocuments.length === 0" class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300">
        No tienes documentos visibles todavía.
      </div>

      <div v-else class="space-y-6">
        <div v-for="group in groupedDocuments" :key="group.applicationId || 'sin-proyecto'" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div class="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-5 py-4 dark:border-slate-700 dark:bg-slate-900/60">
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
                Proyecto
              </p>
              <h2 class="mt-1 text-xl font-semibold text-slate-800 dark:text-white">
                {{ group.applicationName }}
              </h2>
            </div>
            <span class="rounded-full bg-slate-200 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200">
              {{ group.documents.length }} archivos
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
                  Descargar
                </button>
                <button
                  type="button"
                  @click="deleteDocument(doc)"
                  class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-100 dark:border-red-900 dark:bg-red-950/40 dark:text-red-200 dark:hover:bg-red-900/60"
                >
                  Eliminar
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
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'
import FileUpload from '@/components/FileUpload.vue'

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

const dialogStore = useDialogStore()
const allDocuments = ref<DocRow[]>([])
const appMap = ref<Map<string, { id: string; name: string }>>(new Map())
const epicMap = ref<Map<string, { id: string; applicationId?: string; title?: string }>>(new Map())
const ticketMap = ref<Map<string, { id: string; epicId?: string }>>(new Map())
const isLoading = ref(false)

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

onMounted(async () => {
  await loadDocuments()
})

const normalize = <T>(value: any): T => value?.data ?? value?.items ?? value ?? []

const loadDocuments = async () => {
  isLoading.value = true

  try {
    const apps = normalize<any[]>(await api.applications.list())
    appMap.value = new Map((apps || []).map((app: any) => [String(app.id), { id: String(app.id), name: app.name || 'Proyecto' }]))

    for (const app of apps || []) {
      const epics = normalize<any[]>(await api.epics.list(String(app.id)))
      for (const epic of epics || []) {
        epicMap.value.set(String(epic.id), { id: String(epic.id), applicationId: String(epic.applicationId || app.id), title: epic.title || 'Épica' })
      }
    }

    const docs = normalize<DocRow[]>(await api.documents.list())
    allDocuments.value = Array.isArray(docs) ? docs : []

    for (const doc of allDocuments.value) {
      const ticketId = String(doc.ticket_id ?? doc.ticketId ?? '')
      if (ticketId) {
        try {
          const ticket = normalize<any>(await api.tickets.getById(ticketId))
          const currentTicket = ticket?.data ?? ticket
          if (currentTicket?.id) {
            ticketMap.value.set(String(currentTicket.id), { id: String(currentTicket.id), epicId: currentTicket.epicId || currentTicket.epic_id || undefined })
          }
        } catch {
          // La vista sigue funcionando si el ticket no está disponible en el mapa
        }
      }
    }
  } catch (error) {
    console.error('Error cargando documentación del desarrollador:', error)
    allDocuments.value = []
  } finally {
    isLoading.value = false
  }
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
