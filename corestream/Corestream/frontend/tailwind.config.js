/**
 * Configuración de Tailwind CSS para CoreStream
 * 
 * Define los colores personalizados de la marca, tipografía y modos de tema.
 * Tailwind utiliza estos valores para generar clases CSS reutilizables.
 */

export default {
  /**
   * Especifica qué archivos Tailwind debe examinar para detectar clases utilizadas
   * Solo incluye las clases que realmente se utilizan en la compilación final
   */
  content: [
    './src/**/*.{vue,ts,tsx}',
    './index.html'
  ],

  /**
   * Tema personalizado que extiende los valores por defecto de Tailwind
   * Define colores corporativos y estilos específicos de CoreStream
   */
  theme: {
    extend: {
      /**
       * Colores personalizados de CoreStream
       * Estos colores se utilizan en todo el proyecto para mantener consistencia visual
       */
      colors: {
        /**
         * Color primario corporativo - Azul
         * Utilizado en botones principales, enlaces y elementos destacados
         */
        primary: '#2563EB',

        /**
         * Color de éxito - Verde
         * Utilizado en acciones completadas, estados exitosos y validaciones positivas
         */
        success: '#10B981',

        /**
         * Color de advertencia - Ámbar
         * Utilizado en alertas, elementos pendientes y situaciones que requieren atención
         */
        warning: '#F59E0B',

        /**
         * Color de peligro/error - Rojo
         * Utilizado en mensajes de error, eliminaciones y situaciones críticas
         */
        danger: '#EF4444',

        /**
         * Color secundario - Índigo
         * Utilizado en elementos secundarios, desplegables y componentes auxiliares
         */
        indigo: '#6366F1'
      }
    }
  },

  /**
   * Modo oscuro - Utiliza la clase 'dark' en el elemento raíz (HTML)
   * Cuando se agrega la clase 'dark' al <html>, Tailwind aplica estilos oscuros
   * Ejemplos: dark:bg-gray-900, dark:text-white, etc.
   */
  darkMode: 'class',

  /**
   * Configuración de complementos
   * Extiende Tailwind con funcionalidades adicionales
   */
  plugins: []
}
