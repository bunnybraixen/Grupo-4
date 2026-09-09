<template>
  <div class="flex flex-col min-h-screen bg-[var(--bg-app)]">
    <AppHeader />

    <div class="p-8 flex-1 overflow-auto max-w-3xl mx-auto w-full">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-[var(--text-primary)] mb-1">⚙ Configuración</h1>
        <p class="text-[var(--text-secondary)] text-sm">Gestiona tu perfil, seguridad y preferencias</p>
      </div>

      <!-- SECCIÓN: Perfil -->
      <section class="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-6 mb-6">
        <h2 class="text-base font-semibold text-[var(--text-primary)] mb-4">👤 Perfil</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1">Nombre</label>
            <input
              v-model="profile.firstName"
              type="text"
              class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)]"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1">Apellido</label>
            <input
              v-model="profile.lastName"
              type="text"
              class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)]"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1">Email</label>
            <input
              :value="profile.email"
              readonly
              type="email"
              class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-muted)] cursor-not-allowed"
            />
          </div>
          <div>
            <label class="block text-xs font-semibold text-[var(--text-secondary)] mb-1">Especialidad</label>
            <input
              v-model="profile.specialty"
              type="text"
              placeholder="Ej: Frontend, Backend, DevOps…"
              class="w-full px-3 py-2 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] placeholder-[var(--text-muted)]"
            />
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button
            @click="saveProfile"
            :disabled="isSavingProfile"
            class="px-4 py-2 text-sm font-semibold bg-[var(--teal)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {{ isSavingProfile ? 'Guardando…' : 'Guardar perfil' }}
          </button>
        </div>
      </section>

      <!-- SECCIÓN: Seguridad -->
      <section class="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-6 mb-6">
        <h2 class="text-base font-semibold text-[var(--text-primary)] mb-4">🔒 Seguridad</h2>
        <div class="space-y-4">
          <!-- Contraseña actual — uses floating label to avoid placeholder showing as dots -->
          <div class="relative">
            <label
              :class="[
                'absolute left-3 transition-all pointer-events-none text-[var(--text-muted)]',
                pwForm.current || pwCurrentFocused
                  ? '-top-2 text-[10px] bg-[var(--bg-card)] px-1'
                  : 'top-2.5 text-sm'
              ]"
            >
              Contraseña Actual
            </label>
            <input
              v-model="pwForm.current"
              :type="showCurrent ? 'text' : 'password'"
              @focus="pwCurrentFocused = true"
              @blur="pwCurrentFocused = false"
              class="w-full px-3 py-2.5 pt-3 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] pr-10"
            />
            <button
              type="button"
              @click="showCurrent = !showCurrent"
              class="absolute right-3 top-2.5 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              tabindex="-1"
            >{{ showCurrent ? '🙈' : '👁' }}</button>
          </div>

          <div class="relative">
            <label
              :class="[
                'absolute left-3 transition-all pointer-events-none text-[var(--text-muted)]',
                pwForm.next || pwNextFocused
                  ? '-top-2 text-[10px] bg-[var(--bg-card)] px-1'
                  : 'top-2.5 text-sm'
              ]"
            >
              Nueva Contraseña
            </label>
            <input
              v-model="pwForm.next"
              :type="showNext ? 'text' : 'password'"
              @focus="pwNextFocused = true"
              @blur="pwNextFocused = false"
              class="w-full px-3 py-2.5 pt-3 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] pr-10"
            />
            <button
              type="button"
              @click="showNext = !showNext"
              class="absolute right-3 top-2.5 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              tabindex="-1"
            >{{ showNext ? '🙈' : '👁' }}</button>
          </div>

          <div class="relative">
            <label
              :class="[
                'absolute left-3 transition-all pointer-events-none text-[var(--text-muted)]',
                pwForm.confirm || pwConfirmFocused
                  ? '-top-2 text-[10px] bg-[var(--bg-card)] px-1'
                  : 'top-2.5 text-sm'
              ]"
            >
              Confirmar Nueva Contraseña
            </label>
            <input
              v-model="pwForm.confirm"
              :type="showConfirm ? 'text' : 'password'"
              @focus="pwConfirmFocused = true"
              @blur="pwConfirmFocused = false"
              class="w-full px-3 py-2.5 pt-3 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)] pr-10"
              :class="pwForm.confirm && pwForm.next !== pwForm.confirm ? 'border-red-500' : ''"
            />
            <button
              type="button"
              @click="showConfirm = !showConfirm"
              class="absolute right-3 top-2.5 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              tabindex="-1"
            >{{ showConfirm ? '🙈' : '👁' }}</button>
          </div>

          <p v-if="pwForm.confirm && pwForm.next !== pwForm.confirm" class="text-xs text-red-500">
            Las contraseñas no coinciden
          </p>
          <p v-if="pwError" class="text-xs text-red-500">{{ pwError }}</p>
          <p v-if="pwSuccess" class="text-xs text-[var(--teal)]">✓ Contraseña actualizada</p>

          <div class="flex justify-end">
            <button
              @click="changePassword"
              :disabled="!pwForm.current || !pwForm.next || pwForm.next !== pwForm.confirm || isChangingPw"
              class="px-4 py-2 text-sm font-semibold bg-[var(--teal)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {{ isChangingPw ? 'Actualizando…' : 'Cambiar contraseña' }}
            </button>
          </div>
        </div>
      </section>

      <!-- SECCIÓN: Preferencias -->
      <section class="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-6 mb-6">
        <h2 class="text-base font-semibold text-[var(--text-primary)] mb-4">🎨 Preferencias</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-[var(--text-primary)]">Modo oscuro</p>
              <p class="text-xs text-[var(--text-muted)]">Cambia entre tema claro y oscuro</p>
            </div>
            <button
              @click="toggleThemeDraft"
              :class="draftIsDark ? 'bg-[var(--teal)]' : 'bg-[var(--border-subtle)]'"
              class="relative w-10 h-6 rounded-full transition-colors"
            >
              <span
                :class="draftIsDark ? 'translate-x-4' : 'translate-x-0.5'"
                class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
              />
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-[var(--text-primary)]">Idioma</p>
              <p class="text-xs text-[var(--text-muted)]">Idioma de la interfaz</p>
            </div>
            <select
              v-model="draftLocale"
              class="px-3 py-1.5 text-sm bg-[var(--bg-panel)] border border-[var(--border-subtle)] rounded-lg text-[var(--text-primary)] focus:outline-none focus:border-[var(--teal)]"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
              <option value="fr">Français</option>
              <option value="de">Deutsch</option>
              <option value="pt">Português</option>
            </select>
          </div>
        </div>

        <div class="mt-5 flex justify-end gap-3 border-t border-[var(--border-subtle)] pt-4">
          <button
            @click="cancelPrefs"
            :disabled="!prefsDirty"
            class="px-4 py-2 text-sm font-medium border border-[var(--border-subtle)] text-[var(--text-secondary)] rounded-lg hover:bg-[var(--bg-panel)] transition-opacity disabled:opacity-40"
          >
            Cancelar
          </button>
          <button
            @click="savePrefs"
            :disabled="!prefsDirty || isSavingPrefs"
            class="px-4 py-2 text-sm font-semibold bg-[var(--teal)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {{ isSavingPrefs ? 'Guardando…' : 'Guardar preferencias' }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, type Ref } from 'vue'
import type { Theme } from '@/stores/theme'
import { useI18n } from 'vue-i18n'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useDialogStore } from '@/stores/dialog'
import { api } from '@/services/api'

const { locale } = useI18n()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const dialogStore = useDialogStore()

// Profile
const profile = reactive({
  firstName: '',
  lastName: '',
  email: '',
  specialty: '',
})
const isSavingProfile = ref(false)

// Password
const pwForm = reactive({ current: '', next: '', confirm: '' })
const showCurrent = ref(false)
const showNext = ref(false)
const showConfirm = ref(false)
const pwCurrentFocused = ref(false)
const pwNextFocused = ref(false)
const pwConfirmFocused = ref(false)
const isChangingPw = ref(false)
const pwError = ref('')
const pwSuccess = ref(false)

// Preferences — draft state: changes are previewed but not persisted until "Guardar"
const originalTheme: Ref<Theme> = ref(themeStore.getTheme())
const draftTheme: Ref<Theme> = ref(themeStore.getTheme())
const draftLocale = ref(locale.value)
const draftIsDark = computed(() => draftTheme.value === 'dark')
const prefsDirty = computed(
  () => draftTheme.value !== originalTheme.value || draftLocale.value !== locale.value
)
const isSavingPrefs = ref(false)

onMounted(async () => {
  try {
    await authStore.fetchMe()
  } catch (e) {
    console.error('Error loading user', e)
  }
  const user = authStore.user as any
  if (user) {
    const parts = (user.fullName || '').split(' ')
    profile.firstName = parts[0] || ''
    profile.lastName = parts.slice(1).join(' ') || ''
    profile.email = user.email || ''
    profile.specialty = user.specialty || (user as any).especialidad || ''
  }
})

async function saveProfile() {
  isSavingProfile.value = true
  try {
    await api.auth.updateProfile({
      full_name: `${profile.firstName} ${profile.lastName}`.trim(),
      specialty: profile.specialty,
    } as any)
    await authStore.fetchMe()
  } catch (e: any) {
    dialogStore.alert('Error al guardar: ' + (e.response?.data?.detail || e.message))
  } finally {
    isSavingProfile.value = false
  }
}

async function changePassword() {
  if (pwForm.next !== pwForm.confirm) return
  isChangingPw.value = true
  pwError.value = ''
  pwSuccess.value = false
  try {
    await api.auth.changePassword({
      oldPassword: pwForm.current,
      newPassword: pwForm.next,
    })
    pwForm.current = ''
    pwForm.next = ''
    pwForm.confirm = ''
    pwSuccess.value = true
    setTimeout(() => { pwSuccess.value = false }, 3000)
  } catch (e: any) {
    pwError.value = e.response?.data?.detail || 'Error al cambiar contraseña'
  } finally {
    isChangingPw.value = false
  }
}

function toggleThemeDraft() {
  draftTheme.value = draftTheme.value === 'dark' ? 'light' : 'dark'
  themeStore.previewTheme(draftTheme.value)
}

function cancelPrefs() {
  draftTheme.value = originalTheme.value
  draftLocale.value = locale.value
  themeStore.previewTheme(originalTheme.value)
}

async function savePrefs() {
  isSavingPrefs.value = true
  try {
    themeStore.applyTheme(draftTheme.value)
    originalTheme.value = draftTheme.value
    locale.value = draftLocale.value
    localStorage.setItem('corestream-locale', draftLocale.value)
  } finally {
    isSavingPrefs.value = false
  }
}
</script>
