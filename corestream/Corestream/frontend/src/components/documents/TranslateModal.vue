<template>
  <Transition name="fade-modal">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="$emit('close')"
    >
      <div class="bg-slate-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 overflow-hidden">
        <!-- Header -->
        <div class="p-6 border-b border-slate-700">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-full bg-teal-900 bg-opacity-50 flex items-center justify-center flex-shrink-0">
              <span class="text-lg">🌐</span>
            </div>
            <div>
              <h2 class="text-lg font-bold text-white">{{ t('codeDocs.translate') }}</h2>
              <p class="text-sm text-slate-400 truncate max-w-xs">{{ document?.filename }}</p>
            </div>
          </div>
        </div>

        <!-- Controles de idioma -->
        <div class="p-6 space-y-4">
          <div class="flex items-center gap-3">
            <label class="text-sm font-medium text-slate-300 whitespace-nowrap">
              {{ t('codeDocs.translateTo') }}:
            </label>
            <select
              v-model="selectedLang"
              :disabled="isTranslating || isDownloading"
              class="flex-1 px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 disabled:opacity-50"
            >
              <option value="" disabled>{{ t('codeDocs.selectTargetLanguage') }}</option>
              <option v-for="(label, code) in SUPPORTED_LANGUAGES" :key="code" :value="code">
                {{ label }}
              </option>
            </select>

            <button
              @click="handleTranslate"
              :disabled="!selectedLang || isTranslating || isDownloading"
              class="px-4 py-2 bg-teal-600 hover:bg-teal-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
            >
              {{ isTranslating ? t('codeDocs.translating') : t('codeDocs.translate') }}
            </button>

            <button
              @click="handleDownload"
              :disabled="!selectedLang || isTranslating || isDownloading"
              class="px-4 py-2 bg-slate-600 hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors whitespace-nowrap"
              :title="t('codeDocs.translateDownloadHint')"
            >
              {{ isDownloading ? t('codeDocs.downloading') : '⬇ ' + t('codeDocs.download') }}
            </button>
          </div>

          <!-- Barra de progreso -->
          <div v-if="isTranslating || isDownloading" class="space-y-1.5">
            <div class="flex justify-between items-center text-xs">
              <span class="text-slate-300">{{ progressLabel }}</span>
              <span class="text-slate-500">{{ progressTimeLabel }}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
              <div
                class="h-1.5 rounded-full bg-teal-500 transition-all duration-500"
                :style="{ width: `${translationProgress}%` }"
              />
            </div>
          </div>

          <!-- Error: servicio no disponible (cargando modelos) -->
          <div v-if="serviceUnavailable" class="flex items-start gap-3 bg-amber-900 bg-opacity-30 border border-amber-700 px-4 py-3 rounded-lg">
            <span class="text-amber-400 text-lg shrink-0">⏳</span>
            <div class="flex-1">
              <p class="text-sm font-semibold text-amber-300">{{ t('codeDocs.serviceStarting') }}</p>
              <p class="text-xs text-amber-400 mt-1">
                {{ t('codeDocs.serviceStartingDesc') }}
              </p>
              <button
                @click="handleTranslate"
                :disabled="isTranslating"
                class="mt-2 px-3 py-1 text-xs bg-amber-700 hover:bg-amber-600 disabled:opacity-50 text-white rounded-lg transition-colors"
              >
                {{ isTranslating ? t('codeDocs.retrying') : t('codeDocs.retry') }}
              </button>
            </div>
          </div>

          <!-- Error genérico de traducción -->
          <p v-else-if="errorMessage" class="text-sm text-red-400 bg-red-900 bg-opacity-30 px-3 py-2 rounded-lg">
            {{ errorMessage }}
          </p>

          <!-- Error de descarga -->
          <p v-if="downloadError" class="text-sm text-red-400 bg-red-900 bg-opacity-30 px-3 py-2 rounded-lg">
            {{ downloadError }}
          </p>

          <!-- Resultado -->
          <div v-if="translatedText">
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-semibold text-slate-300">
                {{ t('codeDocs.translationResult') }}
              </label>
              <button
                @click="handleCopy"
                class="flex items-center gap-1.5 px-3 py-1 text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
              >
                <span>{{ copied ? '✓' : '📋' }}</span>
                {{ copied ? t('codeDocs.copied') : t('codeDocs.copyToClipboard') }}
              </button>
            </div>
            <pre class="w-full max-h-64 overflow-y-auto p-3 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-200 whitespace-pre-wrap break-words font-mono">{{ translatedText }}</pre>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t border-slate-700 flex justify-end">
          <button
            @click="$emit('close')"
            class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDocumentsStore } from '@/stores/documents'
import { api } from '@/services/api'
import { SUPPORTED_LANGUAGES } from '@/types'
import type { Document } from '@/types'

const { t } = useI18n()
const documentsStore = useDocumentsStore()

const props = defineProps<{
  isOpen: boolean
  document: Document | null
}>()

const emit = defineEmits<{
  close: []
}>()

const selectedLang = ref('')
const translatedText = ref('')
const isTranslating = ref(false)
const isDownloading = ref(false)
const errorMessage = ref('')
const downloadError = ref('')
const serviceUnavailable = ref(false)
const copied = ref(false)

// --- Progreso ---
const translationProgress = ref(0)
const estimatedSeconds = ref(30)
const elapsedSeconds = ref(0)
let progressInterval: ReturnType<typeof setInterval> | null = null

const progressLabel = computed(() => {
  const pct = translationProgress.value
  if (pct >= 95) return t('codeDocs.finalizing')
  if (isDownloading.value) return `${t('codeDocs.generatingFile')} ${pct}%`
  return `${t('codeDocs.translating')} ${pct}%`
})

const progressTimeLabel = computed(() => {
  if (translationProgress.value >= 95) return t('codeDocs.almostDone')
  const remaining = Math.max(1, estimatedSeconds.value - elapsedSeconds.value)
  if (remaining > 60) return `~${Math.ceil(remaining / 60)} ${t('codeDocs.minutesRemaining')}`
  return `~${remaining} ${t('codeDocs.secondsRemaining')}`
})

function startProgress(fileSize: number) {
  if (progressInterval) clearInterval(progressInterval)
  translationProgress.value = 0
  elapsedSeconds.value = 0

  // ~2 bytes/char UTF-8 promedio, 4000 chars/chunk, 8s/chunk (Azure Translator)
  const chunks = Math.max(1, Math.ceil(fileSize / 2 / 4000))
  estimatedSeconds.value = Math.max(15, chunks * 8)

  const startTime = Date.now()
  progressInterval = setInterval(() => {
    const elapsed = (Date.now() - startTime) / 1000
    elapsedSeconds.value = Math.floor(elapsed)
    // Asintótico: nunca supera 94% hasta que la operación completa realmente
    translationProgress.value = Math.min(94, Math.round((elapsed / estimatedSeconds.value) * 94))
  }, 500)
}

function stopProgress(completed: boolean) {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
  if (completed) {
    translationProgress.value = 100
    setTimeout(() => { translationProgress.value = 0 }, 800)
  } else {
    translationProgress.value = 0
  }
}

onUnmounted(() => {
  if (progressInterval) clearInterval(progressInterval)
})

// Reinicia estado al abrir el modal con un documento diferente
watch(() => props.document?.id, () => {
  if (progressInterval) { clearInterval(progressInterval); progressInterval = null }
  translationProgress.value = 0
  translatedText.value = ''
  errorMessage.value = ''
  downloadError.value = ''
  serviceUnavailable.value = false
  selectedLang.value = ''
  copied.value = false
})

async function handleTranslate() {
  if (!props.document || !selectedLang.value) return

  isTranslating.value = true
  errorMessage.value = ''
  downloadError.value = ''
  serviceUnavailable.value = false
  translatedText.value = ''

  startProgress(props.document.fileSize ?? 1024)

  try {
    const res = await documentsStore.translateDocument(props.document.id, selectedLang.value)
    translatedText.value = res.translatedText
    stopProgress(true)
  } catch (e: any) {
    stopProgress(false)
    const httpStatus = e?.response?.status
    if (httpStatus === 503) {
      serviceUnavailable.value = true
    } else {
      const detail = e?.response?.data?.detail ?? e?.message ?? 'Error al traducir'
      errorMessage.value = detail
    }
  } finally {
    isTranslating.value = false
  }
}

async function handleDownload() {
  if (!props.document || !selectedLang.value) return

  isDownloading.value = true
  downloadError.value = ''
  serviceUnavailable.value = false

  startProgress(props.document.fileSize ?? 1024)

  try {
    await api.documents.translateDownload(props.document.id, selectedLang.value)
    stopProgress(true)
  } catch (e: any) {
    stopProgress(false)
    if (e?.response?.status === 503) {
      serviceUnavailable.value = true
    } else {
      let msg = 'Error al generar la traducción. Intenta de nuevo.'
      try {
        const blob = e?.response?.data as Blob
        if (blob?.text) {
          const text = await blob.text()
          const parsed = JSON.parse(text)
          if (parsed.detail) msg = parsed.detail
        }
      } catch { /* ignorar errores de parseo del blob */ }
      downloadError.value = msg
    }
  } finally {
    isDownloading.value = false
  }
}

async function handleCopy() {
  if (!translatedText.value) return
  await navigator.clipboard.writeText(translatedText.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.fade-modal-enter-active,
.fade-modal-leave-active {
  transition: opacity 0.3s ease;
}

.fade-modal-enter-from,
.fade-modal-leave-to {
  opacity: 0;
}

.fade-modal-enter-active > div {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  transform: scale(1);
}

.fade-modal-enter-from > div {
  transform: scale(0.95);
}
</style>
