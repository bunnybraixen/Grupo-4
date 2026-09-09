<!--
  Página pública de aceptación de invitación (plan 3.7).
  Sustituye al registro público: el invitado llega con un enlace de un solo
  uso (/invite/:token), ve a qué se está uniendo, y elige su propia
  contraseña. No requiere sesión.
-->
<template>
  <div
    class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-300"
    :class="isDark
      ? 'bg-[#0A1A20]'
      : 'bg-gradient-to-br from-[#E6F8F7] via-[#F7FDED] to-[#CDF1F0]'"
  >
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold" :class="isDark ? 'text-white' : 'text-[#142730]'">CoreStream</h1>
      </div>

      <div
        class="rounded-2xl p-10 space-y-5 transition-colors duration-300"
        :class="isDark
          ? 'bg-[#142730] shadow-[0_20px_60px_rgba(0,0,0,0.4)]'
          : 'bg-white shadow-[0_20px_60px_rgba(6,183,178,0.15),0_4px_16px_rgba(0,0,0,0.08)]'"
      >
        <!-- Cargando la info de la invitación -->
        <div v-if="loadingInfo" class="text-center py-6" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
          Comprobando invitación...
        </div>

        <!-- Invitación inválida, caducada o ya usada -->
        <div v-else-if="invitationError" class="text-center space-y-4">
          <p class="text-sm text-[#DC2626] bg-[#FEE2E2] px-4 py-3 rounded-lg">
            {{ invitationError }}
          </p>
          <router-link to="/login" class="text-sm underline" :class="isDark ? 'text-[#06B7B2]' : 'text-[#0891B2]'">
            Ir a iniciar sesión
          </router-link>
        </div>

        <!-- Cuenta creada -->
        <div v-else-if="accepted" class="text-center space-y-4">
          <p class="text-sm" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
            Cuenta creada correctamente. Ya puedes iniciar sesión.
          </p>
          <router-link
            to="/login"
            class="inline-block w-full py-3 px-4 rounded-xl bg-[#ADEA4B] text-[#142730] text-base font-bold hover:bg-[#B5EC5D] transition-colors duration-200"
          >
            Ir a iniciar sesión
          </router-link>
        </div>

        <!-- Formulario de aceptación -->
        <form v-else @submit.prevent="onSubmit" class="space-y-5">
          <div class="text-sm" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
            Fuiste invitado con <strong>{{ invitation?.email }}</strong> como
            <strong>{{ roleLabel }}</strong>.
          </div>

          <div>
            <label class="block text-sm font-medium mb-2" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
              Nombre completo
            </label>
            <input
              v-model="fullName"
              type="text"
              required
              class="w-full rounded-xl border px-4 py-3 text-sm focus:outline-none focus:ring-2 transition-all"
              :class="isDark
                ? 'bg-[#0A1A20] border-[#2A4A55] text-white focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'
                : 'bg-white border-[#D0D4D6] text-[#142730] focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
              Contraseña
            </label>
            <input
              v-model="password"
              type="password"
              required
              minlength="8"
              autocomplete="new-password"
              class="w-full rounded-xl border px-4 py-3 text-sm focus:outline-none focus:ring-2 transition-all"
              :class="isDark
                ? 'bg-[#0A1A20] border-[#2A4A55] text-white focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'
                : 'bg-white border-[#D0D4D6] text-[#142730] focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2" :class="isDark ? 'text-[#A1A9AC]' : 'text-[#5A686E]'">
              Confirmar contraseña
            </label>
            <input
              v-model="passwordConfirm"
              type="password"
              required
              minlength="8"
              autocomplete="new-password"
              class="w-full rounded-xl border px-4 py-3 text-sm focus:outline-none focus:ring-2 transition-all"
              :class="isDark
                ? 'bg-[#0A1A20] border-[#2A4A55] text-white focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'
                : 'bg-white border-[#D0D4D6] text-[#142730] focus:border-[#06B7B2] focus:ring-[#06B7B2]/20'"
            />
          </div>

          <p v-if="formError" class="text-sm text-[#DC2626] bg-[#FEE2E2] px-4 py-3 rounded-lg">
            {{ formError }}
          </p>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full py-3 px-4 rounded-xl bg-[#ADEA4B] text-[#142730] text-base font-bold hover:bg-[#B5EC5D] disabled:opacity-50 transition-colors duration-200"
          >
            {{ submitting ? 'Creando cuenta...' : 'Crear cuenta' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores'
import api from '@/services/api'

const route = useRoute()
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark())

const token = computed(() => String(route.params.token ?? ''))

const loadingInfo = ref(true)
const invitationError = ref<string | null>(null)
const invitation = ref<{ email: string; role: string } | null>(null)

const fullName = ref('')
const password = ref('')
const passwordConfirm = ref('')
const submitting = ref(false)
const formError = ref<string | null>(null)
const accepted = ref(false)

const roleLabel = computed(() => {
  const labels: Record<string, string> = {
    ADMIN: 'Administrador',
    TEAM_LEADER: 'Líder de Equipo',
    DEVELOPER: 'Desarrollador',
  }
  return invitation.value ? (labels[invitation.value.role] ?? invitation.value.role) : ''
})

onMounted(async () => {
  try {
    const info = await api.invitations.getInfo(token.value)
    if (info.isUsed) {
      invitationError.value = 'Esta invitación ya fue usada.'
    } else if (info.isExpired) {
      invitationError.value = 'Esta invitación ha caducado. Pide al administrador que genere una nueva.'
    } else {
      invitation.value = { email: info.email, role: info.role }
    }
  } catch {
    invitationError.value = 'Invitación no encontrada. Revisa el enlace.'
  } finally {
    loadingInfo.value = false
  }
})

const onSubmit = async () => {
  formError.value = null

  if (password.value !== passwordConfirm.value) {
    formError.value = 'Las contraseñas no coinciden'
    return
  }
  if (password.value.length < 8) {
    formError.value = 'La contraseña debe tener mínimo 8 caracteres'
    return
  }

  submitting.value = true
  try {
    await api.invitations.accept(token.value, {
      fullName: fullName.value.trim(),
      password: password.value,
    })
    accepted.value = true
  } catch (err: any) {
    formError.value = err?.response?.data?.detail || 'No se pudo crear la cuenta'
  } finally {
    submitting.value = false
  }
}
</script>
