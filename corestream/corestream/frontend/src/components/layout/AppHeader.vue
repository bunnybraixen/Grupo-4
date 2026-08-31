<template>
  <!-- Encabezado superior de la aplicación CoreStream -->
  <!-- Proporciona navegación principal, cambio de rol, notificaciones y opciones de usuario -->
  <header class="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
    <div class="px-4 py-3 flex items-center justify-between gap-4">
      
      <!-- Sección izquierda: Logo y cambio de rol (Admin/Developer) -->
      <div class="flex items-center gap-6 min-w-0">
        <!-- Logo y nombre de CoreStream -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">C</span>
          </div>
          <span class="font-bold text-lg text-slate-900 dark:text-white hidden sm:inline">CoreStream</span>
        </div>

        <!-- Pestañas de cambio de rol (Admin/Developer) -->
        <!-- Permite alternar entre vista de Constructor y vista de Workbench -->
        <div class="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          <button
            @click="currentRole = 'admin'"
            :class="[
              'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
              currentRole === 'admin'
                ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            ]"
          >
            Builder
          </button>
          <button
            @click="currentRole = 'developer'"
            :class="[
              'px-3 py-1.5 rounded-md text-sm font-medium transition-all',
              currentRole === 'developer'
                ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            ]"
          >
            Workbench
          </button>
        </div>
      </div>

      <!-- Sección central: Se utiliza para expansión futura -->
      <div class="flex-1"></div>

      <!-- Sección derecha: Notificaciones, idioma, ajustes, usuario y modo oscuro -->
      <div class="flex items-center gap-3">
        
        <!-- Icono de campana de notificaciones con insignia -->
        <div class="relative group">
          <button 
            class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
            title="Notificaciones"
          >
            <svg class="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <!-- Insignia de notificaciones no leídas -->
            <span v-if="unreadNotifications > 0" class="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
              {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
            </span>
          </button>
          
          <!-- Panel desplegable de notificaciones (visible en hover) -->
          <div class="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 hidden group-hover:block p-4 z-50">
            <div class="space-y-3 max-h-96 overflow-y-auto">
              <div v-for="notification in notificationsList" :key="notification.id" class="flex gap-3 pb-3 border-b border-slate-100 dark:border-slate-700 last:border-0">
                <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0">
                  <span class="text-sm">{{ notification.avatar }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-slate-900 dark:text-white">{{ notification.title }}</p>
                  <p class="text-xs text-slate-600 dark:text-slate-400">{{ notification.message }}</p>
                  <p class="text-xs text-slate-500 dark:text-slate-500 mt-1">{{ notification.timestamp }}</p>
                </div>
                <div v-if="!notification.read" class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1"></div>
              </div>
            </div>
            <button class="w-full mt-3 px-3 py-2 text-sm text-blue-600 dark:text-blue-400 hover:bg-slate-50 dark:hover:bg-slate-700 rounded transition-colors">
              Marcar todo como leído
            </button>
          </div>
        </div>

        <!-- Selector de idioma con banderas -->
        <!-- Permite cambiar entre 5 idiomas: Español, Inglés, Portugués, Francés, Alemán -->
        <div class="relative group">
          <button 
            class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors text-lg"
            title="Idioma"
          >
            {{ languageFlags[currentLanguage] }}
          </button>
          <div class="absolute right-0 top-full mt-2 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 hidden group-hover:block z-50">
            <button
              v-for="(lang, code) in languageOptions"
              :key="code"
              @click="currentLanguage = code"
              :class="[
                'w-full px-4 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors',
                currentLanguage === code ? 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-400 font-medium' : 'text-slate-700 dark:text-slate-300'
              ]"
            >
              <span class="mr-2">{{ languageFlags[code] }}</span>{{ lang }}
            </button>
          </div>
        </div>

        <!-- Icono de ajustes -->
        <button 
          class="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          title="Ajustes"
        >
          <svg class="w-5 h-5 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>

        <!-- Divisor visual -->
        <div class="w-px h-6 bg-slate-200 dark:bg-slate-700"></div>

        <!-- Información del usuario y avatar -->
        <div class="flex items-center gap-3">
          <div class="text-right hidden sm:block">
            <p class="text-sm font-medium text-slate-900 dark:text-white">{{ userName }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">{{ userRole }}</p>
          </div>
          <!-- Avatar del usuario -->
          <div class="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm cursor-pointer hover:ring-2 hover:ring-blue-300 transition-all">
            {{ userInitials }}
          </div>
        </div>

        <!-- Toggle de modo oscuro -->
        <!-- Permite cambiar entre tema claro y oscuro -->
        <button 
          @click="darkMode = !darkMode"
          :class="[
            'p-2 rounded-lg transition-colors',
            darkMode 
              ? 'bg-slate-800 text-yellow-400' 
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          ]"
          title="Cambiar modo"
        >
          <!-- Icono de luna (modo oscuro) -->
          <svg v-if="!darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
          </svg>
          <!-- Icono de sol (modo claro) -->
          <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v2a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l-2.12-2.12a4 4 0 00 0-5.656 4 4 0 005.656 5.656l2.12-2.12a7 7 0 10-9.9-9.9l2.12 2.12a4 4 0 005.656 0 4 4 0 000-5.656l-2.12 2.12a7 7 0 109.9 9.9z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
/**
 * Componente AppHeader - Encabezado principal de CoreStream
 * 
 * Responsabilidades:
 * - Mostrar logo y nombre de CoreStream
 * - Permitir cambio entre rol Admin (Builder) y Developer (Workbench)
 * - Mostrar campana de notificaciones con contador de no leídas
 * - Selector de idioma con soporte a 5 idiomas
 * - Icono de ajustes para configuración
 * - Información del usuario actual con avatar
 * - Toggle para cambiar entre modo claro y oscuro
 * - Diseño responsivo que se adapta a pantallas pequeñas
 * 
 * La navegación del usuario es fundamental para acceder a ambas vistas principales
 * de la aplicación: la vista de Constructor (Admin) para gestionar epics y tickets,
 * y la vista de Workbench (Developer) para trabajar en los tickets asignados.
 */

import { ref, computed } from 'vue'

// ============================================================================
// ESTADOS REACTIVOS
// ============================================================================

/**
 * Rol actual del usuario
 * Puede ser 'admin' (vista Builder) o 'developer' (vista Workbench)
 */
const currentRole = ref<'admin' | 'developer'>('admin')

/**
 * Idioma actual de la aplicación
 * Soporta: es (Español), en (English), pt (Português), fr (Français), de (Deutsch)
 */
const currentLanguage = ref<'es' | 'en' | 'pt' | 'fr' | 'de'>('es')

/**
 * Estado del modo oscuro
 * true = modo oscuro activado, false = modo claro
 */
const darkMode = ref(false)

// ============================================================================
// DATOS ESTÁTICOS
// ============================================================================

/**
 * Mapeo de banderas para cada idioma
 * Utiliza emojis de banderas para representación visual
 */
const languageFlags = {
  es: '🇪🇸',
  en: '🇬🇧',
  pt: '🇵🇹',
  fr: '🇫🇷',
  de: '🇩🇪'
}

/**
 * Opciones de idioma disponibles
 * Muestra el nombre completo de cada idioma
 */
const languageOptions = {
  es: 'Español',
  en: 'English',
  pt: 'Português',
  fr: 'Français',
  de: 'Deutsch'
}

/**
 * Lista de notificaciones de ejemplo
 * En una aplicación real, esto vendría de una API o store global
 * Cada notificación tiene: id, avatar, title, message, timestamp, read status
 */
const notificationsList = ref([
  {
    id: 1,
    avatar: '👤',
    title: 'Ticket asignado',
    message: 'Te han asignado un nuevo ticket en el Epic de Autenticación',
    timestamp: 'hace 5 minutos',
    read: false
  },
  {
    id: 2,
    avatar: '✅',
    title: 'Ticket completado',
    message: 'Juan completó el ticket #42 - Validación de formulario',
    timestamp: 'hace 1 hora',
    read: true
  },
  {
    id: 3,
    avatar: '❓',
    title: 'Nueva pregunta',
    message: 'María tiene una duda en el ticket #38',
    timestamp: 'hace 3 horas',
    read: true
  }
])

// ============================================================================
// INFORMACIÓN DEL USUARIO
// ============================================================================

/**
 * Nombre del usuario actual
 * En una aplicación real, esto vendría del estado global o autenticación
 */
const userName = ref('Carlos Mendez')

/**
 * Rol del usuario actual
 * Se muestra debajo del nombre en el header
 */
const userRole = ref('Project Manager')

/**
 * Iniciales del usuario para el avatar
 * Se calcula a partir del nombre
 */
const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
})

// ============================================================================
// NOTIFICACIONES
// ============================================================================

/**
 * Contador de notificaciones no leídas
 * Se calcula dinámicamente a partir de la lista de notificaciones
 */
const unreadNotifications = computed(() => {
  return notificationsList.value.filter(n => !n.read).length
})
</script>

<style scoped lang="postcss">
/**
 * Estilos específicos del componente AppHeader
 * Utiliza Tailwind CSS a través de las clases en el template
 * Los estilos aquí son complementarios para comportamientos especiales
 */

/* Animación suave para transiciones de tema */
:deep(*) {
  @apply transition-colors duration-200;
}

/* Efecto hover en el avatar del usuario */
:deep(.user-avatar:hover) {
  @apply ring-2 ring-blue-300;
}
</style>
