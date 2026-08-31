/**
 * Configuración de PostCSS para CoreStream
 * 
 * PostCSS es un transformador de CSS que procesa estilos a través de plugins.
 * En este caso utilizamos:
 * - tailwindcss: para generar clases CSS basadas en utilidad
 * - autoprefixer: para añadir prefijos del navegador automáticamente (-webkit-, -moz-, etc.)
 */

export default {
  /**
   * Lista de plugins de PostCSS a ejecutar en orden
   * El orden importa: Tailwind debe procesarse antes de Autoprefixer
   */
  plugins: {
    /**
     * Plugin de Tailwind CSS
     * Genera todas las clases CSS reutilizables basadas en la configuración
     * y el contenido de los archivos especificados en tailwind.config.js
     */
    tailwindcss: {},

    /**
     * Plugin Autoprefixer
     * Añade prefijos específicos del navegador a propiedades CSS
     * Ejemplo: transform -> -webkit-transform, -moz-transform, etc.
     * Garantiza compatibilidad con navegadores más antiguos
     */
    autoprefixer: {}
  }
}
