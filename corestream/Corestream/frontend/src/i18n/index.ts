/**
 * Archivo de configuración principal de vue-i18n
 * Configura la instancia de internacionalización para toda la aplicación
 * Soporta múltiples idiomas con localización por defecto
 */
 
import { createI18n } from 'vue-i18n'
import type { MessageCompiler, MessageContext } from 'vue-i18n'
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
 * Compilador de mensajes propio, sin JIT.
 *
 * Por defecto vue-i18n compila cada mensaje a una función con `new Function`
 * la primera vez que se usa (JIT compilation) — esto viola la CSP
 * `script-src 'self'` del contenedor (frontend/nginx/default.conf), que a
 * propósito no incluye 'unsafe-eval'.
 *
 * Se probó primero precompilar en build time con @intlify/unplugin-vue-i18n,
 * pero introduce un bug de números de código de error duplicados entre
 * chunks (SyntaxError vacío, code=24) al combinarse con el code-splitting
 * de Vite en esta versión de vue-i18n — con o sin dropMessageCompiler.
 *
 * Como todos los mensajes en es/en/fr/de/pt.ts solo usan interpolación
 * simple con nombre (`{n}`, `{year}`, `{count}` — sin plural ICU ni mensajes
 * enlazados `@:`), un compilador propio minimalista cubre el 100% de los
 * casos reales sin depender de eval en ninguna forma.
 */
const messageCompiler: MessageCompiler = (message, { onError, key }) => {
  if (typeof message !== 'string') {
    onError?.({ name: 'CompileError', message: `CoreStream i18n: mensaje no textual en la clave '${key}'`, code: -1 } as any)
    return () => ''
  }
  return (ctx: MessageContext) => message.replace(/\{(\w+)\}/g, (match, name) => {
    const value = ctx.named(name)
    return value === undefined ? match : String(value)
  })
}

/**
 * Configuración de la instancia de vue-i18n
 * - locale: idioma por defecto (español)
 * - fallbackLocale: idioma alternativo si una traducción no existe
 * - messages: importa todos los archivos de idioma
 * - globalInjection: permite acceso global al objeto $t
 * - legacy: false para usar API de Composition
 * - messageCompiler: ver comentario arriba
 */
const i18n = createI18n({
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
  messageCompiler,
} as any)

export default i18n
