import { defineStore } from 'pinia'
import { api } from '@/services/api'
import type { Document, TranslateResponse } from '@/types'

export const useDocumentsStore = defineStore('documents', {
  state: () => ({
    documents: [] as Document[],
    isLoading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchDocuments(filters?: { ticketId?: string; epicId?: string }) {
      this.isLoading = true
      this.error = null
      try {
        const res = await api.documents.list(filters)
        this.documents = (res as any)?.data ?? (res as unknown as Document[])
      } catch (e: any) {
        this.error = e.message || 'Error al cargar documentos'
        console.error('Error fetchDocuments:', e)
      } finally {
        this.isLoading = false
      }
    },

    async deleteDocument(documentId: string) {
      try {
        await api.documents.delete(documentId)
        this.documents = this.documents.filter(d => d.id !== documentId)
      } catch (e) {
        console.error('Error deleteDocument:', e)
      }
    },

    async translateDocument(documentId: string, targetLanguage: string): Promise<TranslateResponse> {
      this.isLoading = true
      this.error = null
      try {
        const res = await api.documents.translate(documentId, targetLanguage)
        return ('data' in (res as object) ? (res as any).data : res) as TranslateResponse
      } catch (e: any) {
        this.error = e.message || 'Error al traducir documento'
        console.error('Error translateDocument:', e)
        throw e
      } finally {
        this.isLoading = false
      }
    },
  },

  getters: {
    codeDocuments: (state): Document[] =>
      state.documents.filter(d => (d.docType as string) === 'CODE'),

    docDocuments: (state): Document[] =>
      state.documents.filter(d => (d.docType as string) === 'DOCUMENTATION'),

    recentDocuments: (state): Document[] =>
      [...state.documents]
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, 5),

    uploaderIds: (state): string[] =>
      [...new Set(state.documents.map(d => d.uploadedById).filter(Boolean))],

    documentsByUploader: (state): Record<string, Document[]> =>
      state.documents.reduce((groups: Record<string, Document[]>, doc) => {
        const key = doc.uploadedById || 'unknown'
        if (!groups[key]) groups[key] = []
        groups[key].push(doc)
        return groups
      }, {}),

    uploaderNameById: (state): Record<string, string> =>
      state.documents.reduce((map: Record<string, string>, doc) => {
        if (doc.uploadedById && doc.uploadedBy && !map[doc.uploadedById]) {
          map[doc.uploadedById] = doc.uploadedBy.fullName || doc.uploadedBy.email
        }
        return map
      }, {}),
  },
})
