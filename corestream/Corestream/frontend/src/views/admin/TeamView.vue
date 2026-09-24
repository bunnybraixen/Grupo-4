<!--
  Vista de Gestión de Equipos y Usuarios (Admin)
  Permite al Administrador:
  - Crear equipos de trabajo y asignar desarrolladores a los mismos.
  - Editar y eliminar equipos existentes.
  - Ver la lista de usuarios y gestionar sus roles y membresías de equipo.
-->
<template>
  <div class="p-8 max-w-6xl mx-auto text-[var(--text-primary)]">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold">Gestión de Equipos y Usuarios</h1>
        <p class="mt-2 text-sm text-[var(--text-muted)]">
          Crea equipos de trabajo, asigna desarrolladores y gestiona roles en CoreStream
        </p>
      </div>

      <button
        @click="openTeamModal()"
        class="px-4 py-2.5 rounded-xl bg-[var(--teal)] text-white hover:bg-[var(--teal-90)] font-medium text-sm flex items-center gap-2 shadow-sm"
      >
        <span>+</span> Crear Nuevo Equipo
      </button>
    </div>

    <!-- Modal Crear / Editar Equipo -->
    <div v-if="showTeamModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <h2 class="text-xl font-bold text-[var(--text-primary)]">
          {{ editingTeamId ? 'Editar Equipo' : 'Crear Nuevo Equipo' }}
        </h2>

        <div>
          <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-1">Nombre del equipo</label>
          <input
            v-model="teamForm.name"
            placeholder="Ej: Equipo Frontend, Equipo Backend..."
            class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 outline-none text-sm text-[var(--text-primary)]"
          />
        </div>

        <div>
          <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-1">Descripción</label>
          <textarea
            v-model="teamForm.description"
            rows="2"
            placeholder="Propósito u objetivo del equipo..."
            class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 outline-none text-sm text-[var(--text-primary)]"
          ></textarea>
        </div>

        <div>
          <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-2">Integrantes del Equipo</label>
          <div class="max-h-48 overflow-y-auto space-y-1.5 border border-[var(--border-subtle)] rounded-lg p-3 bg-[var(--bg-app)]">
            <div
              v-for="u in availableUsers"
              :key="u.email"
              class="flex items-center justify-between p-1.5 hover:bg-[var(--bg-card)] rounded transition-colors"
            >
              <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
                <input
                  type="checkbox"
                  :value="u.email.toLowerCase()"
                  v-model="teamForm.memberEmails"
                  class="rounded accent-[var(--teal)] h-4 w-4"
                />
                <span class="font-medium text-[var(--text-primary)]">{{ u.fullName || u.email }}</span>
                <span class="text-xs text-[var(--text-muted)]">({{ u.email }})</span>
              </label>
              <span class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-[var(--bg-card)] text-[var(--text-muted)] border border-[var(--border-subtle)]">
                {{ u.role }}
              </span>
            </div>
          </div>
        </div>

        <!-- Añadir usuario por correo si no está en lista -->
        <div>
          <label class="block text-xs uppercase tracking-[0.15em] text-[var(--text-muted)] mb-1">Agregar por correo (opcional)</label>
          <div class="flex gap-2">
            <input
              v-model="customEmail"
              @keyup.enter="addCustomEmail"
              placeholder="desarrollador@correo.com"
              class="flex-1 bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-1.5 text-sm outline-none"
            />
            <button
              @click="addCustomEmail"
              type="button"
              class="px-3 py-1.5 text-xs bg-[var(--teal)]/20 text-[var(--teal)] rounded-lg hover:bg-[var(--teal)]/30 font-medium"
            >
              Añadir
            </button>
          </div>
        </div>

        <p v-if="modalError" class="text-xs text-red-400 font-medium">{{ modalError }}</p>

        <div class="flex justify-end gap-2 pt-2">
          <button
            @click="closeTeamModal"
            class="px-4 py-2 rounded-lg text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)]"
          >
            Cancelar
          </button>
          <button
            @click="saveTeam"
            :disabled="!teamForm.name.trim()"
            class="px-4 py-2 rounded-lg text-sm bg-[var(--teal)] text-white hover:bg-[var(--teal-90)] disabled:opacity-50 font-medium"
          >
            Guardar Equipo
          </button>
        </div>
      </div>
    </div>

    <!-- Lista de Equipos -->
    <div class="mt-8 space-y-4">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <span>👥</span> Equipos de Trabajo Configurados ({{ teamsStore.teams.length }})
      </h2>

      <div v-if="teamsStore.teams.length === 0" class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-[var(--text-muted)]">
        No hay equipos creados. Haz clic en «+ Crear Nuevo Equipo» para empezar.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div
          v-for="team in teamsStore.teams"
          :key="team.id"
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 shadow-sm space-y-3 flex flex-col justify-between"
        >
          <div>
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="font-bold text-lg text-[var(--text-primary)] flex items-center gap-2">
                  <span class="inline-block h-3 w-3 rounded-full bg-[var(--teal)]"></span>
                  {{ team.name }}
                </h3>
                <p class="text-xs text-[var(--text-muted)] mt-1">
                  {{ team.description || 'Sin descripción' }}
                </p>
              </div>
              <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30">
                {{ team.memberEmails.length }} miembro{{ team.memberEmails.length === 1 ? '' : 's' }}
              </span>
            </div>

            <!-- Lista de Miembros en badges -->
            <div class="mt-4">
              <p class="text-[10px] uppercase tracking-[0.18em] text-[var(--text-muted)] mb-2 font-semibold">Integrantes:</p>
              <div v-if="team.memberEmails.length === 0" class="text-xs text-[var(--text-muted)] italic">
                Sin miembros asignados a este equipo.
              </div>
              <div v-else class="flex flex-wrap gap-1.5">
                <span
                  v-for="email in team.memberEmails"
                  :key="email"
                  class="px-2.5 py-1 rounded-lg text-xs bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] flex items-center gap-1.5"
                >
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                  {{ getUserNameByEmail(email) }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex gap-2 pt-3 border-t border-[var(--border-subtle)] justify-end">
            <button
              @click="openTeamModal(team)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--bg-app)] border border-[var(--border-subtle)] text-[var(--text-primary)] hover:border-[var(--teal)]"
            >
              ✏️ Editar
            </button>
            <button
              @click="confirmDeleteTeam(team)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20"
            >
              🗑 Eliminar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Usuarios del Sistema y Roles -->
    <div class="mt-10 space-y-4">
      <h2 class="text-xl font-bold flex items-center gap-2">
        <span>👤</span> Usuarios del Sistema ({{ systemUsers.length }})
      </h2>

      <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden shadow-sm">
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="border-b border-[var(--border-subtle)] bg-[var(--bg-app)] text-[var(--text-muted)] text-xs uppercase tracking-wider">
              <th class="p-3">Usuario / Nombre</th>
              <th class="p-3">Correo Electrónico</th>
              <th class="p-3">Rol Actual</th>
              <th class="p-3">Equipos Pertenecientes</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]">
            <tr v-for="u in systemUsers" :key="u.id" class="hover:bg-[var(--bg-app)]/50">
              <td class="p-3 font-medium text-[var(--text-primary)]">{{ u.fullName || u.email.split('@')[0] }}</td>
              <td class="p-3 text-[var(--text-muted)]">{{ u.email }}</td>
              <td class="p-3">
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  :class="{
                    'bg-purple-500/20 text-purple-300 border border-purple-500/30': u.role === 'ADMIN',
                    'bg-blue-500/20 text-blue-300 border border-blue-500/30': u.role === 'GROUP_LEADER',
                    'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30': u.role === 'DEVELOPER'
                  }"
                >
                  {{ u.role }}
                </span>
              </td>
              <td class="p-3">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="t in teamsStore.getUserTeams(u.email)"
                    :key="t.id"
                    class="px-2 py-0.5 rounded text-xs bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 font-medium"
                  >
                    {{ t.name }}
                  </span>
                  <span v-if="teamsStore.getUserTeams(u.email).length === 0" class="text-xs text-[var(--text-muted)]">
                    Sin equipo
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeamsStore, type Team } from '@/stores/teams'
import { api } from '@/services/api'
import type { User } from '@/types'

const teamsStore = useTeamsStore()
const systemUsers = ref<User[]>([])

const showTeamModal = ref(false)
const editingTeamId = ref<string | null>(null)
const teamForm = ref<{ name: string; description: string; memberEmails: string[] }>({
  name: '',
  description: '',
  memberEmails: []
})
const customEmail = ref('')
const modalError = ref('')

const defaultUsers: User[] = [
  { id: '1', email: 'admin@corestream.com', fullName: 'Administrador Principal', role: 'ADMIN' as any, isActive: true },
  { id: '2', email: 'dev@corestream.com', fullName: 'Dev Tester', role: 'DEVELOPER' as any, isActive: true },
  { id: '3', email: 'leader@corestream.com', fullName: 'Líder de Proyecto', role: 'GROUP_LEADER' as any, isActive: true },
  { id: '4', email: 'developer@corestream.com', fullName: 'Desarrollador Web', role: 'DEVELOPER' as any, isActive: true }
]

const availableUsers = ref<User[]>([...defaultUsers])

const loadUsers = async () => {
  try {
    const res: any = await api.users.list({ limit: 100 })
    const fetched = Array.isArray(res) ? res : (res?.items ?? res?.data ?? [])
    if (fetched.length) {
      systemUsers.value = fetched
      // Combinar con defaultUsers si no están en fetched
      const mergedMap = new Map<string, User>()
      for (const u of [...defaultUsers, ...fetched]) {
        mergedMap.set(u.email.toLowerCase(), u)
      }
      availableUsers.value = Array.from(mergedMap.values())
    } else {
      systemUsers.value = defaultUsers
      availableUsers.value = defaultUsers
    }
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    systemUsers.value = defaultUsers
    availableUsers.value = defaultUsers
  }
}

const getUserNameByEmail = (email: string): string => {
  const found = availableUsers.value.find((u) => u.email.toLowerCase() === email.toLowerCase())
  return found?.fullName || email
}

const openTeamModal = (team?: Team) => {
  modalError.value = ''
  if (team) {
    editingTeamId.value = team.id
    teamForm.value = {
      name: team.name,
      description: team.description || '',
      memberEmails: [...team.memberEmails]
    }
  } else {
    editingTeamId.value = null
    teamForm.value = {
      name: '',
      description: '',
      memberEmails: []
    }
  }
  showTeamModal.value = true
}

const closeTeamModal = () => {
  showTeamModal.value = false
  editingTeamId.value = null
  customEmail.value = ''
  modalError.value = ''
}

const addCustomEmail = () => {
  const email = customEmail.value.trim().toLowerCase()
  if (!email) return
  if (!teamForm.value.memberEmails.includes(email)) {
    teamForm.value.memberEmails.push(email)
  }
  customEmail.value = ''
}

const saveTeam = () => {
  const name = teamForm.value.name.trim()
  if (!name) {
    modalError.value = 'El nombre del equipo es obligatorio.'
    return
  }

  if (editingTeamId.value) {
    teamsStore.updateTeam(editingTeamId.value, {
      name,
      description: teamForm.value.description,
      memberEmails: teamForm.value.memberEmails
    })
  } else {
    teamsStore.createTeam(name, teamForm.value.description, teamForm.value.memberEmails)
  }

  closeTeamModal()
}

const confirmDeleteTeam = (team: Team) => {
  if (window.confirm(`¿Estás seguro de eliminar el equipo "${team.name}"?`)) {
    teamsStore.deleteTeam(team.id)
  }
}

onMounted(() => {
  teamsStore.loadFromStorage()
  loadUsers()
})
</script>
