<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div 
        v-if="dialogStore.isOpen" 
        class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
        @mousedown="handleBackdropClick"
      >
        <div 
          class="bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all"
          @mousedown.stop
        >
          <!-- Encabezado con Ícono y Título -->
          <div class="p-6 pb-4 flex items-center gap-4">
            <div 
              class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
              :class="iconBgColor"
            >
              <span class="text-2xl">{{ iconEmoji }}</span>
            </div>
            <div>
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">
                {{ dialogStore.options?.title }}
              </h2>
            </div>
          </div>

          <!-- Mensaje -->
          <div class="px-6 py-2">
            <p class="text-slate-600 dark:text-gray-300 text-[15px] leading-relaxed whitespace-pre-line">
              {{ dialogStore.options?.message }}
            </p>
          </div>

          <!-- Acciones -->
          <div class="px-6 py-5 mt-4 flex gap-3 justify-end bg-slate-50 dark:bg-gray-950/50 border-t border-slate-100 dark:border-gray-800/50">
            <!-- Botón Cancelar (solo si es Confirm) -->
            <button
              v-if="dialogStore.options?.type === 'confirm'"
              @click="cancel"
              class="px-5 py-2.5 rounded-xl font-medium border border-slate-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-slate-700 dark:text-gray-300 hover:bg-slate-50 dark:hover:bg-gray-700 transition-colors"
            >
              {{ dialogStore.options?.cancelText || 'Cancelar' }}
            </button>
            
            <!-- Botón Confirmar/Aceptar -->
            <button
              @click="confirm"
              class="px-5 py-2.5 rounded-xl font-bold text-white shadow-lg transition-colors flex items-center justify-center min-w-[100px]"
              :class="confirmBtnColor"
            >
              {{ dialogStore.options?.confirmText || (dialogStore.options?.type === 'alert' ? 'Aceptar' : 'Confirmar') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useDialogStore } from '@/stores/dialog'

const dialogStore = useDialogStore()

// Computed classes para estilos según el tipo (alerta vs confirmar vs borrar)
const isDanger = computed(() => {
  const msg = dialogStore.options?.message.toLowerCase() || ''
  const title = dialogStore.options?.title?.toLowerCase() || ''
  return msg.includes('eliminar') || title.includes('eliminar') || msg.includes('delete') || msg.includes('permanente')
})

const iconEmoji = computed(() => {
  if (isDanger.value) return '⚠️'
  if (dialogStore.options?.type === 'alert') return 'ℹ️'
  return '❓'
})

const iconBgColor = computed(() => {
  if (isDanger.value) return 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
  if (dialogStore.options?.type === 'alert') return 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
  return 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
})

const confirmBtnColor = computed(() => {
  if (isDanger.value) return 'bg-red-500 hover:bg-red-600'
  if (dialogStore.options?.type === 'alert') return 'bg-blue-500 hover:bg-blue-600'
  return 'bg-[var(--teal)] hover:bg-[var(--teal)] opacity-90 hover:opacity-100'
})

const confirm = () => {
  dialogStore.close(true)
}

const cancel = () => {
  dialogStore.close(false)
}

const handleBackdropClick = () => {
  // Solo permitir cerrar haciendo clic afuera si es una alerta
  // Si es confirmación, obligar a presionar un botón
  if (dialogStore.options?.type === 'alert') {
    cancel()
  } else {
    // Pequeño efecto visual o sonido si se quisiera
  }
}
</script>

<style scoped>
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-from .bg-white,
.dialog-fade-leave-to .bg-white,
.dialog-fade-enter-from .dark\:bg-gray-900,
.dialog-fade-leave-to .dark\:bg-gray-900 {
  transform: scale(0.95) translateY(10px);
}
</style>
