/**
 * Store de Tema — CoreStream
 *
 * Gestiona el estado del tema (claro/oscuro) y aplica los cambios al DOM.
 *
 * Características:
 * - Persistencia en localStorage
 * - Sincronización con atributo data-theme en <html>
 * - Modo claro como default (según manual de usuario)
 * - Transiciones suaves entre temas
 */

import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  /**
   * Tema actual
   * Default: 'light' (modo claro como muestra el manual)
   * Se lee de localStorage si existe
   */
  const theme = ref<Theme>(
    (localStorage.getItem('corestream-theme') as Theme) || 'light'
  )

  /**
   * Aplicar tema al documento
   * Establece data-theme en el elemento html
   * y guarda preferencia en localStorage
   */
  function applyTheme(t: Theme) {
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('corestream-theme', t)
    theme.value = t
  }

  /**
   * Alternar entre tema claro y oscuro
   */
  function toggleTheme() {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    applyTheme(newTheme)
  }

  /**
   * Vista previa del tema: aplica al DOM sin guardar en localStorage.
   * Usar durante el modal de configuración; confirmar con applyTheme al Guardar
   * o revertir con applyTheme(original) al Cancelar.
   */
  function previewTheme(t: Theme) {
    document.documentElement.setAttribute('data-theme', t)
    theme.value = t
  }

  /**
   * Establecer tema específico
   */
  function setTheme(t: Theme) {
    applyTheme(t)
  }

  /**
   * Obtener tema actual
   */
  function getTheme(): Theme {
    return theme.value
  }

  /**
   * Verificar si está en modo oscuro
   */
  function isDark(): boolean {
    return theme.value === 'dark'
  }

  /**
   * Observar cambios de tema y aplicarlos
   */
  watch(theme, (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('corestream-theme', newTheme)
  })

  /**
   * Aplicar tema inicial al crear el store
   * Esto se ejecuta antes de montar la app
   */
  applyTheme(theme.value)

  return {
    theme,
    applyTheme,
    toggleTheme,
    previewTheme,
    setTheme,
    getTheme,
    isDark,
  }
})
