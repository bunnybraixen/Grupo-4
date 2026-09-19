<!--
  Vista de login para CoreStream

  Proporciona formulario de autenticación.
  Usuarios pueden ingresar con correo y contraseña.
  Después de login exitoso, se redirige al dashboard apropriado.
-->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Encabezado -->
      <div class="text-center">
        <h1 class="text-4xl font-bold text-primary">CoreStream</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">
          Plataforma de Gestión de Proyectos
        </p>
      </div>

      <!-- Formulario de login -->
      <form
        class="bg-white dark:bg-gray-800 rounded-lg shadow p-8 space-y-4"
        @submit.prevent="handleSubmit"
      >
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Correo Electrónico
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            autocomplete="username"
            placeholder="tu-correo@empresa.com"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-gray-900 dark:text-gray-100 outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Contraseña
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 px-3 py-2 text-gray-900 dark:text-gray-100 outline-none focus:border-blue-500"
          />
        </div>

        <!-- Mensaje de error -->
        <p v-if="errorMessage" class="text-sm text-red-500" role="alert">
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium rounded-lg px-4 py-2 transition-colors"
        >
          {{ isSubmitting ? 'Iniciando sesión…' : 'Iniciar Sesión' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Lógica del componente LoginView
 *
 * Autentica contra el backend (POST /api/auth/login) a través del store de
 * auth, que deja el access token activo en el cliente HTTP y persistido en
 * localStorage. Sin este formulario, la SPA no tenía NINGUNA forma de obtener
 * token: cualquier ruta protegida acababa en 403 al llamar a la API.
 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

const handleSubmit = async (): Promise<void> => {
  if (isSubmitting.value) return

  errorMessage.value = ''
  isSubmitting.value = true

  try {
    const user = await authStore.login(email.value.trim(), password.value)

    // Datos usados por el guard del router y la directiva de permisos
    localStorage.setItem('userRole', user.role)
    localStorage.setItem('userId', user.id)
    localStorage.setItem('userName', user.fullName ?? '')

    // Destino: el que pidió el guard (?redirect=) o el panel según el rol
    const redirect = route.query.redirect
    const target =
      typeof redirect === 'string' && redirect
        ? redirect
        : user.role === 'ADMIN'
          ? '/admin/builder'
          : '/dev/workbench'

    await router.replace(target)
  } catch (err: any) {
    const status = err?.response?.status
    errorMessage.value =
      status === 401
        ? 'Correo o contraseña incorrectos'
        : status === 429
          ? 'Demasiados intentos. Espera unos minutos e inténtalo de nuevo.'
          : err?.response?.data?.detail ?? 'No se pudo iniciar sesión'
  } finally {
    isSubmitting.value = false
  }
}
</script>
