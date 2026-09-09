<!--
  Vista 404 - Página no encontrada

  Se muestra cuando el usuario intenta acceder a una ruta que no existe.
-->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-900 dark:text-white mb-4">404</h1>
      <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
        Página no encontrada
      </p>
      <router-link
        to="/"
        class="inline-block px-6 py-3 bg-primary text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Volver al inicio
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Componente NotFoundView - Sin lógica adicional requerida
 */
</script>
