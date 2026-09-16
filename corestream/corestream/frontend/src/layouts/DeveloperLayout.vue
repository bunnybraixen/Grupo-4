<!--
  Layout para sección de desarrollo

  Proporciona navegación sidebar y estructura común para todas las vistas de desarrollo.
-->
<template>
  <div class="flex h-screen bg-gray-100 dark:bg-gray-950">
    <!-- Sidebar -->
    <aside class="w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">
      <nav class="p-6 space-y-4">
        <h2 class="font-bold text-lg text-gray-900 dark:text-white mb-6">
          Desarrollo
        </h2>
        
        <router-link
          to="/dev/workbench"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Workbench
        </router-link>
        
        <router-link
          to="/dev/uploads"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Mis Cargas
        </router-link>
        
        <!-- Solo visible para líderes de grupo -->
        <router-link
          to="/dev/team-assignment"
          class="block px-4 py-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          Asignación de Equipo
        </router-link>
      </nav>
    </aside>

    <!-- Contenido principal -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * DeveloperLayout - Componente de estructura para vistas de desarrollo
 */
</script>
