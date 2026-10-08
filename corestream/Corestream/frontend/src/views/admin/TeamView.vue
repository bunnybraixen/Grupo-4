<!--
  Vista de Gestión de Equipos y Usuarios (Admin)
  - Crear / editar / eliminar equipos (con modal de confirmación propio)
  - Crear usuarios nuevos con roles
  - Editar usuarios existentes (nombre, correo, rol)
  - Ver tabla de todos los usuarios del sistema
-->
<template>
  <div class="p-8 max-w-6xl mx-auto text-[var(--text-primary)] space-y-10">

    <!-- ====================================================== -->
    <!-- HEADER                                                 -->
    <!-- ====================================================== -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold">Gestión de Equipos y Usuarios</h1>
        <p class="mt-2 text-sm text-[var(--text-muted)]">
          Crea equipos, asigna desarrolladores y gestiona usuarios del sistema
        </p>
      </div>
      <button @click="openTeamModal()"
        class="px-4 py-2.5 rounded-xl bg-[var(--teal)] text-white hover:opacity-90 font-medium text-sm flex items-center gap-2 shadow-sm">
        + Crear Nuevo Equipo
      </button>
    </div>

    <!-- ====================================================== -->
    <!-- MODAL CREAR / EDITAR EQUIPO                            -->
    <!-- ====================================================== -->
    <div v-if="showTeamModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <h2 class="text-xl font-bold">{{ editingTeamId ? 'Editar Equipo' : 'Crear Nuevo Equipo' }}</h2>

        <div>
          <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Nombre del equipo</label>
          <input v-model="teamForm.name" placeholder="Ej: Equipo Frontend…"
            class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 outline-none text-sm focus:border-[var(--teal)]" />
        </div>

        <div>
          <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Descripción</label>
          <textarea v-model="teamForm.description" rows="2" placeholder="Propósito del equipo…"
            class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 outline-none text-sm focus:border-[var(--teal)]"></textarea>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)]">Integrantes</label>
            <span class="text-xs text-[var(--text-muted)]">{{ teamForm.memberEmails.length }} seleccionados</span>
          </div>
          <!-- Buscador de integrantes -->
          <input
            v-model="teamMemberSearch"
            placeholder="🔍 Buscar integrante por nombre o correo…"
            class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-2.5 py-1.5 mb-2 text-xs outline-none focus:border-[var(--teal)]"
          />
          <div class="max-h-48 overflow-y-auto space-y-1.5 border border-[var(--border-subtle)] rounded-lg p-3 bg-[var(--bg-app)]">
            <div v-for="u in filteredAvailableUsers" :key="u.email"
              class="flex items-center justify-between p-1.5 hover:bg-[var(--bg-card)] rounded">
              <label class="flex items-center gap-2 text-sm cursor-pointer select-none">
                <input type="checkbox" :value="u.email.toLowerCase()" v-model="teamForm.memberEmails"
                  class="rounded accent-[var(--teal)] h-4 w-4" />
                <span class="font-medium">{{ u.fullName || u.email }}</span>
                <span class="text-xs text-[var(--text-muted)]">({{ u.email }})</span>
              </label>
              <span class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-[var(--bg-card)] text-[var(--text-muted)] border border-[var(--border-subtle)]">{{ u.role }}</span>
            </div>
            <div v-if="filteredAvailableUsers.length === 0" class="text-xs text-[var(--text-muted)] py-2 text-center">
              No se encontraron usuarios
            </div>
          </div>
        </div>

        <div>
          <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Agregar por correo (opcional)</label>
          <div class="flex gap-2">
            <input v-model="customEmail" @keyup.enter="addCustomEmail" placeholder="desarrollador@correo.com"
              class="flex-1 bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg px-3 py-1.5 text-sm outline-none focus:border-[var(--teal)]" />
            <button @click="addCustomEmail" type="button"
              class="px-3 py-1.5 text-xs bg-[var(--teal)]/20 text-[var(--teal)] rounded-lg hover:bg-[var(--teal)]/30 font-medium">Añadir</button>
          </div>
        </div>

        <p v-if="modalError" class="text-xs text-red-400 font-medium">{{ modalError }}</p>

        <div class="flex justify-end gap-2 pt-2">
          <button @click="closeTeamModal" class="px-4 py-2 rounded-lg text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)]">Cancelar</button>
          <button @click="saveTeam" :disabled="!teamForm.name.trim()"
            class="px-4 py-2 rounded-lg text-sm bg-[var(--teal)] text-white hover:opacity-90 disabled:opacity-50 font-medium">Guardar Equipo</button>
        </div>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- MODAL CONFIRMAR ELIMINAR EQUIPO                        -->
    <!-- ====================================================== -->
    <div v-if="teamToDelete" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div class="bg-[var(--bg-card)] border border-red-500/30 rounded-2xl max-w-sm w-full p-6 shadow-2xl space-y-4">
        <h2 class="text-lg font-bold text-red-400">🗑 Eliminar Equipo</h2>
        <p class="text-sm text-[var(--text-muted)]">
          ¿Eliminar el equipo <span class="font-semibold text-[var(--text-primary)]">{{ teamToDelete.name }}</span>?
          Los proyectos asignados a este equipo quedarán sin equipo asignado.
        </p>
        <div class="flex justify-end gap-2">
          <button @click="teamToDelete = null" class="px-4 py-2 rounded-lg text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)]">Cancelar</button>
          <button @click="doDeleteTeam" class="px-4 py-2 rounded-lg text-sm bg-red-600 text-white hover:bg-red-700 font-medium">Sí, eliminar</button>
        </div>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- MODAL EDITAR USUARIO                                   -->
    <!-- ====================================================== -->
    <div v-if="editingUser" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div class="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
        <h2 class="text-xl font-bold">✏️ Editar Usuario</h2>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Nombre completo</label>
            <input v-model="editUserForm.fullName" placeholder="Nombre Apellido"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Correo electrónico</label>
            <input v-model="editUserForm.email" type="email"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Nueva contraseña <span class="text-[var(--text-muted)] normal-case text-[10px]">(opcional)</span></label>
            <input v-model="editUserForm.password" type="password" placeholder="Mínimo 8 caracteres…"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Rol</label>
            <select v-model="editUserForm.role"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]">
              <option value="DEVELOPER">Developer</option>
              <option value="GROUP_LEADER">Team Leader</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>
        </div>

        <p v-if="editUserError" class="text-xs text-red-400 font-medium">{{ editUserError }}</p>

        <div class="flex justify-end gap-2 pt-2">
          <button @click="editingUser = null; editUserError = ''" class="px-4 py-2 rounded-lg text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)]">Cancelar</button>
          <button @click="saveUserEdits" :disabled="savingUser || !editUserForm.email.trim()"
            class="px-4 py-2 rounded-lg text-sm bg-[var(--teal)] text-white hover:opacity-90 disabled:opacity-50 font-medium">
            {{ savingUser ? 'Guardando…' : 'Guardar cambios' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- LISTA DE EQUIPOS                                       -->
    <!-- ====================================================== -->
    <div class="space-y-4">
      <h2 class="text-xl font-bold flex items-center gap-2">👥 Equipos Configurados ({{ teamsStore.teams.length }})</h2>

      <div v-if="teamsStore.teams.length === 0"
        class="rounded-2xl border border-dashed border-[var(--border-subtle)] bg-[var(--bg-card)] p-8 text-center text-[var(--text-muted)]">
        No hay equipos creados. Haz clic en «+ Crear Nuevo Equipo» para empezar.
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="team in teamsStore.teams" :key="team.id"
          class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-5 shadow-sm space-y-3 flex flex-col justify-between">
          <div>
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="font-bold text-lg flex items-center gap-2">
                  <span class="inline-block h-3 w-3 rounded-full bg-[var(--teal)]"></span>{{ team.name }}
                </h3>
                <p class="text-xs text-[var(--text-muted)] mt-1">{{ team.description || 'Sin descripción' }}</p>
              </div>
              <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 flex-shrink-0">
                {{ team.memberEmails.length }} miembro{{ team.memberEmails.length === 1 ? '' : 's' }}
              </span>
            </div>
            <div class="mt-4">
              <p class="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2 font-semibold">Integrantes:</p>
              <div v-if="team.memberEmails.length === 0" class="text-xs text-[var(--text-muted)] italic">Sin miembros.</div>
              <div v-else class="flex flex-wrap gap-1.5">
                <span v-for="email in team.memberEmails" :key="email"
                  class="px-2.5 py-1 rounded-lg text-xs bg-[var(--bg-app)] border border-[var(--border-subtle)] flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                  {{ getUserNameByEmail(email) }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex gap-2 pt-3 border-t border-[var(--border-subtle)] justify-end">
            <button @click="openTeamModal(team)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--bg-app)] border border-[var(--border-subtle)] hover:border-[var(--teal)]">✏️ Editar</button>
            <button @click="teamToDelete = team"
              class="px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/30 hover:bg-red-500/20">🗑 Eliminar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- CREAR NUEVO USUARIO                                    -->
    <!-- ====================================================== -->
    <div class="space-y-4">
      <h2 class="text-xl font-bold flex items-center gap-2">➕ Crear Nuevo Usuario</h2>
      <div class="rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-card)] p-6 shadow-sm space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Nombre completo</label>
            <input v-model="newUser.fullName" placeholder="Nombre Apellido"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Correo electrónico</label>
            <input v-model="newUser.email" type="email" placeholder="usuario@correo.com"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Contraseña</label>
            <input v-model="newUser.password" type="password" placeholder="Mínimo 8 caracteres"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">Rol</label>
            <select v-model="newUser.role"
              class="w-full bg-[var(--bg-app)] border border-[var(--border-subtle)] rounded-lg p-2.5 text-sm outline-none focus:border-[var(--teal)]">
              <option value="DEVELOPER">Developer</option>
              <option value="GROUP_LEADER">Team Leader</option>
              <option value="ADMIN">Admin</option>
            </select>
          </div>
        </div>
        <p v-if="createUserError" class="text-xs text-red-400 font-medium">{{ createUserError }}</p>
        <p v-if="createUserSuccess" class="text-xs text-emerald-400 font-medium">{{ createUserSuccess }}</p>
        <div class="flex justify-end">
          <button @click="createUser" :disabled="creatingUser || !newUser.email.trim() || !newUser.password.trim()"
            class="px-5 py-2.5 rounded-xl bg-[var(--teal)] text-white text-sm font-medium hover:opacity-90 disabled:opacity-50">
            {{ creatingUser ? 'Creando…' : '✓ Crear Usuario' }}
          </button>
        </div>
      </div>
    </div>

    <!-- ====================================================== -->
    <!-- TABLA USUARIOS DEL SISTEMA                             -->
    <!-- ====================================================== -->
    <div class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold flex items-center gap-2">👤 Usuarios del Sistema ({{ systemUsers.length }})</h2>
        <button @click="loadUsers" class="text-xs text-[var(--teal)] border border-[var(--teal)]/40 px-3 py-1.5 rounded-lg hover:bg-[var(--teal)]/10">
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
              <th class="p-3">Equipos</th>
              <th class="p-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border-subtle)]">
            <tr v-for="u in systemUsers" :key="u.id || u.email" class="hover:bg-[var(--bg-app)]/50">
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
                  <span v-for="t in teamsStore.getUserTeams(u.email)" :key="t.id"
                    class="px-2 py-0.5 rounded text-xs bg-[var(--teal)]/15 text-[var(--teal)] border border-[var(--teal)]/30 font-medium">{{ t.name }}</span>
                  <span v-if="teamsStore.getUserTeams(u.email).length === 0" class="text-xs text-[var(--text-muted)]">Sin equipo</span>
                </div>
              </td>
              <td class="p-3 text-right">
                <button @click="openEditUser(u)"
                  class="px-3 py-1 rounded-lg text-xs font-medium bg-[var(--bg-app)] border border-[var(--border-subtle)] hover:border-[var(--teal)] text-[var(--text-primary)]">
                  ✏️ Editar
                </button>
              </td>
            </tr>
            <tr v-if="systemUsers.length === 0">
              <td colspan="5" class="p-6 text-center text-[var(--text-muted)] text-sm">No hay usuarios cargados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTeamsStore, type Team } from '@/stores/teams'
import { api } from '@/services/api'
import type { User } from '@/types'

const teamsStore = useTeamsStore()
const systemUsers = ref<User[]>([])
const loadingUsers = ref(false)

// ── Modal Equipo ───────────────────────────────────────────────────
const showTeamModal = ref(false)
const editingTeamId = ref<string | null>(null)
const teamForm = ref({ name: '', description: '', memberEmails: [] as string[] })
const customEmail = ref('')
const modalError = ref('')
const teamMemberSearch = ref('')

// ── Confirmar eliminar equipo ──────────────────────────────────────
const teamToDelete = ref<Team | null>(null)

// ── Editar usuario ─────────────────────────────────────────────────
const editingUser = ref<User | null>(null)
const editUserForm = ref({ fullName: '', email: '', password: '', role: 'DEVELOPER' })
const editUserError = ref('')
const savingUser = ref(false)

// ── Crear usuario ──────────────────────────────────────────────────
const newUser = ref({ fullName: '', email: '', password: '', role: 'DEVELOPER' })
const createUserError = ref('')
const createUserSuccess = ref('')
const creatingUser = ref(false)

// ── Lista de usuarios para checkboxes en el modal ─────────────────
const availableUsers = ref<User[]>([])

const filteredAvailableUsers = computed(() => {
  const query = teamMemberSearch.value.trim().toLowerCase()
  if (!query) return availableUsers.value
  return availableUsers.value.filter((u) =>
    (u.fullName || '').toLowerCase().includes(query) ||
    (u.email || '').toLowerCase().includes(query)
  )
})

// ── Parsear respuesta de api.users.list de forma segura ────────────
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

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    // FastAPI le=100 max en limit
    const res: any = await api.users.list({ limit: 100 })
    const fetched = parseUserList(res)
    if (fetched && fetched.length > 0) {
      systemUsers.value = fetched
      availableUsers.value = fetched
    }
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
  } finally {
    loadingUsers.value = false
  }
}

const getUserNameByEmail = (email: string): string => {
  const found = availableUsers.value.find((u) => u.email.toLowerCase() === email.toLowerCase())
  return found?.fullName || found?.full_name || email
}

// ── Modal equipo ───────────────────────────────────────────────────
const openTeamModal = (team?: Team) => {
  modalError.value = ''
  teamMemberSearch.value = ''
  if (team) {
    editingTeamId.value = team.id
    teamForm.value = { name: team.name, description: team.description || '', memberEmails: [...team.memberEmails] }
  } else {
    editingTeamId.value = null
    teamForm.value = { name: '', description: '', memberEmails: [] }
  }
  showTeamModal.value = true
}

const closeTeamModal = () => {
  showTeamModal.value = false
  editingTeamId.value = null
  teamMemberSearch.value = ''
  customEmail.value = ''
  modalError.value = ''
}

const addCustomEmail = () => {
  const email = customEmail.value.trim().toLowerCase()
  if (!email) return
  if (!teamForm.value.memberEmails.includes(email)) teamForm.value.memberEmails.push(email)
  customEmail.value = ''
}

const saveTeam = () => {
  const name = teamForm.value.name.trim()
  if (!name) { modalError.value = 'El nombre es obligatorio.'; return }
  if (editingTeamId.value) {
    teamsStore.updateTeam(editingTeamId.value, { name, description: teamForm.value.description, memberEmails: teamForm.value.memberEmails })
  } else {
    teamsStore.createTeam(name, teamForm.value.description, teamForm.value.memberEmails)
  }
  closeTeamModal()
}

// ── Eliminar equipo (con modal propio) ─────────────────────────────
const doDeleteTeam = () => {
  if (!teamToDelete.value) return
  teamsStore.deleteTeam(teamToDelete.value.id)
  teamToDelete.value = null
}

// ── Editar usuario ─────────────────────────────────────────────────
const openEditUser = (u: any) => {
  editingUser.value = u
  editUserForm.value = { fullName: u.fullName || u.full_name || '', email: u.email, password: '', role: u.role as string }
  editUserError.value = ''
}

const saveUserEdits = async () => {
  if (!editingUser.value) return
  editUserError.value = ''
  savingUser.value = true
  try {
    const payload: any = {
      full_name: editUserForm.value.fullName.trim() || undefined,
      email: editUserForm.value.email.trim().toLowerCase(),
      role: editUserForm.value.role
    }
    if (editUserForm.value.password.trim()) {
      payload.password = editUserForm.value.password.trim()
    }
    // Actualizar datos del usuario (nombre, correo, rol y password)
    await api.users.update(editingUser.value.id, payload)
    editingUser.value = null
    await loadUsers()
  } catch (err: any) {
    editUserError.value = err?.response?.data?.detail || 'No se pudo guardar los cambios.'
  } finally {
    savingUser.value = false
  }
}

// ── Crear usuario ──────────────────────────────────────────────────
const createUser = async () => {
  createUserError.value = ''
  createUserSuccess.value = ''
  const { fullName, email, password, role } = newUser.value
  if (!email.trim() || !password.trim()) { createUserError.value = 'Correo y contraseña son obligatorios.'; return }
  if (password.length < 8) { createUserError.value = 'La contraseña debe tener al menos 8 caracteres.'; return }
  creatingUser.value = true
  try {
    const created = await api.auth.register({
      email: email.trim().toLowerCase(),
      password,
      full_name: fullName.trim() || email.split('@')[0]
    } as any)
    // Cambiar rol si no es DEVELOPER (el backend registra como DEVELOPER por defecto)
    if (role !== 'DEVELOPER' && created?.user?.id) {
      try {
        await api.users.changeRole(created.user.id, role as any)
      } catch (e) {
        console.warn('No se pudo asignar rol específico al usuario:', e)
      }
    }
    createUserSuccess.value = `✓ Usuario "${email.trim()}" creado correctamente como ${role}.`
    newUser.value = { fullName: '', email: '', password: '', role: 'DEVELOPER' }
    await loadUsers()
  } catch (err: any) {
    createUserError.value = err?.response?.data?.detail || 'No se pudo crear el usuario. ¿El correo ya existe?'
  } finally {
    creatingUser.value = false
  }
}

onMounted(() => {
  teamsStore.loadFromStorage()
  loadUsers()
})
</script>
