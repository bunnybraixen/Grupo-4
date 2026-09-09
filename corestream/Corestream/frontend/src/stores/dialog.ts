import { defineStore } from 'pinia'
import { ref } from 'vue'

export type DialogType = 'alert' | 'confirm'

export interface DialogOptions {
  title?: string
  message: string
  type: DialogType
  confirmText?: string
  cancelText?: string
  resolve: (value: boolean) => void
}

export const useDialogStore = defineStore('dialog', () => {
  const isOpen = ref(false)
  const options = ref<DialogOptions | null>(null)

  const alert = (message: string, title = 'Atención'): Promise<void> => {
    return new Promise((resolve) => {
      options.value = { 
        message, 
        title, 
        type: 'alert', 
        resolve: () => resolve() 
      }
      isOpen.value = true
    })
  }

  const confirm = (message: string, title = 'Confirmar'): Promise<boolean> => {
    return new Promise((resolve) => {
      options.value = { 
        message, 
        title, 
        type: 'confirm', 
        resolve 
      }
      isOpen.value = true
    })
  }

  const close = (value: boolean = false) => {
    if (options.value) {
      options.value.resolve(value)
    }
    isOpen.value = false
    setTimeout(() => {
      options.value = null
    }, 300) // Wait for transition
  }

  return { isOpen, options, alert, confirm, close }
})
