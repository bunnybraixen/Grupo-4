<template>
  <div class="file-upload-container">
    <!-- Área de drag & drop -->
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      :class="[
        'upload-area border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer',
        isDragging
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/10'
          : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900/50',
      ]"
      @click="fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        multiple
        @change="handleFileSelect"
        class="hidden"
        accept=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.cs,.rb,.go,.rs,.php,.swift,.kt,.scala,.md,.pdf,.docx,.txt,.rst,.doc,.json,.yaml,.yml,.xml,.sql,.csv,.toml,.env"
      />

      <svg
        class="w-12 h-12 mx-auto mb-4 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>

      <p class="text-gray-700 dark:text-gray-300 font-medium mb-2">
        Arrastra archivos aquí o haz clic para seleccionar
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        Máximo 25 MB por archivo · Código, documentación y datos
      </p>

      <button
        @click.stop="fileInput?.click()"
        type="button"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        Seleccionar Archivos
      </button>
    </div>

    <!-- Tipos de archivo permitidos -->
    <div class="mt-4 grid grid-cols-3 gap-3">
      <div class="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
        <h4 class="font-semibold text-blue-900 dark:text-blue-200 text-xs mb-1">Código</h4>
        <p class="text-xs text-blue-700 dark:text-blue-300">.py .js .ts .java .go .rs ...</p>
      </div>
      <div class="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">
        <h4 class="font-semibold text-green-900 dark:text-green-200 text-xs mb-1">Documentación</h4>
        <p class="text-xs text-green-700 dark:text-green-300">.md .pdf .docx .txt ...</p>
      </div>
      <div class="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg">
        <h4 class="font-semibold text-purple-900 dark:text-purple-200 text-xs mb-1">Datos</h4>
        <p class="text-xs text-purple-700 dark:text-purple-300">.json .yaml .sql .csv ...</p>
      </div>
    </div>

    <!-- Archivos en progreso -->
    <div v-if="uploadingFiles.length > 0" class="mt-6">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Subiendo...</h3>
      <div class="space-y-3">
        <div
          v-for="f in uploadingFiles"
          :key="f.id"
          class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ f.name }}</span>
            <span class="text-xs text-gray-500 dark:text-gray-400 ml-2 shrink-0">{{ formatFileSize(f.size) }}</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full transition-all" :style="{ width: f.progress + '%' }" />
          </div>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ f.progress }}%</p>
        </div>
      </div>
    </div>

    <!-- Lista de archivos cargados -->
    <div v-if="isLoading" class="mt-6 text-center py-8 text-gray-500 dark:text-gray-400 text-sm">
      Cargando archivos...
    </div>

    <div v-else-if="uploadedFiles.length > 0" class="mt-6">
      <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        Archivos ({{ uploadedFiles.length }})
      </h3>
      <div class="space-y-2">
        <div
          v-for="doc in uploadedFiles"
          :key="doc.id"
          class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 flex items-center gap-3"
        >
          <!-- Badge de tipo -->
          <div
            :class="['w-8 h-8 rounded flex items-center justify-center text-white text-xs font-bold shrink-0', getFileTypeColor(doc.filename)]"
          >
            {{ getFileExtDisplay(doc.filename) }}
          </div>

          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ doc.filename }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatFileSize(doc.file_size) }} · {{ formatDate(doc.created_at) }}
            </p>
          </div>

          <div class="flex gap-1 shrink-0">
            <button
              @click="downloadFile(doc)"
              type="button"
              class="p-1.5 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
              title="Descargar"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </button>
            <button
              @click="deleteFile(doc.id)"
              type="button"
              class="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
              title="Eliminar"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!isLoading && uploadedFiles.length === 0 && uploadingFiles.length === 0" class="mt-6 text-center py-6 text-gray-400 dark:text-gray-500 text-sm">
      No hay archivos aún. Sube el primero usando el área de arriba.
    </div>

    <!-- Mensajes de estado -->
    <transition name="fade">
      <div
        v-if="message"
        :class="[
          'mt-4 p-3 rounded-lg text-sm',
          message.type === 'success'
            ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-200'
            : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-200',
        ]"
      >
        {{ message.text }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { api } from '@/services/api'
import { useDialogStore } from '@/stores/dialog'

interface ApiDocument {
  id: string
  filename: string
  file_size: number
  mime_type: string
  doc_type: string
  epic_id?: string | null
  ticket_id?: string | null
  uploaded_by_id?: string | null
  created_at: string
}

const props = defineProps<{
  epicId?: string
  ticketId?: string
}>()

const emit = defineEmits<{
  uploaded: [doc: ApiDocument]
  deleted: [docId: string]
}>()

const dialogStore = useDialogStore()
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement>()
const uploadingFiles = ref<{ id: string; name: string; size: number; progress: number }[]>([])
const uploadedFiles = ref<ApiDocument[]>([])
const message = ref<{ type: 'success' | 'error'; text: string } | null>(null)
const isLoading = ref(false)

onMounted(async () => {
  await loadFiles()
})

watch([() => props.epicId, () => props.ticketId], async () => {
  await loadFiles()
})

const handleFileSelect = (event: Event) => {
  const files = (event.target as HTMLInputElement).files
  if (files) handleFiles(Array.from(files))
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) handleFiles(Array.from(files))
}

const handleFiles = async (files: File[]) => {
  for (const file of files) {
    await uploadFile(file)
  }
}

const getDocType = (filename: string): string => {
  const ext = (filename.split('.').pop() || '').toLowerCase()
  const codeExts = ['py','js','ts','jsx','tsx','java','cpp','c','cs','rb','go','rs','php','swift','kt','scala']
  return codeExts.includes(ext) ? 'CODE' : 'DOCUMENTATION'
}

const uploadFile = async (file: File) => {
  const uploadId = Math.random().toString(36).substring(2, 11)
  uploadingFiles.value.push({ id: uploadId, name: file.name, size: file.size, progress: 0 })

  try {
    const uploadItem = uploadingFiles.value.find((f) => f.id === uploadId)

    const result = await api.documents.upload(file, {
      epicId:   props.epicId,
      ticketId: props.ticketId,
      docType:  getDocType(file.name),
    })

    // Unwrap ApiResponse<Document> → ApiDocument (mismo patrón que loadFiles() abajo)
    const doc = ((result as any)?.data ?? result) as ApiDocument

    if (uploadItem) uploadItem.progress = 100
    uploadedFiles.value.unshift(doc)
    emit('uploaded', doc)
    showMessage('success', `"${file.name}" cargado exitosamente`)
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : `Error al cargar ${file.name}`
    showMessage('error', msg)
  } finally {
    uploadingFiles.value = uploadingFiles.value.filter((f) => f.id !== uploadId)
    if (fileInput.value) fileInput.value.value = ''
  }
}

const loadFiles = async () => {
  isLoading.value = true
  try {
    const filters: { epicId?: string; ticketId?: string } = {}
    if (props.epicId) filters.epicId = props.epicId
    if (props.ticketId) filters.ticketId = props.ticketId

    const res = await api.documents.list(filters)
    // Backend returns array directly; the store pattern handles both wrapped/unwrapped
    const docs = (res as unknown as { data?: ApiDocument[] })?.data ?? (res as unknown as ApiDocument[])
    uploadedFiles.value = Array.isArray(docs) ? docs : []
  } catch (error) {
    console.error('Error al cargar documentos:', error)
    uploadedFiles.value = []
  } finally {
    isLoading.value = false
  }
}

const downloadFile = async (doc: ApiDocument) => {
  try {
    await api.documents.download(doc.id)
  } catch {
    window.open(`/api/documents/${doc.id}/download`, '_blank')
  }
}

const deleteFile = async (docId: string) => {
  if (!(await dialogStore.confirm('¿Eliminar este archivo permanentemente?'))) return
  try {
    await api.documents.delete(docId)
    uploadedFiles.value = uploadedFiles.value.filter((f) => f.id !== docId)
    emit('deleted', docId)
    showMessage('success', 'Archivo eliminado exitosamente')
  } catch (error: unknown) {
    const msg = error instanceof Error ? error.message : 'Error al eliminar el archivo'
    showMessage('error', msg)
  }
}

const showMessage = (type: 'success' | 'error', text: string) => {
  message.value = { type, text }
  setTimeout(() => { message.value = null }, 5000)
}

const formatFileSize = (bytes: number): string => {
  if (!bytes || bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
}

const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getFileExtension = (filename: string): string => {
  const parts = filename.split('.')
  return parts.length > 1 ? `.${parts.pop()!.toLowerCase()}` : ''
}

const getFileTypeColor = (filename: string): string => {
  const ext = getFileExtension(filename)
  if (['.py','.js','.ts','.jsx','.tsx','.java','.cpp','.c','.cs','.rb','.go','.rs','.php','.swift','.kt','.scala'].includes(ext)) return 'bg-blue-600'
  if (['.md','.pdf','.docx','.txt','.rst','.doc'].includes(ext)) return 'bg-green-600'
  if (['.json','.yaml','.yml','.xml','.sql','.csv','.toml','.env'].includes(ext)) return 'bg-purple-600'
  return 'bg-gray-600'
}

const getFileExtDisplay = (filename: string): string => {
  const ext = getFileExtension(filename)
  return ext.substring(1).toUpperCase().slice(0, 2) || '??'
}
</script>

<style scoped>
.file-upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-area {
  transition: all 0.2s ease;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
