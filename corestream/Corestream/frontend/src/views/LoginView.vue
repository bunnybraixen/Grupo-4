<!--
  Login contra la API /api/auth/login. Guarda tokens y rol en localStorage
  para el router; sincroniza axios con setAuthTokens.
-->
<template>
  <div
    class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-300"
    :class="isDark
      ? 'bg-[#0A1A20]'
      : 'bg-gradient-to-br from-[#E6F8F7] via-[#F7FDED] to-[#CDF1F0]'"
  >
    <!-- Controles de esquina superior derecha: idioma + dark mode -->
    <div class="absolute top-4 right-4 flex items-center gap-2">
      <!-- Selector de idioma -->
      <div class="relative">
        <button
          @click="showLangMenu = !showLangMenu"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-sm font-medium transition-colors"
          :class="isDark
            ? 'bg-[#142730] text-[#A1A9AC] hover:text-white border border-[#2A4A55]'
            : 'bg-white/80 text-[#5A686E] hover:text-[#142730] border border-[#D0D4D6]'"
        >
          <span>{{ langFlags[currentLocale] }}</span>
          <span class="hidden sm:inline">{{ langNames[currentLocale] }}</span>
          <span class="text-xs opacity-60">▾</span>
        </button>
        <div
          v-if="showLangMenu"
          class="absolute right-0 top-full mt-1 rounded-xl shadow-lg border overflow-hidden z-50 min-w-[140px]"
          :class="isDark ? 'bg-[#142730] border-[#2A4A55]' : 'bg-white border-[#D0D4D6]'"
        >
          <button
            v-for="(name, code) in langNames"
            :key="code"
            @click="setLocale(code)"
            class="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-left transition-colors"
            :class="[
              currentLocale === code
                ? 'bg-[#06B7B2]/10 text-[#06B7B2] font-semibold'
                : isDark ? 'text-[#A1A9AC] hover:bg-[#1E3A45]' : 'text-[#5A686E] hover:bg-[#F0F9F9]'
            ]"
          >
            <span>{{ langFlags[code] }}</span>
            {{ name }}
          </button>
        </div>
        <!-- Overlay cierre -->
        <div v-if="showLangMenu" class="fixed inset-0 z-40" @click="showLangMenu = false" />
      </div>

      <!-- Toggle dark mode -->
      <button
        @click="toggleDark"
        class="w-9 h-9 rounded-xl flex items-center justify-center text-base transition-colors border"
        :class="isDark
          ? 'bg-[#142730] text-yellow-400 border-[#2A4A55] hover:bg-[#1E3A45]'
          : 'bg-white/80 text-[#5A686E] border-[#D0D4D6] hover:bg-white hover:text-[#142730]'"
        :title="isDark ? t('login.lightMode') : t('login.darkMode')"
      >
        <!-- Sol (modo claro activo → muestra luna) -->
        <svg v-if="!isDark" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
        </svg>
        <!-- Luna (modo oscuro activo → muestra sol) -->
        <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <div class="max-w-md w-full">
      <!-- Header con logo y títulos -->
      <div class="text-center mb-8">
        <div class="flex justify-center mb-6">
          <img
            :src="logoUrl"
            alt="CoreStream"
            class="w-40 h-auto rounded-xl object-contain shadow-lg"
          />
        </div>
        <h1 class="text-3xl font-bold mb-2 transition-colors" :class="isDark ? 'text-white' : 'text-[#142730]'">
          CoreStream
        </h1>
        <p class="text-sm transition-colors" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
          {{ t('login.subtitle') }}
        </p>
      </div>

      <!-- Card del formulario -->
      <form
        class="rounded-2xl p-10 space-y-5 transition-colors duration-300"
        :class="isDark
          ? 'bg-[#142730] shadow-[0_20px_60px_rgba(0,0,0,0.4)]'
          : 'bg-white shadow-[0_20px_60px_rgba(6,183,178,0.15),0_4px_16px_rgba(0,0,0,0.08)]'"
        @submit.prevent="onSubmit"
      >
        <!-- Campo Email -->
        <div>
          <label for="email" class="block text-sm font-medium mb-2 transition-colors" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
            {{ t('login.email') }}
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="w-full rounded-xl border px-4 py-3 text-sm placeholder-[#A1A9AC] focus:outline-none focus:ring-2 transition-all"
            :class="isDark
              ? 'bg-[#0A1A20] border-[#2A4A55] text-white focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'
              : 'bg-white border-[#D0D4D6] text-[#142730] focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'"
            :placeholder="t('login.emailPlaceholder')"
          />
        </div>

        <!-- Campo Contraseña -->
        <div>
          <label for="password" class="block text-sm font-medium mb-2 transition-colors" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
            {{ t('login.password') }}
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              class="w-full rounded-xl border px-4 py-3 pr-12 text-sm placeholder-[#A1A9AC] focus:outline-none focus:ring-2 transition-all"
              :class="isDark
                ? 'bg-[#0A1A20] border-[#2A4A55] text-white focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'
                : 'bg-white border-[#D0D4D6] text-[#142730] focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'"
              :placeholder="t('login.passwordPlaceholder')"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-[#A1A9AC] hover:text-[#5A686E] transition-colors"
              :title="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            >
              <!-- Ojo abierto (contraseña visible) -->
              <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <!-- Ojo tachado (contraseña oculta) -->
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Mensaje de error -->
        <p v-if="errorMessage" class="text-sm text-[#DC2626] bg-[#FEE2E2] px-4 py-3 rounded-lg">
          {{ errorMessage }}
        </p>

        <!-- Botón Ingresar -->
        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full py-3 px-4 rounded-xl bg-[#ADEA4B] text-[#142730] text-base font-bold hover:bg-[#B5EC5D] active:bg-[#BDEE6F] disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center gap-2"
        >
          <Icon v-if="authStore.isLoading" icon="mdi:loading" class="animate-spin text-lg" />
          {{ authStore.isLoading ? t('login.submitting') : t('login.submit') }}
        </button>
      </form>

      <!-- Footer -->
      <p class="text-xs text-center mt-8 transition-colors" :class="isDark ? 'text-[#2A4A55]' : 'text-[#A1A9AC]'">
        {{ t('login.footer', { year: new Date().getFullYear() }) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores'
import { UserRole } from '@/types'
import logoUrl from '@/assets/logo-corestream.jpeg'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const i18n = useI18n()
const { t } = i18n

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const showLangMenu = ref(false)

const errorMessage = computed(() => authStore.error)
const isDark = computed(() => themeStore.isDark())

const currentLocale = computed<string>(() => i18n.locale.value)

const langFlags: Record<string, string> = { es: '🇪🇸', en: '🇬🇧', pt: '🇵🇹', fr: '🇫🇷', de: '🇩🇪' }
const langNames: Record<string, string> = { es: 'Español', en: 'English', pt: 'Português', fr: 'Français', de: 'Deutsch' }

function setLocale(code: string) {
  i18n.locale.value = code
  localStorage.setItem('corestream-locale', code)
  showLangMenu.value = false
}

function toggleDark() {
  themeStore.toggleTheme()
}

async function onSubmit() {
  try {
    await authStore.login(email.value.trim(), password.value)
    const user = authStore.user
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
    if (redirect && redirect.startsWith('/')) {
      await router.replace(redirect)
      return
    }
    if (user?.role === UserRole.ADMIN) {
      await router.replace({ path: '/admin/builder' })
    } else {
      await router.replace({ path: '/dev/workbench' })
    }
  } catch {
    /* mensaje en store */
  }
}
</script>
