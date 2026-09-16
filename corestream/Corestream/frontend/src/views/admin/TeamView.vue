<template>
  <div class="flex flex-col min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-dark-gray-90 dark:to-dark-gray-80">
    <!-- Header -->
    <AppHeader />

    <!-- Main content -->
    <div class="p-8 flex-1 overflow-auto">
      <!-- Header -->
      <div class="mb-8">
      <h1 class="text-4xl font-bold text-slate-900 dark:text-white mb-2">
        👥 Gestión de Equipo
      </h1>
      <p class="text-slate-600 dark:text-slate-300">
        Administra miembros del equipo, roles y asignaciones de tareas
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
      <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] p-6">
        <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">Total Miembros</div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white mt-2">{{ teamStore.memberCount }}</div>
      </div>
      <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] p-6">
        <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">Desarrolladores</div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white mt-2">{{ teamStore.developerCount }}</div>
      </div>
      <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] p-6">
        <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">Líderes</div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white mt-2">{{ teamStore.leaders.length }}</div>
      </div>
      <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] p-6">
        <div class="text-sm text-slate-600 dark:text-slate-300 font-medium">Tickets Sin Asignar</div>
        <div class="text-3xl font-bold text-slate-900 dark:text-white mt-2">{{ teamStore.unassignedTicketCount }}</div>
      </div>
    </div>

    <!-- Controls -->
    <div class="mb-6 flex gap-3">
      <button
        @click="showAddMemberModal = true"
        class="px-4 py-2 bg-lime text-dark-gray font-semibold rounded-lg hover:bg-lime-90 transition-colors flex items-center gap-2"
      >
        ➕ Invitar Miembro
      </button>
      <button
        @click="refreshTeam"
        :disabled="isLoading"
        class="px-4 py-2 bg-slate-200 dark:bg-[var(--bg-card)] text-slate-700 dark:text-slate-300 font-medium rounded-lg hover:bg-slate-300 dark:hover:bg-[var(--border-subtle)] transition-colors disabled:opacity-50"
      >
        🔄 Actualizar
      </button>
    </div>

    <!-- Members Table -->
    <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-sm border border-slate-200 dark:border-[var(--border-subtle)] overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1000px]">
          <thead>
            <tr class="border-b border-slate-200 dark:border-[var(--border-subtle)] bg-slate-50 dark:bg-[var(--bg-panel)]">
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Miembro</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Email</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Rol</th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Especialidad</th>
              <th class="px-3 py-4 text-center text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Completadas</th>
              <th class="px-3 py-4 text-center text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Pendientes</th>
              <th class="px-3 py-4 text-center text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Bloqueadas</th>
              <th class="px-4 py-4 text-right text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider whitespace-nowrap">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-dark-gray-60">
            <tr v-for="member in teamStore.sortedByName" :key="member.id" class="hover:bg-slate-50 dark:hover:bg-[var(--bg-panel)] transition-colors">
              <!-- Member Name with Avatar -->
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 bg-gradient-to-br from-teal to-teal-dark rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {{ getInitials(member.fullName) }}
                  </div>
                  <span class="font-medium text-slate-900 dark:text-white">{{ member.fullName }}</span>
                </div>
              </td>

              <!-- Email -->
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ member.email }}</td>

              <!-- Role Badge -->
              <td class="px-6 py-4">
                <div class="inline-flex items-center gap-2">
                  <span
                    :class="[
                      'px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1',
                      member.role === 'ADMIN'
                        ? 'bg-teal/20 text-teal'
                        : member.role === 'TEAM_LEADER'
                          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                          : 'bg-slate-200 dark:bg-dark-gray-60 text-slate-700 dark:text-slate-300'
                    ]"
                  >
                    <span v-if="member.role === 'TEAM_LEADER'">👑</span>
                    {{ roleLabel(member.role) }}
                  </span>
                </div>
              </td>

              <!-- Specialty -->
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400 font-medium">
                {{ member.specialty || 'Sin especificar' }}
              </td>

              <!-- Completed Tickets -->
              <td class="px-3 py-4 text-center">
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-teal/10 text-teal font-semibold">
                  {{ memberStats[member.id]?.completed || 0 }}
                </span>
              </td>

              <!-- Pending Tickets -->
              <td class="px-3 py-4 text-center">
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 font-semibold">
                  {{ memberStats[member.id]?.pending || 0 }}
                </span>
              </td>

              <!-- Blocked Tickets -->
              <td class="px-3 py-4 text-center">
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 font-semibold">
                  {{ memberStats[member.id]?.blocked || 0 }}
                </span>
              </td>

              <!-- Actions -->
              <td class="px-4 py-4 text-right whitespace-nowrap">
                <div class="flex justify-end gap-2">
                  <!-- Promote Button -->
                  <button
                    v-if="member.role === 'DEVELOPER' && authStore.user?.role === 'ADMIN'"
                    @click="promoteToLeader(member.id)"
                    :disabled="isLoading"
                    class="px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-900/50 rounded text-xs font-medium transition-colors disabled:opacity-50"
                    title="Promover a Líder"
                  >
                    Promover
                  </button>

                  <!-- Demote Button -->
                  <button
                    v-if="member.role === 'TEAM_LEADER' && authStore.user?.role === 'ADMIN'"
                    @click="demoteLeader(member.id)"
                    :disabled="isLoading"
                    class="px-3 py-1 bg-slate-200 dark:bg-dark-gray-60 text-slate-700 dark:text-slate-300 hover:bg-slate-300 dark:hover:bg-[var(--border-color)] rounded text-xs font-medium transition-colors disabled:opacity-50"
                    title="Degradar a Desarrollador"
                  >
                    Degradar
                  </button>

                  <!-- Edit Button -->
                  <button
                    @click="editMember(member)"
                    class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50 rounded text-xs font-medium transition-colors"
                    title="Editar"
                  >
                    ✏️
                  </button>

                  <!-- Delete Button -->
                  <button
                    v-if="member.id !== authStore.user?.id && authStore.user?.role === 'ADMIN'"
                    @click="promptDelete(member.id, member.fullName)"
                    :disabled="isLoading"
                    class="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-900/50 rounded text-xs font-medium transition-colors disabled:opacity-50"
                    title="Eliminar"
                  >
                    🗑️
                  </button>

                  <!-- Protected indicator for own account -->
                  <span
                    v-else-if="member.id === authStore.user?.id && authStore.user?.role === 'ADMIN'"
                    class="px-3 py-1 rounded text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 cursor-not-allowed select-none"
                    title="No puedes eliminar tu propia cuenta de administrador"
                  >
                    🔒 Protegido
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="!isLoading && teamStore.members.length === 0" class="p-12 text-center">
        <p class="text-slate-600 dark:text-slate-400">No hay miembros en el equipo</p>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="p-12 text-center">
        <p class="text-slate-600 dark:text-slate-400">Cargando...</p>
      </div>
    </div>

    <!-- MODAL 1: Agregar/Editar Miembro -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showAddMemberModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-xl w-full max-w-md mx-4">
            <div class="p-6 border-b border-slate-200 dark:border-[var(--border-subtle)]">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white">
                {{ showEditModal ? 'Editar Miembro' : 'Invitar Nuevo Miembro' }}
              </h2>
            </div>

            <!-- Enlace de invitación ya generado: se muestra en vez del formulario -->
            <div v-if="inviteLink" class="p-6 space-y-4">
              <p class="text-sm text-slate-600 dark:text-slate-300">
                Copia este enlace y entrégaselo a la persona invitada (por Slack, correo, etc.).
                Solo se muestra una vez.
              </p>
              <div class="flex gap-2">
                <input
                  :value="inviteLink"
                  readonly
                  class="flex-1 px-3 py-2 border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg bg-slate-50 dark:bg-[var(--bg-panel)] text-slate-900 dark:text-white text-sm"
                  @click="($event.target as HTMLInputElement).select()"
                />
                <button
                  type="button"
                  @click="copyInviteLink"
                  class="px-4 py-2 bg-lime text-dark-gray font-semibold rounded-lg hover:bg-lime-90 transition-colors"
                >
                  Copiar
                </button>
              </div>
              <button
                type="button"
                @click="closeMemberModal"
                class="w-full px-4 py-2 border border-slate-300 dark:border-[var(--border-subtle)] text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-[var(--bg-panel)] transition-colors"
              >
                Cerrar
              </button>
            </div>

            <form v-else @submit.prevent="saveMember" class="p-6 space-y-4">
              <div v-if="showEditModal">
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Nombre Completo
                </label>
                <input
                  v-model="formData.fullName"
                  type="text"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg bg-white dark:bg-[var(--bg-panel)] text-slate-900 dark:text-white focus:outline-none focus:border-lime"
                  required
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Email
                </label>
                <input
                  v-model="formData.email"
                  type="email"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg bg-white dark:bg-[var(--bg-panel)] text-slate-900 dark:text-white focus:outline-none focus:border-lime"
                  :disabled="showEditModal"
                  required
                />
              </div>

              <div v-if="showEditModal">
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Especialidad
                </label>
                <select
                  v-model="formData.specialty"
                  class="w-full px-3 py-2 border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg bg-white dark:bg-[var(--bg-panel)] text-slate-900 dark:text-white focus:outline-none focus:border-lime"
                >
                  <option value="" disabled>Seleccione una especialidad...</option>
                  <option value="Frontend">Frontend</option>
                  <option value="Backend">Backend</option>
                  <option value="Fullstack">Fullstack</option>
                  <option value="DevOps / Cloud">DevOps / Cloud</option>
                  <option value="QA / Testing">QA / Testing</option>
                  <option value="UX/UI Design">UX/UI Design</option>
                  <option value="Data Science">Data Science</option>
                  <option value="Project Management">Project Management</option>
                </select>
              </div>

              <div v-if="!showEditModal">
                <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Rol
                </label>
                <select
                  v-model="formData.role"
                  required
                  class="w-full px-3 py-2 border border-slate-300 dark:border-[var(--border-subtle)] rounded-lg bg-white dark:bg-[var(--bg-panel)] text-slate-900 dark:text-white focus:outline-none focus:border-lime"
                >
                  <option value="DEVELOPER">Desarrollador</option>
                  <option value="TEAM_LEADER">Líder de Equipo</option>
                </select>
              </div>

              <div class="flex gap-3 mt-6">
                <button
                  type="button"
                  @click="closeMemberModal"
                  class="flex-1 px-4 py-2 border border-slate-300 dark:border-[var(--border-subtle)] text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-[var(--bg-panel)] transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  :disabled="isLoading"
                  class="flex-1 px-4 py-2 bg-lime text-dark-gray font-semibold rounded-lg hover:bg-lime-90 transition-colors disabled:opacity-50"
                >
                  {{ showEditModal ? 'Guardar Cambios' : 'Generar Invitación' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- MODAL 2: Confirmación de Eliminación -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="memberToDelete" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div class="bg-white dark:bg-[var(--bg-card)] rounded-xl shadow-xl w-full max-w-md mx-4 p-6 border border-slate-200 dark:border-[var(--border-subtle)]">
            
            <div class="flex items-center gap-3 mb-4 text-red-600 dark:text-red-400">
              <span class="text-3xl">⚠️</span>
              <h3 class="text-xl font-bold text-slate-900 dark:text-white">
                Eliminar a {{ memberToDelete.name }}
              </h3>
            </div>

            <p class="text-slate-600 dark:text-slate-300 mb-6 text-sm">
              Estás a punto de eliminar a este miembro del equipo. Elige cómo deseas proceder con sus datos:
            </p>

            <div class="flex flex-col gap-3">
              <!-- Soft Delete -->
              <button 
                @click="executeDelete(false)" 
                :disabled="isLoading"
                class="w-full px-4 py-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700/50 text-amber-800 dark:text-amber-300 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors text-left disabled:opacity-50"
              >
                <span class="font-bold block">Desactivar (Soft Delete)</span>
                <span class="text-xs opacity-80">Recomendado. Conserva su historial de tickets y métricas.</span>
              </button>

              <!-- Hard Delete -->
              <button 
                @click="executeDelete(true)" 
                :disabled="isLoading"
                class="w-full px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/50 text-red-800 dark:text-red-300 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors text-left disabled:opacity-50"
              >
                <span class="font-bold block">Eliminación Total (Hard Delete)</span>
                <span class="text-xs opacity-80">Peligroso. Destruye su registro y tickets permanentemente.</span>
              </button>

              <!-- Cancelar -->
              <button 
                @click="memberToDelete = null" 
                :disabled="isLoading"
                class="w-full mt-2 px-4 py-2 border-2 border-slate-200 dark:border-[var(--border-subtle)] rounded-lg font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-[var(--bg-panel)] transition-colors text-center disabled:opacity-50"
              >
                Cancelar y volver
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import { useTeamStore } from '@/stores/team'
import { useAuthStore } from '@/stores/auth'
import { UserRole } from '@/types'
import type { User } from '@/types'
import api from '@/services/api'
import { useDialogStore } from '@/stores/dialog'

const teamStore = useTeamStore()
const authStore = useAuthStore()
const dialogStore = useDialogStore()

// ========== STATE ==========
const isLoading = ref(false)
const showAddMemberModal = ref(false)
const showEditModal = ref(false)
const inviteLink = ref<string | null>(null)

const formData = ref({
  fullName: '',
  email: '',
  specialty: '',
  role: UserRole.DEVELOPER,
})

const editingMemberId = ref<string | null>(null)

// Member statistics (completed, pending, blocked tickets)
const memberStats = ref<Record<string, { completed: number; pending: number; blocked: number }>>({})

const loadRealStats = async () => {
  try {
    const response = await api.tickets.list({ limit: 500 } as any)
    
    // Manejamos la estructura de respuesta según FastAPI
    const allTickets = Array.isArray(response) ? response : ((response as any).items || (response as any).data || [])
    
    const stats: Record<string, { completed: number; pending: number; blocked: number }> = {}
    
    // Inicializamos a todos los miembros en 0
    teamStore.members.forEach(member => {
      stats[member.id] = { completed: 0, pending: 0, blocked: 0 }
    })

    // Contamos los tickets reales por usuario
    allTickets.forEach((ticket: any) => {
      const uId = ticket.assignee_id
      if (!stats[uId]) return
      
      if (ticket.status === 'COMPLETED') {
        stats[uId].completed++
      } else if (ticket.status === 'BLOCKED_QUESTION') {
        stats[uId].blocked++
      } else {
        stats[uId].pending++ 
      }
    })
    
    memberStats.value = stats
  } catch (error) {
    console.error('Error al cargar estadísticas reales:', error)
  }
}

// ========== METHODS ==========
const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || 'U'
}

const roleLabel = (role: UserRole): string => {
  const labels: Record<UserRole, string> = {
    ADMIN: 'Administrador',
    TEAM_LEADER: 'Líder de Equipo',
    DEVELOPER: 'Desarrollador',
  }
  return labels[role] || role
}

const refreshTeam = async () => {
  isLoading.value = true
  try {
    await teamStore.fetchMembers()
    await loadRealStats()
  } catch (error) {
    console.error('Error al actualizar equipo:', error)
    dialogStore.alert('Error al actualizar el equipo')
  } finally {
    isLoading.value = false
  }
}

const editMember = (member: User) => {
  editingMemberId.value = member.id
  formData.value = {
    fullName: member.fullName,
    email: member.email,
    specialty: member.specialty || '',
    role: member.role,
  }
  showEditModal.value = true
}

const saveMember = async () => {
  if (showEditModal.value) {
    if (!formData.value.fullName) {
      dialogStore.alert('Por favor completa todos los campos requeridos')
      return
    }
  } else if (!formData.value.email) {
    dialogStore.alert('Por favor ingresa un correo')
    return
  }

  isLoading.value = true
  try {
    if (editingMemberId.value) {
      // Edit existing member
      await teamStore.updateMember(editingMemberId.value, {
        fullName: formData.value.fullName,
        specialty: formData.value.specialty || undefined,
      })
      showEditModal.value = false
      formData.value = { fullName: '', email: '', specialty: '', role: UserRole.DEVELOPER }
      editingMemberId.value = null
    } else {
      // Invita al nuevo miembro: no crea la cuenta todavía, solo genera el
      // enlace. Se muestra en el propio modal en vez de cerrarlo.
      inviteLink.value = await teamStore.inviteMember({
        email: formData.value.email,
        role: formData.value.role as UserRole,
      })
    }
  } catch (error) {
    console.error('Error al guardar miembro:', error)
    dialogStore.alert('Error al guardar los cambios')
  } finally {
    isLoading.value = false
  }
}

const closeMemberModal = () => {
  showAddMemberModal.value = false
  showEditModal.value = false
  inviteLink.value = null
  formData.value = { fullName: '', email: '', specialty: '', role: UserRole.DEVELOPER }
  editingMemberId.value = null
}

const copyInviteLink = async () => {
  if (!inviteLink.value) return
  try {
    await navigator.clipboard.writeText(inviteLink.value)
    dialogStore.alert('Enlace copiado al portapapeles')
  } catch {
    // Sin permiso de clipboard: el input de todas formas es seleccionable a mano
  }
}

const promoteToLeader = async (userId: string) => {
  if (!(await dialogStore.confirm('¿Estás seguro de que deseas promover este miembro a líder?'))) {
    return
  }

  isLoading.value = true
  try {
    await teamStore.promoteToLeader(userId)
  } catch (error) {
    console.error('Error al promover:', error)
    dialogStore.alert('Error al promover el miembro')
  } finally {
    isLoading.value = false
  }
}

const demoteLeader = async (userId: string) => {
  if (!(await dialogStore.confirm('¿Estás seguro de que deseas degradar este líder a desarrollador?'))) {
    return
  }

  isLoading.value = true
  try {
    await teamStore.demoteLeader(userId)
  } catch (error) {
    console.error('Error al degradar:', error)
    dialogStore.alert('Error al degradar el líder')
  } finally {
    isLoading.value = false
  }
}

// Variable para controlar el modal de eliminación
const memberToDelete = ref<{ id: string; name: string } | null>(null)

// Abre el modal guardando los datos del usuario
const promptDelete = (userId: string, memberName: string) => {
  memberToDelete.value = { id: userId, name: memberName }
}

// Ejecuta la eliminación (Soft o Hard) y llama al store
const executeDelete = async (hardDelete: boolean) => {
  if (!memberToDelete.value) return

  isLoading.value = true
  try {
    // Llamamos al store pasando el parámetro de hardDelete
    await teamStore.deleteMember(memberToDelete.value.id, hardDelete)
    memberToDelete.value = null
  } catch (error) {
    console.error('Error al eliminar:', error)
    dialogStore.alert('Error al eliminar el miembro: ' + (error as Error).message)
  } finally {
    isLoading.value = false
  }
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  isLoading.value = true
  try {
    await teamStore.fetchMembers()
    await loadRealStats()
  } catch (error) {
    console.error('Error al cargar equipo:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
