<template>
  <!-- ================================================================ -->
  <!-- COMPONENTE: Animación de Confeti -->
  <!-- ================================================================ -->
  <!-- Usa canvas-confetti para animar explosión de confeti -->
  <!-- Se dispara cuando se completa un ticket -->
  <!-- Proporciona función fireConfetti() exportada via defineExpose -->
  <!-- ================================================================ -->

  <div>
    <!-- ================================================================ -->
    <!-- CANVAS: Elemento para animación -->
    <!-- ================================================================ -->
    <!-- Canvas donde se renderiza la animación de confeti -->
    <!-- ================================================================ -->
    <canvas
      ref="canvasRef"
      class="fixed inset-0 pointer-events-none"
    />
  </div>
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

  // Función para generar confeti recursivamente
  const randomInRange = (min: number, max: number): number => {
    return Math.random() * (max - min) + min
  }

  // Lanzar confeti desde múltiples puntos
  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      clearInterval(interval)
      return
    }

    // Disparar confeti desde el centro hacia arriba
    confettiInstance({
      // Particulas desde el centro
      particleCount: 100,
      // Ángulo de dispersión: arriba
      angle: 90,
      // Spread en grados
      spread: 45,
      // Origen: centro de la pantalla
      origin: {
        x: 0.5,
        y: 0.5
      },
      // Velocidad de las partículas
      velocity: randomInRange(25, 45),
      // Colores de confeti
      colors: [
        '#10b981', // Verde (para éxito)
        '#3b82f6', // Azul
        '#f59e0b', // Ámbar
        '#ec4899', // Rosa
        '#8b5cf6'  // Púrpura
      ],
      // Duración de caída
      decay: randomInRange(0.9, 0.95),
      // Rotación
      gravity: 1,
      // Escala de las partículas
      scalar: randomInRange(0.5, 1)
    })

    // También lanzar desde los lados para más efecto
    confettiInstance({
      particleCount: 50,
      angle: randomInRange(0, 360),
      spread: 360,
      origin: {
        x: Math.random(),
        y: Math.random() * 0.5
      },
      velocity: randomInRange(15, 35),
      colors: [
        '#10b981',
        '#3b82f6',
        '#f59e0b',
        '#ec4899',
        '#8b5cf6'
      ],
      decay: randomInRange(0.85, 0.95),
      gravity: 1,
      scalar: randomInRange(0.4, 0.8)
    })
  }, 50) // Actualizar cada 50ms
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
