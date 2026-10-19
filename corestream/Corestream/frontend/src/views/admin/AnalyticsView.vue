<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      Analítica Global
    </h1>
    <p class="mt-2 mb-6 text-gray-600 dark:text-gray-400">
      Métricas de proyecto y rendimiento del equipo
    </p>
    <MetricCards />
  </div>
</template>

<script setup lang="ts">
import MetricCards from '@/components/analytics/MetricCards.vue'
</script>