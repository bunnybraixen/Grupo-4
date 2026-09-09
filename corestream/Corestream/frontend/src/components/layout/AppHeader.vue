<template>
  <!-- Encabezado superior de la aplicación CoreStream -->
  <!-- Proporciona navegación principal, cambio de rol, notificaciones y opciones de usuario -->
  <header class="bg-[var(--bg-header)] border-b border-[var(--border-subtle)] sticky top-0 z-[100]">
    <div class="px-4 py-3 flex items-center justify-between gap-4">

      <!-- Sección izquierda: Logo y cambio de rol (Admin/Developer) -->
      <div class="flex items-center gap-6 min-w-0">
        <!-- Botón para alternar el sidebar del layout (solo móvil) -->
        <button
          @click="eventBus.emit('toggle-sidebar')"
          class="md:hidden p-2 -ml-2 rounded hover:bg-[var(--bg-panel)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--teal)]"
          aria-label="Alternar menú de navegación"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        </button>

        <!-- Logo y nombre de CoreStream -->
        <div class="flex items-center gap-2 flex-shrink-0">
          <img
            :src="logoUrl"
            alt="CoreStream"
            class="w-8 h-8 rounded-lg object-cover"
          />
          <span class="font-bold text-lg text-[var(--text-primary)] hidden sm:inline">CoreStream</span>
        </div>

      </div>

      <!-- Sección central: Se utiliza para expansión futura -->
      <div class="flex-1"></div>

      <!-- Sección derecha: Notificaciones, idioma, ajustes, usuario y modo oscuro -->
      <div class="flex items-center gap-3">
        
        <!-- Campana de notificaciones -->
        <NotificationBell />

        <!-- Icono de ajustes -->
        <button
          @click="openSettingsModal"
          class="p-2 hover:bg-[var(--bg-panel)] rounded-lg transition-colors"
          title="Ajustes"
        >
          <svg class="w-5 h-5 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>

        <!-- Divisor visual -->
        <div class="w-px h-6 bg-[var(--border-subtle)]"></div>

        <!-- Información del usuario y avatar -->
        <div class="flex items-center gap-3">
          <div class="text-right hidden sm:block">
            <p class="text-sm font-medium text-[var(--text-primary)]">{{ userName }}</p>
            <p class="text-xs text-[var(--text-secondary)]">{{ userRole }}</p>
          </div>
          <!-- Avatar del usuario con badge de líder -->
          <div class="relative w-8 h-8 bg-gradient-to-br from-teal to-teal-dark rounded-full flex items-center justify-center text-white font-bold text-sm cursor-pointer hover:ring-2 hover:ring-teal-30 transition-all">
            {{ userInitials }}
            <!-- Badge dorado (👑) para líderes de equipo -->
            <div v-if="authStore.isTeamLeader" class="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center text-xs flex-shrink-0" title="Líder de Equipo">
              👑
            </div>
          </div>
        </div>

        <!-- Divisor visual -->
        <div class="w-px h-6 bg-[var(--border-subtle)]"></div>

        <!-- Cerrar sesión -->
        <button
          type="button"
          @click="logout"
          class="px-3 py-2 rounded-lg bg-[var(--priority-urg-bg)] text-white text-sm font-medium hover:opacity-90 transition-colors whitespace-nowrap"
        >
          {{ t('header.logout') }}
        </button>
      </div>
    </div>
  </header>
  <!-- ========================================== -->
  <!-- MODAL DE CONFIGURACIÓN (CS-043)            -->
  <!-- ========================================== -->
  <div v-if="showSettingsModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm" @click="showSettingsModal = false">
    <div class="w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col bg-[var(--bg-app)] rounded-2xl shadow-2xl transform transition-all border border-[var(--border-subtle)]" @click.stop>
      <!-- Cabecera del Modal -->
      <div class="p-6 border-b border-[var(--border-subtle)] bg-[var(--bg-header)] flex justify-between items-center">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-[var(--bg-panel)] rounded-xl flex items-center justify-center border border-[var(--border-subtle)]">
            <span class="text-2xl">⚙️</span>
          </div>
          <div>
            <h2 class="text-xl font-bold text-[var(--text-primary)]">Configuración</h2>
            <p class="text-sm text-[var(--text-secondary)]">Personaliza tu experiencia en CoreStream</p>
          </div>
        </div>
        <button @click="showSettingsModal = false" class="p-2 rounded-xl hover:bg-[var(--bg-panel)] text-[var(--text-secondary)] transition-colors">
          <span class="text-xl">✕</span>
        </button>
      </div>

      <!-- Contenido scrolleable -->
      <div class="p-6 overflow-y-auto flex-1 space-y-8">
        
        <!-- SECCIÓN 1: PERFIL -->
        <section>
          <h3 class="text-sm font-bold uppercase tracking-wider text-[var(--text-muted)] mb-4">Perfil de Usuario</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Nombre</label>
              <input v-model="profileForm.firstName" type="text" class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Apellidos</label>
              <input v-model="profileForm.lastName" type="text" class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Correo Electrónico</label>
              <input v-model="profileForm.email" type="email" class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" />
            </div>
          </div>
        </section>

        <hr class="border-[var(--border-subtle)]" />

        <!-- SECCIÓN 2: APARIENCIA E IDIOMA -->
        <section>
          <h3 class="text-sm font-bold uppercase tracking-wider text-[var(--text-muted)] mb-4">Apariencia e Idioma</h3>
          <div class="space-y-4">
            <!-- Tema -->
            <div class="flex items-center justify-between p-4 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)]">
              <div class="flex items-center gap-3">
                <span class="text-2xl">{{ themeStore.isDark() ? '🌙' : '☀️' }}</span>
                <div>
                  <p class="text-sm font-semibold text-[var(--text-primary)]">Tema de la Interfaz</p>
                  <p class="text-xs text-[var(--text-secondary)]">Elige entre modo claro u oscuro</p>
                </div>
              </div>
              <div class="flex bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-lg p-1">
                <button @click="themeStore.previewTheme('light')" :class="[!themeStore.isDark() ? 'bg-[var(--bg-panel)] shadow-sm text-[var(--teal)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]', 'px-4 py-1.5 rounded-md text-sm font-medium transition-all']">Claro</button>
                <button @click="themeStore.previewTheme('dark')" :class="[themeStore.isDark() ? 'bg-[var(--bg-panel)] shadow-sm text-[var(--teal)]' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]', 'px-4 py-1.5 rounded-md text-sm font-medium transition-all']">Oscuro</button>
              </div>
            </div>

            <!-- Idiomas -->
            <div class="p-4 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-panel)]">
              <div class="mb-3">
                <p class="text-sm font-semibold text-[var(--text-primary)]">{{ t('header.language') }}</p>
                <p class="text-xs text-[var(--text-secondary)]">Selecciona tu idioma preferido</p>
              </div>
              <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
                <button v-for="(lang, code) in languageOptions" :key="code" @click="changeLocale(code)" :class="['px-3 py-2 text-sm rounded-lg border transition-all flex items-center gap-2', locale === code ? 'border-[var(--lime)] bg-[var(--lime)]/10 text-[var(--lime)] font-medium' : 'border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-secondary)] hover:border-[var(--text-muted)]']">
                  <span class="text-lg">{{ languageFlags[code as keyof typeof languageFlags] }}</span> {{ lang }}
                </button>
              </div>
            </div>
          </div>
        </section>



        <!-- SECCIÓN 4: CUENTA -->
        <section>
          <h3 class="text-sm font-bold uppercase tracking-wider text-[var(--text-muted)] mb-4">Cuenta</h3>
          <div class="grid grid-cols-2 gap-3">
            <button @click="openPasswordModal" type="button" class="group p-4 rounded-xl text-left border border-orange-500/20 bg-orange-500/10 hover:bg-orange-500/20 transition-all flex flex-col">
              <span class="text-3xl mb-2 block group-hover:scale-110 transition-transform origin-left">🔐</span>
              <p class="text-sm font-medium text-[var(--text-primary)]">Cambiar Contraseña</p>
              <p class="text-xs text-[var(--text-secondary)]">Actualiza tus credenciales</p>
            </button>

            <button @click="exportUserData" type="button" class="group p-4 rounded-xl text-left border border-blue-500/20 bg-blue-500/10 hover:bg-blue-500/20 transition-all flex flex-col">
              <span class="text-3xl mb-2 block group-hover:scale-110 transition-transform origin-left">📊</span>
              <p class="text-sm font-medium text-[var(--text-primary)]">Exportar Datos</p>
              <p class="text-xs text-[var(--text-secondary)]">Descarga tus datos</p>
            </button>
          </div>
        </section>

        <hr class="border-[var(--border-subtle)]" />
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-[var(--border-subtle)] bg-[var(--bg-header)] flex justify-end gap-3">
        <button @click="cancelSettings" class="px-5 py-2.5 rounded-xl font-medium border border-[var(--border-subtle)] bg-[var(--bg-panel)] text-[var(--text-primary)] hover:bg-[var(--bg-card)]/10 transition-colors">Cancelar</button>
        <button @click="saveSettings" :disabled="isSaving" class="px-5 py-2.5 rounded-xl font-bold text-[var(--dark-gray)] bg-[var(--lime)] hover:bg-[var(--lime)]/90 transition-colors shadow-lg flex items-center gap-2">
          <span v-if="isSaving" class="animate-spin">⏳</span>
          {{ isSaving ? 'Guardando...' : 'Guardar Preferencias' }}
        </button>
      </div>
    </div>
  </div>
  <div v-if="showPasswordModal" style="z-index: 9999;" class="fixed inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click="showPasswordModal = false">
    <div class="w-full max-w-md bg-[var(--bg-app)] rounded-2xl shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-[var(--border-subtle)] overflow-hidden" @click.stop>
      <div class="p-5 border-b border-[var(--border-subtle)] bg-[var(--bg-header)] flex justify-between items-center">
        <h3 class="text-lg font-bold text-[var(--text-primary)]">Cambiar Contraseña</h3>
        <button @click="showPasswordModal = false" class="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-xl">✕</button>
      </div>
      <form @submit.prevent="submitPasswordChange" class="p-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Contraseña Actual</label>
          <input v-model="passwordForm.oldPassword" type="password" required class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" placeholder="••••••••" />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Nueva Contraseña</label>
          <input v-model="passwordForm.newPassword" type="password" required minlength="8" class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" placeholder="Mínimo 8 caracteres" />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">Confirmar Nueva Contraseña</label>
          <input v-model="passwordForm.confirmPassword" type="password" required minlength="8" class="w-full px-4 py-2 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] text-[var(--text-primary)] focus:ring-2 focus:ring-[var(--teal)] outline-none" placeholder="Repite la nueva contraseña" />
        </div>
        <div class="pt-4 flex justify-end gap-3">
          <button type="button" @click="showPasswordModal = false; resetPasswordForm()" class="px-4 py-2 rounded-xl text-sm font-medium border border-[var(--border-subtle)] text-[var(--text-primary)] hover:bg-[var(--bg-card)]/10">Cancelar</button>
          <button type="submit" :disabled="isChangingPassword" class="px-4 py-2 rounded-xl text-sm font-bold text-[var(--dark-gray)] bg-[var(--lime)] hover:bg-[var(--lime)]/90 disabled:opacity-50 transition-all">
            {{ isChangingPassword ? 'Guardando...' : 'Actualizar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Componente AppHeader - Encabezado principal de CoreStream
 * 
 * Responsabilidades:
 * - Mostrar logo y nombre de CoreStream
 * - Mostrar campana de notificaciones con contador de no leídas
 * - Selector de idioma con soporte a 5 idiomas
 * - Icono de ajustes para configuración
 * - Información del usuario actual con avatar
 * - Toggle para cambiar entre modo claro y oscuro
 * - Diseño responsivo que se adapta a pantallas pequeñas
 *
 * La navegación por módulo (Builder / Workbench) se realiza exclusivamente
 * a través del sidebar de cada layout, separado por rol.
 */

import { ref, computed, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore, useThemeStore } from '@/stores'
import { useDialogStore } from '@/stores/dialog'
import type { Theme } from '@/stores/theme'
import { api } from '@/services/api'
import NotificationBell from '@/components/shared/NotificationBell.vue'
import logoUrl from '@/assets/logo-corestream.jpeg'
import { eventBus } from '@/utils/eventBus'

// ============================================================================
// ESTADOS REACTIVOS
// ============================================================================

/**
 * Estado para mostrar/ocultar el menú de selección de idioma
 */
const showLanguageMenu = ref(false)

const authStore = useAuthStore()
const themeStore = useThemeStore()
const dialogStore = useDialogStore()
const i18n = useI18n()
const { t } = i18n
const router = useRouter()



/**
 * Obtener el idioma actual con tipado correcto
 * Permite acceder a locale como ref reactiva
 */
const locale = computed<'es' | 'en' | 'pt' | 'fr' | 'de'>(() =>
  (i18n.locale.value as 'es' | 'en' | 'pt' | 'fr' | 'de') || 'es'
)

/**
 * Inicializar idioma desde localStorage
 * Si existe un idioma guardado, aplicarlo a i18n
 */
const savedLocale = localStorage.getItem('corestream-locale')
if (savedLocale) {
  i18n.locale.value = savedLocale
}

/**
 * Cambia el idioma de la aplicación y persiste en localStorage
 */
function changeLocale(newLocale: string): void {
  i18n.locale.value = newLocale
  localStorage.setItem('corestream-locale', newLocale)
  showLanguageMenu.value = false
}

/**
 * Alterna la visibilidad del menú de idioma
 */
function toggleLanguageMenu(): void {
  showLanguageMenu.value = !showLanguageMenu.value
}

/**
 * Cierra el menú de idioma al hacer click fuera
 */
function closeLanguageMenu(): void {
  showLanguageMenu.value = false
}

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


// ============================================================================
// INFORMACIÓN DEL USUARIO
// ============================================================================

/**
 * Nombre del usuario actual
 * Proviene del estado global de autenticación
 */
const userName = computed(() => authStore.user?.fullName || 'Usuario')

/**
 * Rol del usuario actual
 * Se muestra debajo del nombre en el header
 */
const userRole = computed(() => authStore.user?.role || 'Rol no definido')

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

/**
 * Cierra la sesión del usuario y redirige al login
 */
const logout = async () => {
  await authStore.logout()
  await router.push('/login')
}

// ============================================================================
// CONFIGURACIÓN (CS-043)
// ============================================================================
const showSettingsModal = ref(false)
const isSaving = ref(false)
const showPasswordModal = ref(false)
const originalTheme = ref<Theme>('light')
const isChangingPassword = ref(false)
const passwordForm = reactive({ 
  oldPassword: '', 
  newPassword: '', 
  confirmPassword: ''
})

const profileForm = reactive({
  firstName: authStore.user?.fullName?.split(' ')[0] || '',
  lastName: authStore.user?.fullName?.split(' ').slice(1).join(' ') || '',
  email: authStore.user?.email || ''
})

const userPrefs = authStore.user?.preferences || {}

const notifEnabled = reactive({
  email: true,
  push: true,
  mobile: false,
  reminders: false,
})

const notifications = computed(() => ({
  email:     { icon: '📧', title: t('settings.notifEmail'),     desc: t('settings.notifEmailDesc'),     enabled: notifEnabled.email },
  push:      { icon: '🔔', title: t('settings.notifPush'),      desc: t('settings.notifPushDesc'),      enabled: notifEnabled.push },
  mobile:    { icon: '📱', title: t('settings.notifMobile'),    desc: t('settings.notifMobileDesc'),    enabled: notifEnabled.mobile },
  reminders: { icon: '⏰', title: t('settings.notifReminders'), desc: t('settings.notifRemindersDesc'), enabled: notifEnabled.reminders },
}))

function toggleNotif(key: string) {
  const k = key as keyof typeof notifEnabled
  notifEnabled[k] = !notifEnabled[k]
}

const openSettingsModal = async () => {
  // Sincronizar con el backend para tener los datos más recientes
  try { 
    await authStore.fetchMe(); 
  } catch (e) { 
    console.error("Error al sincronizar usuario:", e); 
  }
  
  const user = authStore.user as any;

  if (user) {
    // Cargar datos del perfil en el formulario
    const nameParts = user.fullName?.split(' ') || [];
    profileForm.firstName = nameParts[0] || '';
    profileForm.lastName = nameParts.slice(1).join(' ') || '';
    profileForm.email = user.email || '';

    // Obtener preferencias
    let prefs = user.preferences || {};
    
    // Si la BD devuelve un string por accidente, lo convertimos a objeto
    if (typeof prefs === 'string') {
      try { 
        prefs = JSON.parse(prefs); 
      } catch (e) { 
        prefs = {}; 
      }
    }

    // Función auxiliar para leer booleanos limpios o los objetos antiguos
    const getBool = (val: any, defaultVal: boolean) => {
      if (typeof val === 'boolean') return val;
      if (val && typeof val === 'object' && val.enabled !== undefined) return Boolean(val.enabled);
      return defaultVal;
    };

    // Asignar los valores a los switches
    notifEnabled.email = getBool(prefs.email, true);
    notifEnabled.push = getBool(prefs.push, true);
    notifEnabled.mobile = getBool(prefs.mobile, false);
    notifEnabled.reminders = getBool(prefs.reminders, false);
  }
  
  // 5. Guardar tema actual como referencia para poder revertir en Cancelar
  originalTheme.value = themeStore.getTheme()

  // 6. Mostrar el modal
  showSettingsModal.value = true;
}

const cancelSettings = () => {
  themeStore.applyTheme(originalTheme.value)
  showSettingsModal.value = false
}

const saveSettings = async () => {
  isSaving.value = true
  try {
    // 1. Extraemos los true/false + tema seleccionado
    const prefsToSave = {
      email: notifEnabled.email,
      push: notifEnabled.push,
      mobile: notifEnabled.mobile,
      reminders: notifEnabled.reminders,
      theme: themeStore.getTheme()
    };

    // 2. Guardamos enviando el objeto limpio
    const updatedUser = await api.auth.updateSettings({
      firstName: profileForm.firstName,
      lastName: profileForm.lastName,
      email: profileForm.email,
      preferences: prefsToSave 
    });

    // Confirmar el tema en localStorage (hasta ahora era solo previsualización)
    themeStore.applyTheme(themeStore.getTheme())

    authStore.$patch((state) => {
      if (state.user) {
        state.user.fullName = updatedUser.fullName;
        state.user.email = updatedUser.email;
        state.user.preferences = updatedUser.preferences;
      }
    });

    showSettingsModal.value = false;
    dialogStore.alert('¡Preferencias guardadas exitosamente!');
  } catch (error) {
    console.error('Error al guardar:', error);
    dialogStore.alert('Hubo un error al guardar las preferencias.');
  } finally {
    isSaving.value = false
  }
}

const openPasswordModal = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  showPasswordModal.value = true
}

const submitPasswordChange = async () => {
  // Validación de coincidencia
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    dialogStore.alert('Las nuevas contraseñas no coinciden. Por favor, verifica.')
    return
  }

  if (passwordForm.newPassword.length < 8) {
    dialogStore.alert('Por seguridad, la nueva contraseña debe tener al menos 8 caracteres.')
    return
  }

  isChangingPassword.value = true
  try {
    await api.auth.changePassword({ 
      oldPassword: passwordForm.oldPassword, 
      newPassword: passwordForm.newPassword 
    })
    
    dialogStore.alert('¡Contraseña actualizada con éxito! 🔐')

    resetPasswordForm()
    showPasswordModal.value = false
  } catch (error: any) {
    console.error(error)
    const mensajeReal = error.response?.data?.detail || error.message || 'Verifica tu contraseña actual.'
    dialogStore.alert(`Error al cambiar la contraseña: ${mensajeReal}`)
  } finally {
    isChangingPassword.value = false
  }
}

const resetPasswordForm = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}



const exportUserData = () => {
  // Extraemos las preferencias del usuario global
  const { preferences, ...cleanData } = authStore.user || {}

  // Armamos el paquete
  const dataToExport = {
    perfil: profileForm,
    preferencias: notifEnabled,
    datosSesion: cleanData,
    fechaExportacion: new Date().toISOString()
  }

  const dataStr = JSON.stringify(dataToExport, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)

  const a = document.createElement('a')
  a.href = url
  a.download = `corestream_datos_${profileForm.firstName || 'usuario'}.json`
  document.body.appendChild(a)
  a.click()
  
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

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
