/**
 * Archivo de configuración principal de vue-i18n
 * Configura la instancia de internacionalización para toda la aplicación
 * Soporta múltiples idiomas con localización por defecto
 */

import { createI18n } from 'vue-i18n'
import es from './es'
import en from './en'

export type SupportedLocale = 'es' | 'en'

const storedLocale = localStorage.getItem('corestream-locale')
const initialLocale: SupportedLocale = storedLocale === 'en' ? 'en' : 'es'

/**
 * Configuración de la instancia de vue-i18n
 * - locale: idioma por defecto (español)
 * - fallbackLocale: idioma alternativo si una traducción no existe
 * - messages: importa todos los archivos de idioma
 * - globalInjection: permite acceso global al objeto $t
 * - legacy: false para usar API de Composition
 */
const i18n = createI18n({
  locale: initialLocale,
  fallbackLocale: 'en',
  messages: {
    es,
    en,
  },
  globalInjection: true,
  legacy: false,
})

export function setLocale(locale: SupportedLocale): void {
  if (typeof (i18n.global.locale as any) === 'object' && 'value' in (i18n.global.locale as any)) {
    (i18n.global.locale as any).value = locale
  } else {
    (i18n.global as any).locale = locale
  }
  localStorage.setItem('corestream-locale', locale)
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', locale)
  }
}

export function getLocale(): SupportedLocale {
  const current = typeof (i18n.global.locale as any) === 'object' && 'value' in (i18n.global.locale as any)
    ? (i18n.global.locale as any).value
    : (i18n.global as any).locale
  return (current === 'en' ? 'en' : 'es') as SupportedLocale
}

export default i18n
