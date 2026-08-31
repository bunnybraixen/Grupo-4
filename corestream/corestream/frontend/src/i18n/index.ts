/**
 * Archivo de configuración principal de vue-i18n
 * Configura la instancia de internacionalización para toda la aplicación
 * Soporta múltiples idiomas con localización por defecto
 */

import { createI18n } from 'vue-i18n'
import es from './es'
import en from './en'
import fr from './fr'
import de from './de'
import pt from './pt'

/**
 * Tipo para los mensajes disponibles
 * Asegura tipado fuerte de las traducciones en toda la aplicación
 */
type MessageSchema = typeof es

/**
 * Configuración de la instancia de vue-i18n
 * - locale: idioma por defecto (español)
 * - fallbackLocale: idioma alternativo si una traducción no existe
 * - messages: importa todos los archivos de idioma
 * - globalInjection: permite acceso global al objeto $t
 * - legacy: false para usar API de Composition
 */
const i18n = createI18n<MessageSchema>({
  locale: 'es',
  fallbackLocale: 'en',
  messages: {
    es,
    en,
    fr,
    de,
    pt,
  },
  globalInjection: true,
  legacy: false,
})

export default i18n
