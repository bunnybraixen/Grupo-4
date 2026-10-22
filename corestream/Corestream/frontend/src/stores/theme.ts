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
import { ref } from 'vue'

export type Theme = 'light' | 'dark'

export const useThemeStore = defineStore('theme', () => {
  /**
   * Tema actual
   * Default: 'light' (modo claro como muestra el manual)
   * Se lee de localStorage si existe
   */
  const savedTheme = localStorage.getItem('corestream-theme')
  const theme = ref<Theme>(savedTheme === 'dark' ? 'dark' : 'light')

  function syncTheme(t: Theme) {
    const root = document.documentElement
    root.setAttribute('data-theme', t)
    root.classList.toggle('dark', t === 'dark')
  }

  /**
   * Aplicar tema al documento
   * Establece data-theme en el elemento html
   * y guarda preferencia en localStorage
   */
  function applyTheme(t: Theme) {
    theme.value = t
    syncTheme(t)
    localStorage.setItem('corestream-theme', t)
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
    theme.value = t
    syncTheme(t)
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
