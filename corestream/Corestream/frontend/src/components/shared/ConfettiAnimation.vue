<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Animación de Confeti -->
  <!-- ================================================================ -->
  <!-- Usa canvas-confetti para animar explosión de confeti -->
  <!-- Se dispara cuando se completa un ticket -->
  <!-- Proporciona función fireConfetti() exportada via defineExpose -->
  <!-- ================================================================ -->
  <Teleport to="body">
    <!-- ================================================================ -->
    <!-- CANVAS: Elemento para animación -->
    <!-- ================================================================ -->
    <!-- Canvas donde se renderiza la animación de confeti -->
    <!-- ================================================================ -->
    <canvas
      ref="canvasRef"
      class="fixed inset-0 w-full h-full pointer-events-none"
      style="z-index: 99999;"
    />
  </Teleport>
</template>

<script setup lang="ts">
// =====================================================================
// IMPORTS Y COMPOSABLES
// =====================================================================

import { ref, onMounted, onBeforeUnmount } from 'vue'
import confetti from 'canvas-confetti'

// =====================================================================
// ESTADO LOCAL
// =====================================================================

// Referencia al elemento canvas
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Instancia de la función confetti configurada
let confettiInstance: any = null

// =====================================================================
// CICLO DE VIDA
// =====================================================================

/**
 * Al montar el componente, configura canvas-confetti
 * Obtiene la referencia del canvas para dibujar animación
 */
onMounted(() => {
  if (canvasRef.value) {
    // Configurar confetti con referencia al canvas
    confettiInstance = confetti.create(canvasRef.value, {
      // Resolver: permite usar canvas específico
      resize: true,
      // Usar canvas completo de la página
    })
  }
})

/**
 * Al desmontar el componente, limpia recursos
 * Asegura que no haya memory leaks
 */
onBeforeUnmount(() => {
  // Limpiar confetti si existe
  if (confettiInstance) {
    confettiInstance.reset()
  }
})

// =====================================================================
// MÉTODOS
// =====================================================================

/**
 * Dispara la animación de confeti
 * Crea explosión de confeti desde el centro de la pantalla
 * Configurado para celebración de completación de ticket
 */
const fireConfetti = () => {
  if (!confettiInstance) return

  // Configuración de la explosión
  const duration = 2500 // 2.5 segundos de animación
  const animationEnd = Date.now() + duration
  // Colores corporativos
  const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6']

  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      clearInterval(interval)
      return
    }

    const particleCount = 20 * (timeLeft / duration) // Va disminuyendo suavemente

    // Disparo Izquierdo
    confetti({
      particleCount,
      angle: 60,
      spread: 80,        // Más dispersión lateral
      origin: { x: 0, y: 1 },
      colors: colors,
      scalar: 1.4,       // ¡Papelitos 40% más grandes!
      zIndex: 99999      // Prioridad máxima
    })

    // Disparo Derecho
    confetti({
      particleCount,
      angle: 120,
      spread: 80,
      origin: { x: 1, y: 1 },
      colors: colors,
      scalar: 1.4,
      zIndex: 99999
    })
  }, 250)
}

// =====================================================================
// EXPORTS
// =====================================================================

/**
 * Exponer función fireConfetti para que componentes padre la usen
 * Permite disparar la animación desde otro componente
 */
defineExpose({
  fireConfetti
})
</script>

<style scoped>
/* ================================================================ */
/* ESTILOS */
/* ================================================================ */

/* El canvas se posiciona fixed sobre toda la pantalla */
/* pointer-events-none permite que otros elementos reciban clicks */

/* No se requieren estilos personalizados adicionales */
</style>
