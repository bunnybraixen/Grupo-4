<!--
  Vista de Documentación de Código (Admin)

  Gestiona especificaciones técnicas, documentación de código y archivos asociados.
-->
<template>
  <div class="flex flex-col min-h-screen bg-[var(--bg-app)]">
    <AppHeader />
  <div class="flex-1 overflow-auto p-8 bg-[var(--bg-panel)]">
    <div class="mb-6">
      <h1 class="text-3xl font-bold mb-2 text-[var(--text-primary)]">{{ t('codeDocs.repositoryTitle') }}</h1>
      <p class="text-sm text-[var(--text-secondary)]">{{ t('codeDocs.repositorySubtitle') }}</p>
    </div>

    <!-- Loading state -->
    <div v-if="documentsStore.isLoading" class="flex items-center justify-center py-20 text-[var(--text-secondary)]">
      <span class="text-lg">{{ t('codeDocs.loadingDocs') }}</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="documentsStore.documents.length === 0" class="flex items-center justify-center py-20">
      <div class="text-center text-[var(--text-secondary)]">
        <span class="text-5xl mb-4 block">📂</span>
        <p class="text-lg font-medium">{{ t('codeDocs.noDocsYet') }}</p>
        <p class="text-sm mt-1">{{ t('codeDocs.noDocsDesc') }}</p>
      </div>
    </div>

    <template v-else>
      <div class="flex gap-4 mb-8">
        <button
          @click="detailView = 'codeFiles'"
          class="flex-1 rounded-xl p-5 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer text-left"
          :class="detailView === 'codeFiles' ? 'border-[var(--border-color)] ring-2 ring-[var(--border-subtle)] bg-[var(--bg-panel)]' : 'border-[var(--border-color)] bg-[var(--bg-card)] hover:border-[var(--text-muted)]'"
        >
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 bg-[var(--bg-panel)] rounded-xl flex items-center justify-center">
              <span class="text-2xl">💻</span>
            </div>
            <div class="flex-1">
              <p class="text-3xl font-bold text-[var(--text-primary)]">{{ documentsStore.codeDocuments.length }}</p>
              <p class="text-sm text-[var(--text-secondary)] mt-1">{{ t('codeDocs.codeFiles') }}</p>
            </div>
            <span class="text-xs text-blue-500 font-medium">{{ t('codeDocs.details') }}</span>
          </div>
        </button>

        <button
          @click="detailView = 'documentation'"
          class="flex-1 rounded-xl p-5 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer text-left"
          :class="detailView === 'documentation' ? 'border-indigo-500 ring-2 ring-indigo-200 bg-indigo-50' : 'border-[var(--border-color)] bg-[var(--bg-card)] hover:border-indigo-300'"
        >
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center">
              <span class="text-2xl">📚</span>
            </div>
            <div class="flex-1">
              <p class="text-3xl font-bold text-indigo-600">{{ documentsStore.docDocuments.length }}</p>
              <p class="text-sm text-[var(--text-secondary)] mt-1">{{ t('codeDocs.documentation') }}</p>
            </div>
            <span class="text-xs text-indigo-500 font-medium">{{ t('codeDocs.details') }}</span>
          </div>
        </button>

        <button
          @click="detailView = 'contributors'"
          class="flex-1 rounded-xl p-5 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer text-left"
          :class="detailView === 'contributors' ? 'border-emerald-500 ring-2 ring-emerald-200 bg-emerald-50' : 'border-[var(--border-color)] bg-[var(--bg-card)] hover:border-emerald-300'"
        >
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 bg-emerald-100 rounded-xl flex items-center justify-center">
              <span class="text-2xl">👥</span>
            </div>
            <div class="flex-1">
              <p class="text-3xl font-bold text-emerald-600">{{ documentsStore.uploaderIds.length }}</p>
              <p class="text-sm text-[var(--text-secondary)] mt-1">{{ t('codeDocs.contributors') }}</p>
            </div>
            <span class="text-xs text-emerald-500 font-medium">{{ t('codeDocs.details') }}</span>
          </div>
        </button>

        <button
          @click="detailView = 'byContext'"
          class="flex-1 rounded-xl p-5 shadow-sm border-2 transition-all hover:shadow-md cursor-pointer text-left"
          :class="detailView === 'byContext' ? 'border-violet-500 ring-2 ring-violet-200 bg-violet-50' : 'border-[var(--border-color)] bg-[var(--bg-card)] hover:border-violet-300'"
        >
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 bg-violet-100 rounded-xl flex items-center justify-center">
              <span class="text-2xl">🗂️</span>
            </div>
            <div class="flex-1">
              <p class="text-3xl font-bold text-violet-600">{{ contextCount }}</p>
              <p class="text-sm text-[var(--text-secondary)] mt-1">{{ t('codeDocs.epicsTickets') }}</p>
            </div>
            <span class="text-xs text-violet-500 font-medium">{{ t('codeDocs.details') }}</span>
          </div>
        </button>
      </div>

      <div class="bg-[var(--bg-card)] rounded-xl shadow-sm border border-[var(--border-color)] mb-6">
        <div class="p-5 border-b border-[var(--border-color)]">
          <h3 class="text-lg font-semibold text-[var(--text-primary)]">{{ t('codeDocs.recentFiles') }}</h3>
        </div>
        <div class="divide-y divide-[var(--border-subtle)]">
          <div
            v-for="doc in documentsStore.recentDocuments"
            :key="doc.id"
            class="flex items-center gap-4 p-5 hover:bg-[var(--bg-panel)] transition-colors"
          >
            <div
              class="w-12 h-12 rounded-lg flex items-center justify-center shrink-0"
              :class="isCodeFile(doc.docType) ? 'bg-[var(--bg-panel)]' : 'bg-indigo-100'"
            >
              <span class="text-xl">{{ isCodeFile(doc.docType) ? '💻' : '📚' }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold truncate text-[var(--text-primary)]">{{ doc.filename }}</p>
              <p class="text-xs text-[var(--text-secondary)] mt-1">{{ formatDate(doc.createdAt) }}</p>
            </div>
            <span class="text-sm text-[var(--text-secondary)] shrink-0">{{ formatFileSize(doc.fileSize) }}</span>
            <span class="px-3 py-1 text-xs font-medium rounded-full bg-[var(--bg-panel)] text-[var(--text-primary)] shrink-0">
              {{ getDocTypeLabel(doc.docType) }}
            </span>
            <div class="flex gap-2 shrink-0">
              <button
                @click.stop="downloadDocument(doc)"
                class="px-3 py-1.5 text-xs bg-[var(--bg-panel)] hover:bg-[var(--border-subtle)] text-[var(--text-primary)] rounded-lg border border-[var(--border-color)] transition-colors whitespace-nowrap"
              >
                ⬇ {{ t('codeDocs.download') }}
              </button>
              <button
                @click.stop="documentToTranslate = doc; translateModalOpen = true"
                class="px-3 py-1.5 text-xs bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg border border-teal-200 transition-colors whitespace-nowrap"
              >
                🌐 {{ t('codeDocs.translate') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <transition
        enter-active-class="transition ease-out duration-300 transform"
        enter-from-class="translate-x-full"
        enter-to-class="translate-x-0"
        leave-active-class="transition ease-in duration-200 transform"
        leave-from-class="translate-x-0"
        leave-to-class="translate-x-full"
      >
        <div v-if="detailView" class="fixed inset-y-0 right-0 z-50 w-full max-w-2xl bg-[var(--bg-card)] shadow-2xl border-l border-[var(--border-color)] flex flex-col">

          <div class="p-6 border-b border-[var(--border-color)] flex justify-between items-center bg-[var(--bg-panel)]">
            <div class="flex items-center gap-4">
              <div
                class="w-14 h-14 rounded-xl flex items-center justify-center"
                :class="{
                  'bg-[var(--bg-panel)]': detailView === 'codeFiles',
                  'bg-indigo-100':        detailView === 'documentation',
                  'bg-emerald-100':       detailView === 'contributors',
                  'bg-violet-100':        detailView === 'byContext',
                }"
              >
                <span class="text-2xl">{{
                  detailView === 'codeFiles' ? '💻'
                  : detailView === 'documentation' ? '📚'
                  : detailView === 'contributors' ? '👥'
                  : '🗂️'
                }}</span>
              </div>
              <div>
                <h2 class="text-2xl font-bold text-[var(--text-primary)]">{{
                  detailView === 'codeFiles' ? t('codeDocs.codeFiles')
                  : detailView === 'documentation' ? t('codeDocs.documentation')
                  : detailView === 'contributors' ? t('codeDocs.contributors')
                  : t('codeDocs.byEpicTicket')
                }}</h2>
                <p class="text-sm text-[var(--text-secondary)] mt-1">{{
                  documentsStore.documents.length === 1
                    ? t('codeDocs.fileSingularTotal', { n: 1 })
                    : t('codeDocs.filesTotal', { n: documentsStore.documents.length })
                }}</p>
              </div>
            </div>
            <button @click="detailView = null" class="p-3 hover:bg-[var(--border-color)] rounded-xl text-[var(--text-secondary)] hover:text-red-500 transition-colors">
              <span class="text-xl">✕</span>
            </button>
          </div>

          <div class="p-6 flex-1 overflow-y-auto">

            <div v-if="detailView === 'codeFiles'" class="space-y-4">
              <div
                v-for="doc in documentsStore.codeDocuments"
                :key="doc.id"
                class="p-5 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] hover:border-blue-300 transition-colors"
              >
                <div class="flex items-start gap-4">
                  <div class="w-12 h-12 rounded-lg flex items-center justify-center bg-[var(--bg-panel)]">
                    <span class="text-xl">📄</span>
                  </div>
                  <div class="flex-1">
                    <p class="text-base font-semibold text-[var(--text-primary)]">{{ doc.filename }}</p>
                    <div class="flex items-center gap-3 text-xs text-[var(--text-secondary)] mt-2">
                      <span>📅 {{ formatDate(doc.createdAt) }}</span><span>•</span>
                      <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded font-medium">{{ getDocTypeLabel(doc.docType) }}</span><span>•</span>
                      <span>💾 {{ formatFileSize(doc.fileSize) }}</span>
                    </div>
                  </div>
                  <span class="px-3 py-1 text-xs font-semibold rounded-full bg-[var(--bg-panel)] text-[var(--text-primary)]">
                    {{ doc.mimeType.split('/')[1]?.toUpperCase() || doc.mimeType }}
                  </span>
                  <div class="flex gap-2 shrink-0">
                    <button
                      @click="downloadDocument(doc)"
                      class="px-3 py-1.5 text-xs bg-[var(--bg-panel)] hover:bg-[var(--border-subtle)] text-[var(--text-primary)] rounded-lg border border-[var(--border-color)] transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      ⬇ {{ t('codeDocs.download') }}
                    </button>
                    <button
                      @click="documentToTranslate = doc; translateModalOpen = true"
                      class="px-3 py-1.5 text-xs bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg border border-teal-200 transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      🌐 {{ t('codeDocs.translate') }}
                    </button>
                  </div>
                </div>
              </div>
              <p v-if="documentsStore.codeDocuments.length === 0" class="text-center text-[var(--text-muted)] py-8">
                {{ t('codeDocs.noCodeFiles') }}
              </p>
            </div>

            <div v-if="detailView === 'documentation'" class="space-y-4">
              <div
                v-for="doc in documentsStore.docDocuments"
                :key="doc.id"
                class="p-5 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] hover:border-indigo-300 transition-colors"
              >
                <div class="flex items-start gap-4">
                  <div class="w-12 h-12 rounded-lg flex items-center justify-center bg-indigo-100">
                    <span class="text-xl">📄</span>
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-3">
                      <p class="text-base font-semibold text-[var(--text-primary)]">{{ doc.filename }}</p>
                      <span class="px-2 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-700">{{ getDocTypeLabel(doc.docType) }}</span>
                    </div>
                    <div class="flex items-center gap-3 text-xs text-[var(--text-secondary)] mt-2">
                      <span>📅 {{ formatDate(doc.createdAt) }}</span><span>•</span>
                      <span>💾 {{ formatFileSize(doc.fileSize) }}</span>
                    </div>
                  </div>
                  <div class="flex gap-2 shrink-0">
                    <button
                      @click="downloadDocument(doc)"
                      class="px-3 py-1.5 text-xs bg-[var(--bg-panel)] hover:bg-[var(--border-subtle)] text-[var(--text-primary)] rounded-lg border border-[var(--border-color)] transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      ⬇ {{ t('codeDocs.download') }}
                    </button>
                    <button
                      @click="documentToTranslate = doc; translateModalOpen = true"
                      class="px-3 py-1.5 text-xs bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg border border-teal-200 transition-colors flex items-center gap-1 whitespace-nowrap"
                    >
                      🌐 {{ t('codeDocs.translate') }}
                    </button>
                  </div>
                </div>
              </div>
              <p v-if="documentsStore.docDocuments.length === 0" class="text-center text-[var(--text-muted)] py-8">
                {{ t('codeDocs.noDocFiles') }}
              </p>
            </div>

            <!-- Panel: Por Épica / Ticket -->
            <div v-if="detailView === 'byContext'" class="space-y-6">
              <p v-if="documentsByContext.length === 0" class="text-center text-[var(--text-muted)] py-8">
                {{ t('codeDocs.noDocsYet') }}
              </p>
              <div v-for="group in documentsByContext" :key="group.label">
                <!-- Encabezado de grupo -->
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-base">{{ group.type === 'epic' ? '🟣' : group.type === 'ticket' ? '🎫' : '⚪' }}</span>
                  <h4 class="text-sm font-bold text-[var(--text-primary)]">{{ group.label }}</h4>
                  <span class="ml-auto text-xs text-[var(--text-muted)]">
                    {{ t(group.docs.length !== 1 ? 'codeDocs.filesPlural' : 'codeDocs.fileSingular', { n: group.docs.length }) }}
                  </span>
                </div>
                <div class="space-y-3 pl-6 border-l-2"
                  :class="group.type === 'epic' ? 'border-violet-200' : group.type === 'ticket' ? 'border-blue-200' : 'border-[var(--border-subtle)]'"
                >
                  <div
                    v-for="doc in group.docs"
                    :key="doc.id"
                    class="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] hover:border-violet-200 transition-colors"
                  >
                    <div class="flex items-center gap-3">
                      <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                        :class="isCodeFile(doc.docType) ? 'bg-[var(--bg-panel)]' : 'bg-indigo-100'"
                      >
                        <span class="text-sm">{{ isCodeFile(doc.docType) ? '💻' : '📄' }}</span>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold text-[var(--text-primary)] truncate">{{ doc.filename }}</p>
                        <div class="flex items-center gap-2 text-xs text-[var(--text-secondary)] mt-0.5">
                          <span class="px-1.5 py-0.5 rounded bg-[var(--bg-panel)] text-[var(--text-secondary)]">{{ getDocTypeLabel(doc.docType) }}</span>
                          <span>{{ formatFileSize(doc.fileSize) }}</span>
                          <span>{{ formatDate(doc.createdAt) }}</span>
                        </div>
                      </div>
                      <div class="flex gap-2 shrink-0">
                        <button
                          @click="downloadDocument(doc)"
                          class="px-3 py-1.5 text-xs bg-[var(--bg-panel)] hover:bg-[var(--border-subtle)] text-[var(--text-primary)] rounded-lg border border-[var(--border-color)] transition-colors flex items-center gap-1 whitespace-nowrap"
                        >
                          ⬇ {{ t('codeDocs.download') }}
                        </button>
                        <button
                          @click="documentToTranslate = doc; translateModalOpen = true"
                          class="px-3 py-1.5 text-xs bg-teal-50 hover:bg-teal-100 text-teal-700 rounded-lg border border-teal-200 transition-colors flex items-center gap-1 whitespace-nowrap"
                        >
                          🌐 {{ t('codeDocs.translate') }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="detailView === 'contributors'" class="space-y-5">
              <div
                v-for="(docs, uploaderId) in documentsStore.documentsByUploader"
                :key="uploaderId"
                class="p-6 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)]"
              >
                <div class="flex items-start gap-5">
                  <div class="w-16 h-16 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center text-white text-xl font-bold shadow-md">
                    {{ (documentsStore.uploaderNameById[String(uploaderId)] || String(uploaderId)).slice(0, 2).toUpperCase() }}
                  </div>
                  <div class="flex-1">
                    <h3 class="text-base font-bold text-[var(--text-primary)]">{{ documentsStore.uploaderNameById[String(uploaderId)] || `${t('codeDocs.userPrefix')} ${String(uploaderId).slice(0, 8)}…` }}</h3>
                    <p class="text-sm text-[var(--text-secondary)] mt-1">ID: {{ uploaderId }}</p>

                    <div class="grid grid-cols-3 gap-4 mt-5">
                      <div class="bg-[var(--bg-panel)] p-3 rounded-xl text-center border border-[var(--border-subtle)]">
                        <p class="text-xl font-bold text-[var(--text-primary)]">💻 {{ docs.filter(d => isCodeFile(d.docType)).length }}</p>
                        <p class="text-xs font-semibold text-[var(--text-secondary)] mt-1">{{ t('codeDocs.codeLabel') }}</p>
                      </div>
                      <div class="bg-indigo-50 p-3 rounded-xl text-center border border-indigo-100">
                        <p class="text-xl font-bold text-indigo-600">📚 {{ docs.filter(d => !isCodeFile(d.docType)).length }}</p>
                        <p class="text-xs font-semibold text-indigo-500 mt-1">{{ t('codeDocs.docsLabel') }}</p>
                      </div>
                      <div class="bg-emerald-50 p-3 rounded-xl text-center border border-emerald-100">
                        <p class="text-xl font-bold text-emerald-600">{{ formatFileSize(docs.reduce((sum, d) => sum + d.fileSize, 0)) }}</p>
                        <p class="text-xs font-semibold text-emerald-500 mt-1">{{ t('codeDocs.uploadedLabel') }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </transition>

      <div v-if="detailView" @click="detailView = null" class="fixed inset-0 bg-black/40 z-40 transition-opacity cursor-pointer backdrop-blur-sm"></div>
    </template>

  </div>

  <!-- Modal fuera del contenedor overflow-auto para evitar stacking context que bloquea position:fixed -->
  <TranslateModal
    :is-open="translateModalOpen"
    :document="documentToTranslate"
    @close="translateModalOpen = false"
  />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDocumentsStore } from '@/stores/documents'
import type { Document } from '@/types'
import AppHeader from '@/components/layout/AppHeader.vue'
import { api } from '@/services/api'

const TranslateModal = defineAsyncComponent(() =>
  import('@/components/documents/TranslateModal.vue')
)

const { t } = useI18n()
const documentsStore = useDocumentsStore()
const detailView = ref<'codeFiles' | 'documentation' | 'contributors' | 'byContext' | null>(null)
const translateModalOpen = ref(false)
const documentToTranslate = ref<Document | null>(null)
const epicTitleMap = ref<Record<string, string>>({})

const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && detailView.value) detailView.value = null
}

onMounted(async () => {
  window.addEventListener('keydown', handleEscape)
  await documentsStore.fetchDocuments()
  loadEpicTitles()
})

async function loadEpicTitles() {
  try {
    const apps = await api.applications.list()
    const appList = Array.isArray(apps) ? apps : (apps as any)?.data ?? []
    for (const app of appList) {
      try {
        const epics = await api.epics.list(app.id)
        const epicList = Array.isArray(epics) ? epics : (epics as any)?.data ?? []
        for (const epic of epicList) {
          epicTitleMap.value[epic.id] = epic.title
        }
      } catch { /* continuar si falla una app */ }
    }
  } catch { /* silencioso, solo afecta los labels del panel */ }
}

const documentsByContext = computed(() => {
  const groups: Record<string, { label: string; type: 'epic' | 'ticket' | 'none'; docs: Document[] }> = {}
  for (const doc of documentsStore.documents) {
    let key: string
    let label: string
    let type: 'epic' | 'ticket' | 'none'
    if (doc.epicId) {
      key = `epic:${doc.epicId}`
      label = epicTitleMap.value[doc.epicId] ?? `${t('codeDocs.epicPrefix')} ${doc.epicId.slice(0, 8)}…`
      type = 'epic'
    } else if (doc.ticketId) {
      key = `ticket:${doc.ticketId}`
      label = `${t('codeDocs.ticketPrefix')} ${doc.ticketId.slice(0, 8)}…`
      type = 'ticket'
    } else {
      key = 'none'
      label = t('codeDocs.noContext')
      type = 'none'
    }
    if (!groups[key]) groups[key] = { label, type, docs: [] }
    groups[key].docs.push(doc)
  }
  return Object.values(groups).sort((a, b) => {
    if (a.type === 'none') return 1
    if (b.type === 'none') return -1
    return a.label.localeCompare(b.label)
  })
})

const contextCount = computed(() =>
  documentsByContext.value.filter(g => g.type !== 'none').length
)

async function downloadDocument(doc: Document) {
  try {
    await api.documents.download(doc.id)
  } catch {
    window.open(`/api/documents/${doc.id}/download`, '_blank')
  }
}

onUnmounted(() => window.removeEventListener('keydown', handleEscape))

function isCodeFile(docType: string): boolean {
  return docType === 'CODE'
}

function getDocTypeLabel(docType: string): string {
  if (docType === 'CODE') return t('codeDocs.docTypeCode')
  if (docType === 'DOCUMENTATION') return t('codeDocs.docTypeDocumentation')
  return docType
}

function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' })
}
</script>
