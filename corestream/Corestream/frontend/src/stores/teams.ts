/**
 * Store de Equipos (Teams) - CoreStream
 * Gestiona equipos de trabajo, asignación de miembros y vinculación con proyectos.
 *
 * NOTA: Ya no hay equipos DEFAULT hardcodeados para evitar que equipos borrados
 * reaparezcan entre sesiones.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Team {
  id: string
  name: string
  description?: string
  memberEmails: string[]
}

const STORAGE_KEY_TEAMS = 'corestream_teams_list'
const STORAGE_KEY_APP_TEAMS = 'corestream_app_teams_map'

export const useTeamsStore = defineStore('teams', () => {
  const teams = ref<Team[]>([])
  const appTeams = ref<Record<string, string>>({}) // appId -> teamId

  const saveToStorage = () => {
    try {
      localStorage.setItem(STORAGE_KEY_TEAMS, JSON.stringify(teams.value))
      localStorage.setItem(STORAGE_KEY_APP_TEAMS, JSON.stringify(appTeams.value))
    } catch (err) {
      console.error('Error al guardar equipos:', err)
    }
  }

  /**
   * Limpia asignaciones app->equipo que apuntan a equipos que ya no existen.
   * Se llama en loadFromStorage y después de deleteTeam.
   */
  const purgeStaleAppTeams = () => {
    const validIds = new Set(teams.value.map((t) => t.id))
    let changed = false
    for (const appId in appTeams.value) {
      if (!validIds.has(appTeams.value[appId])) {
        delete appTeams.value[appId]
        changed = true
      }
    }
    if (changed) saveToStorage()
  }

  const loadFromStorage = () => {
    try {
      const savedTeams = localStorage.getItem(STORAGE_KEY_TEAMS)
      // Si existe clave en localStorage la usamos (incluso si es array vacío).
      // Si NO existe todavía (primera vez), arrancamos con lista vacía.
      teams.value = savedTeams ? JSON.parse(savedTeams) : []

      const savedAppTeams = localStorage.getItem(STORAGE_KEY_APP_TEAMS)
      appTeams.value = savedAppTeams ? JSON.parse(savedAppTeams) : {}

      // Limpiar referencias huérfanas
      purgeStaleAppTeams()
    } catch (err) {
      console.error('Error al cargar equipos:', err)
      teams.value = []
      appTeams.value = {}
    }
  }

  const createTeam = (name: string, description: string = '', memberEmails: string[] = []): Team => {
    const newTeam: Team = {
      id: `team-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      memberEmails: memberEmails.map((e) => e.trim().toLowerCase())
    }
    teams.value.push(newTeam)
    saveToStorage()
    return newTeam
  }

  const updateTeam = (id: string, data: Partial<Team>): Team | null => {
    const index = teams.value.findIndex((t) => t.id === id)
    if (index === -1) return null
    const existing = teams.value[index]
    const updated: Team = {
      ...existing,
      ...data,
      memberEmails: data.memberEmails
        ? data.memberEmails.map((e) => e.trim().toLowerCase())
        : existing.memberEmails
    }
    teams.value[index] = updated
    saveToStorage()
    return updated
  }

  const deleteTeam = (id: string) => {
    teams.value = teams.value.filter((t) => t.id !== id)
    // Limpiar asignaciones de proyectos a este equipo
    for (const appId in appTeams.value) {
      if (appTeams.value[appId] === id) {
        delete appTeams.value[appId]
      }
    }
    saveToStorage()
  }

  const assignTeamToApp = (appId: string, teamId: string | null) => {
    if (!teamId) {
      delete appTeams.value[appId]
    } else {
      appTeams.value[appId] = teamId
    }
    saveToStorage()
  }

  const getTeamForApp = (appId: string): Team | null => {
    const teamId = appTeams.value[appId]
    if (!teamId) return null
    // Si el teamId apunta a un equipo que ya no existe, limpiar
    const found = teams.value.find((t) => t.id === teamId)
    if (!found) {
      delete appTeams.value[appId]
      saveToStorage()
      return null
    }
    return found
  }

  const getUserTeams = (userEmail?: string | null): Team[] => {
    if (!userEmail) return []
    const email = (userEmail || '').trim().toLowerCase()
    return teams.value.filter((t) =>
      (t.memberEmails || []).some((e) => (e || '').toLowerCase() === email)
    )
  }

  /**
   * Devuelve true si el usuario tiene acceso a la aplicación.
   * - Admin siempre tiene acceso.
   * - Si el proyecto no tiene equipo asignado, solo el Admin puede verlo.
   * - Si tiene equipo, el usuario debe pertenecer a ese equipo.
   */
  const isAppAssignedToUser = (appId: string, userEmail?: string | null, isAdmin: boolean = false): boolean => {
    if (isAdmin) return true
    const appTeam = getTeamForApp(appId)
    if (!appTeam) return false

    const userTeamList = getUserTeams(userEmail)
    return userTeamList.some((t) => t.id === appTeam.id)
  }

  // Cargar inmediatamente al crear el store
  loadFromStorage()

  return {
    teams,
    appTeams,
    createTeam,
    updateTeam,
    deleteTeam,
    assignTeamToApp,
    getTeamForApp,
    getUserTeams,
    isAppAssignedToUser,
    loadFromStorage,
    purgeStaleAppTeams
  }
})
