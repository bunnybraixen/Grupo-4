<!--
  Vista de Gestión de Equipos — Team Leader (GROUP_LEADER)
  - Ve los equipos a los que pertenece
  - Lista todos los usuarios del sistema
  - Permite al team leader agregar / quitar usuarios de sus propios equipos
-->
<template>
  <div class="p-8 max-w-5xl mx-auto text-[var(--text-primary)] space-y-10">

    <!-- ============================================================ -->
    <!-- HEADER                                                       -->
    <!-- ============================================================ -->
    <div>
      <h1 class="text-3xl font-bold">Asignación de Equipo</h1>
      <p class="mt-2 text-sm text-[var(--text-muted)]">
        Gestiona los integrantes de los equipos que lideras.
        <span class="font-mono text-[var(--teal)] text-xs ml-2">📧 {{ userEmail }}</span>
      </p>
    </div>

    <!-- ============================================================ -->
    <!-- MIS EQUIPOS                                                  -->
    <!-- ============================================================ -->
    <div class="space-y-4">
      <h2 class="text-xl font-bold flex items-center gap-2">
        👥 Mis Equipos ({{ myTeams.length }})
      </h2>

      <div v-if="myTeams.length === 0"
        class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-[var(--text-muted)]">
        <p class="font-medium">No tienes equipos asignados actualmente.</p>
        <p class="text-xs mt-1">Pídele al Administrador que te agregue a un equipo en el panel de administración.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="team in myTeams" :key="team.id"
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 shadow-sm space-y-4">

          <!-- Cabecera del equipo -->
          <div class="flex items-start justify-between gap-2">
            <div>
              <h3 class="font-bold text-lg flex items-center gap-2">
                <span class="inline-block h-3 w-3 rounded-full bg-[var(--teal)]"></span>
                {{ team.name }}
              </h3>
              <p class="text-xs text-[var(--text-muted)] mt-1">{{ team.description || 'Sin descripción' }}</p>
            </div>
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 flex-shrink-0">
              {{ team.memberEmails.length }} miembro{{ team.memberEmails.length === 1 ? '' : 's' }}
            </span>
          </div>

          <!-- Miembros actuales con botón de quitar -->
          <div>
            <p class="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2 font-semibold">Integrantes actuales:</p>
            <div v-if="team.memberEmails.length === 0" class="text-xs text-[var(--text-muted)] italic">Sin miembros.</div>
            <div v-else class="flex flex-wrap gap-1.5">
              <span
                v-for="email in team.memberEmails"
                :key="email"
                class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs bg-[var(--bg-app)] border border-[var(--border-subtle)]"
              >
                <span class="w-2 h-2 rounded-full bg-emerald-400 flex-shrink-0"></span>
                <span>{{ getUserName(email) }}</span>
                <!-- No permitir quitarse a sí mismo si es el líder -->
                <button
                  v-if="email.toLowerCase() !== userEmail.toLowerCase()"
                  @click="removeMember(team, email)"
                  class="ml-1 text-red-400 hover:text-red-300 text-[11px] font-bold leading-none cursor-pointer"
                  title="Quitar del equipo"
                >✕</button>
              </span>
            </div>
          </div>

          <!-- Agregar usuario al equipo -->
          <div class="border-t border-[var(--border-subtle)] pt-3 space-y-2">
            <p class="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-semibold">Agregar usuario al equipo:</p>
            
            <!-- Buscador para filtrar opciones de usuario -->
            <input
              v-model="memberSearchQuery[team.id]"
              placeholder="🔍 Buscar por nombre o correo…"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[var(--teal)]"
            />

            <div class="flex gap-2">
              <select
                v-model="addMemberSelect[team.id]"
                class="flex-1 bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[var(--teal)] text-[var(--text-primary)]"
              >
                <option value="">— Seleccionar usuario ({{ usersNotInTeamFiltered(team).length }} disponibles) —</option>
                <option
                  v-for="u in usersNotInTeamFiltered(team)"
                  :key="u.id || u.email"
                  :value="u.email"
                >
                  {{ u.fullName || u.email }} ({{ u.email }})
                </option>
              </select>
              <button
                :disabled="!addMemberSelect[team.id]"
                @click="addMember(team)"
                class="px-3 py-1.5 rounded-lg text-xs bg-[var(--teal)]/20 text-[var(--teal)] border border-[var(--teal)]/40 hover:bg-[var(--teal)]/30 disabled:opacity-40 font-medium"
              >
                Agregar
              </button>
            </div>
            <!-- Agregar por correo manual -->
            <div class="flex gap-2">
              <input
                v-model="customEmailInput[team.id]"
                @keyup.enter="addCustomMember(team)"
                placeholder="o escribir correo manual…"
                class="flex-1 bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[var(--teal)]"
              />
              <button
                :disabled="!customEmailInput[team.id]?.trim()"
                @click="addCustomMember(team)"
                class="px-3 py-1.5 rounded-lg text-xs bg-[var(--bg-app)] border border-[var(--border-subtle)] hover:border-[var(--teal)] disabled:opacity-40 font-medium"
              >
                Añadir
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================ -->
    <!-- TODOS LOS USUARIOS DEL SISTEMA                               -->
    <!-- ============================================================ -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold flex items-center gap-2">
          👤 Usuarios del Sistema ({{ allUsers.length }})
        </h2>
        <button @click="loadAllUsers" class="text-xs text-[var(--teal)] border border-[var(--teal)]/40 px-3 py-1.5 rounded-lg hover:bg-[var(--teal)]/10">
          ↻ Recargar
        </button>
      </div>

      <div v-if="loadingUsers" class="text-sm text-[var(--text-muted)] py-4 text-center">Cargando usuarios…</div>

      <div v-else class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] overflow-hidden shadow-sm">
        <table class="w-full text-left text-sm border-collapse">
          <thead>
            <tr class="border-b border-[var(--border-subtle)] bg-[var(--bg-app)] text-[var(--text-muted)] text-xs uppercase tracking-wider">
              <th class="p-3">Nombre</th>
              <th class="p-3">Correo</th>
              <th class="p-3">Rol</th>
              <th class="p-3">Equipos asignados</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]">
            <tr v-for="u in allUsers" :key="u.id || u.email" class="hover:bg-[var(--bg-app)]/40">
              <td class="p-3 font-medium">{{ u.fullName || u.email.split('@')[0] }}</td>
              <td class="p-3 text-[var(--text-muted)]">{{ u.email }}</td>
              <td class="p-3">
                <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  :class="{
                    'bg-purple-500/20 text-purple-300 border border-purple-500/30': u.role === 'ADMIN',
                    'bg-blue-500/20 text-blue-300 border border-blue-500/30': u.role === 'GROUP_LEADER',
                    'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30': u.role === 'DEVELOPER'
                  }">{{ u.role }}</span>
              </td>
              <td class="p-3">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="t in teamsStore.getUserTeams(u.email)"
                    :key="t.id"
                    class="px-2 py-0.5 rounded text-xs bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 font-medium"
                  >{{ t.name }}</span>
                  <span v-if="teamsStore.getUserTeams(u.email).length === 0" class="text-xs text-[var(--text-muted)]">—</span>
                </div>
              </td>
            </tr>
            <tr v-if="allUsers.length === 0">
              <td colspan="4" class="p-6 text-center text-[var(--text-muted)] text-sm">No hay usuarios disponibles.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore, type Team } from '@/stores/teams'
import { api } from '@/services/api'
import type { User } from '@/types'

const authStore = useAuthStore()
const teamsStore = useTeamsStore()

const userEmail = computed(() =>
  (authStore.user?.email || localStorage.getItem('userEmail') || '').toLowerCase()
)

// ── Mis equipos (en los que estoy registrado como miembro) ───────
const myTeams = computed(() => teamsStore.getUserTeams(userEmail.value))

// ── Todos los usuarios del sistema ────────────────────────────────
const allUsers = ref<User[]>([])
const loadingUsers = ref(false)

// ── Estado de los formularios por cada equipo ────────────────────
const addMemberSelect = ref<Record<string, string>>({})
const customEmailInput = ref<Record<string, string>>({})
const memberSearchQuery = ref<Record<string, string>>({})

// ── Parsear respuesta de api.users.list ───────────────────────────
const parseUserList = (res: any): User[] => {
  let list: any[] = []
  if (Array.isArray(res)) list = res
  else if (Array.isArray(res?.items)) list = res.items
  else if (Array.isArray(res?.data?.items)) list = res.data.items
  else if (Array.isArray(res?.data)) list = res.data
  return list.map((u: any) => ({
    ...u,
    id: String(u.id),
    email: u.email,
    fullName: u.fullName || u.full_name || '',
    role: u.role,
    isActive: u.isActive ?? u.is_active ?? true
  }))
}

const loadAllUsers = async () => {
  loadingUsers.value = true
  try {
    const res: any = await api.users.list({ limit: 100 })
    allUsers.value = parseUserList(res)
  } catch (err) {
    console.error('Error cargando usuarios en team assignment:', err)
    allUsers.value = []
  } finally {
    loadingUsers.value = false
  }
}

const getUserName = (email: string): string => {
  const found = allUsers.value.find((u) => u.email.toLowerCase() === email.toLowerCase())
  return found?.fullName || email
}

// Usuarios que NO están ya en el equipo para el dropdown
const usersNotInTeam = (team: Team): User[] =>
  allUsers.value.filter(
    (u) => !team.memberEmails.some((e) => e.toLowerCase() === u.email.toLowerCase())
  )

// Filtrados por el buscador por equipo
const usersNotInTeamFiltered = (team: Team): User[] => {
  const notInTeam = usersNotInTeam(team)
  const query = (memberSearchQuery.value[team.id] || '').trim().toLowerCase()
  if (!query) return notInTeam
  return notInTeam.filter((u) =>
    (u.fullName || '').toLowerCase().includes(query) ||
    (u.email || '').toLowerCase().includes(query)
  )
}

// ── Agregar miembro con selector ──────────────────────────────────
const addMember = (team: Team) => {
  const email = (addMemberSelect.value[team.id] || '').trim().toLowerCase()
  if (!email) return
  const existing = team.memberEmails.map((e) => e.toLowerCase())
  if (!existing.includes(email)) {
    teamsStore.updateTeam(team.id, {
      memberEmails: [...team.memberEmails, email]
    })
  }
  addMemberSelect.value[team.id] = ''
}

// ── Agregar miembro por correo custom ────────────────────────────
const addCustomMember = (team: Team) => {
  const email = (customEmailInput.value[team.id] || '').trim().toLowerCase()
  if (!email) return
  const existing = team.memberEmails.map((e) => e.toLowerCase())
  if (!existing.includes(email)) {
    teamsStore.updateTeam(team.id, {
      memberEmails: [...team.memberEmails, email]
    })
  }
  customEmailInput.value[team.id] = ''
}

// ── Quitar miembro ────────────────────────────────────────────────
const removeMember = (team: Team, email: string) => {
  teamsStore.updateTeam(team.id, {
    memberEmails: team.memberEmails.filter((e) => e.toLowerCase() !== email.toLowerCase())
  })
}

onMounted(() => {
  teamsStore.loadFromStorage()
  loadAllUsers()
})
</script>
