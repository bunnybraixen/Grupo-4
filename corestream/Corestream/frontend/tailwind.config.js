/**
 * Configuración de Tailwind CSS para CoreStream
 * 
 * Define los colores personalizados de la marca, tipografía y modos de tema.
 * Tailwind utiliza estos valores para generar clases CSS reutilizables.
 */

export default {
  content: [
    './src/**/*.{vue,ts,tsx}',
    './index.html'
  ],

  theme: {
    extend: {
      colors: {
        lime: {
          DEFAULT: '#ADEA4B',
          90: '#B5EC5D', 80: '#BDEE6F', 70: '#C6F081', 60: '#CEF293',
          50: '#D6F4A5', 40: '#DEF7B7', 30: '#E6F9C9', 20: '#EFFBDB', 10: '#F7FDED',
        },
        teal: {
          DEFAULT: '#06B7B2',
          90: '#1FBEBA', 80: '#38C5C1', 70: '#51CDC9', 60: '#6AD4D1',
          50: '#82DBD8', 40: '#9BE2E0', 30: '#B4E9E8', 20: '#CDF1F0', 10: '#E6F8F7',
          dark: '#046B74', darker: '#049A95',
        },
        'dark-gray': {
          DEFAULT: '#142730',
          90: '#2B3D45', 80: '#435259', 70: '#5A686E', 60: '#727D83',
          50: '#899397', 40: '#A1A9AC', 30: '#B8BEC1', 20: '#D0D4D6', 10: '#E7E9EA',
        },
        accent: {
          'warm-1': '#C1108B', 'warm-2': '#D07AB8', 'warm-3': '#E8B4DA',
          'cold-1': '#1106C6', 'cold-2': '#2058D8', 'cold-3': '#82A6F7',
        },
        // Backward-compat aliases for existing text-primary, etc.
        primary: '#ADEA4B',
        success: '#06B7B2',
        warning: '#F59E0B',
        danger: '#EF4444',
        // Semantic colors using CSS variables (for theme system)
        'semantic': {
          'bg-app':    'var(--bg-app)',
          'bg-card':   'var(--bg-card)',
          'bg-sidebar':'var(--bg-sidebar)',
          'bg-header': 'var(--bg-header)',
          'bg-panel':  'var(--bg-panel)',
          'bg-input':  'var(--bg-input)',
          'bg-modal':  'var(--bg-modal)',
          'bg-dropdown': 'var(--bg-dropdown)',
          'bg-tag':    'var(--bg-tag)',
          'text-base': 'var(--text-primary)',
          'text-sub':  'var(--text-secondary)',
          'text-muted':'var(--text-muted)',
          'border':    'var(--border-color)',
          'border-subtle': 'var(--border-subtle)',
          'border-focus':  'var(--border-focus)',
        }
      },
      fontFamily: {
        sans: ['Nunito', 'Calibri', 'sans-serif'],
      },
    },
  },

  darkMode: ['selector', '[data-theme="dark"]'],
  plugins: []
}
