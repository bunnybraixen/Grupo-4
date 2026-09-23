<script setup lang="ts">
const emit = defineEmits(['close', 'created'])
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-900">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Nuevo incidente</h3>
        <button class="text-slate-500" @click="emit('close')">Cerrar</button>
      </div>

      <p class="mb-4 text-sm text-slate-600 dark:text-slate-300">
        La creación de incidentes aún se maneja en la sección de desarrollo.
      </p>

      <button
        class="w-full rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white"
        @click="emit('created')"
      >Guardar</button>
    </div>
  </div>
</template>
