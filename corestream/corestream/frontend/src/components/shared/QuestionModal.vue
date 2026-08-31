<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Modal para Levantar Pregunta -->
  <!-- ================================================================ -->
  <!-- Modal overlay para ingresar texto de pregunta que bloquea ticket -->
  <!-- Muestra: ícono de alerta, título, descripción, textarea, botones -->
  <!-- Validación: mínimo 10 caracteres para confirmar -->
  <!-- ================================================================ -->

  <Transition name="fade-modal">
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
    >
      <!-- ================================================================ -->
      <!-- CONTENEDOR: Modal -->
      <!-- ================================================================ -->
      <div class="bg-slate-800 rounded-lg shadow-2xl max-w-md w-full mx-4 overflow-hidden">
        <!-- ================================================================ -->
        <!-- SECCIÓN: Encabezado con Ícono -->
        <!-- ================================================================ -->
        <div class="p-6 space-y-2 bg-slate-750 border-b border-slate-700">
          <!-- Ícono de advertencia -->
          <div class="flex items-center gap-3 mb-3">
            <div class="w-10 h-10 rounded-full bg-amber-900 bg-opacity-50 flex items-center justify-center flex-shrink-0">
              <Icon icon="mdi:alert-circle" class="text-amber-400 text-lg" />
            </div>
          </div>

          <!-- Título -->
          <h2 class="text-lg font-bold text-white">
            Levantar Pregunta
          </h2>

          <!-- Subtítulo / Descripción -->
          <p class="text-sm text-slate-400">
            El ticket será bloqueado hasta que se resuelva la duda
          </p>
        </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Contenido Principal -->
        <!-- ================================================================ -->
        <div class="p-6 space-y-4">
          <!-- Información del ticket -->
          <div class="p-3 bg-slate-900 rounded-lg border border-slate-700">
            <p class="text-xs text-slate-400 mb-1">Ticket</p>
            <p class="text-sm font-medium text-white truncate">
              {{ ticketTitle }}
            </p>
          </div>

          <!-- Textarea para pregunta -->
          <div>
            <label class="block text-sm font-semibold text-white mb-2">
              Tu Pregunta
            </label>
            <textarea
              v-model="questionText"
              placeholder="Describe la duda que tienes..."
              maxlength="500"
              rows="4"
              class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 resize-none"
            />

            <!-- Contador de caracteres -->
            <div class="flex justify-between mt-2">
              <span class="text-xs text-slate-400">
                Mínimo 10 caracteres para continuar
              </span>
              <span :class="[
                'text-xs font-medium',
                questionText.length >= 10
                  ? 'text-green-400'
                  : 'text-slate-400'
              ]">
                {{ questionText.length }}/500
              </span>
            </div>
          </div>
        </div>

        <!-- ================================================================ -->
        <!-- SECCIÓN: Footer con Botones -->
        <!-- ================================================================ -->
        <div class="p-4 bg-slate-750 border-t border-slate-700 flex gap-2">
          <!-- Botón cancelar -->
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-colors"
          >
            Cancelar
          </button>

          <!-- Botón enviar -->
          <button
            @click="handleSubmit"
            :disabled="questionText.trim().length < 10"
            :class="[
              'flex-1 px-4 py-2 font-semibold rounded-lg transition-colors',
              questionText.trim().length >= 10
                ? 'bg-amber-600 hover:bg-amber-700 text-white'
                : 'bg-amber-600 opacity-50 cursor-not-allowed text-white'
            ]"
          >
            Levantar Pregunta
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref } from 'vue'
import { Icon } from '@iconify/vue'

// =====================================================================
// PROPS
// =====================================================================

interface Props {
  isOpen: boolean
  ticketTitle: string
}

const props = defineProps<Props>()

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Texto de la pregunta siendo ingresada
const questionText = ref('')

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Maneja el envío de la pregunta
 * Valida que tenga al menos 10 caracteres
 * Emite evento con texto de pregunta
 */
const handleSubmit = () => {
  // Validación: mínimo 10 caracteres
  if (questionText.value.trim().length < 10) {
    return
  }

  // Emitir evento con pregunta
  emit('submit', questionText.value)

  // Limpiar estado
  questionText.value = ''
}

// =====================================================================
// EMITS
// =====================================================================

/**
 * Eventos emitidos por el componente QuestionModal
 */
const emit = defineEmits<{
  close: []
  submit: [questionText: string]
}>()
</script>

<style scoped>
/* ================================================================ */
/* TRANSICIONES */
/* ================================================================ */

/* Transición de fade para el modal */
.fade-modal-enter-active,
.fade-modal-leave-active {
  transition: opacity 0.3s ease;
}

.fade-modal-enter-from,
.fade-modal-leave-to {
  opacity: 0;
}

/* Escala del modal durante transición */
.fade-modal-enter-active {
  & > div {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    transform: scale(1);
  }
}

.fade-modal-enter-from > div {
  transform: scale(0.95);
}
</style>
