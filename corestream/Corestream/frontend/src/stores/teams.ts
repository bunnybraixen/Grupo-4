/**
 * Store de Equipos (Teams) - CoreStream
 * Gestiona equipos de trabajo, asignación de miembros y vinculación con proyectos.
 *
 * PERSISTENCIA: los equipos viven en el backend (`/api/teams`) para que una
 * sesión nueva —otro navegador, otro equipo, una ventana privada— los recupere
 * igual que recupera las aplicaciones y las épicas. `localStorage` se mantiene
 * como caché para pintar de inmediato y como respaldo si la API no responde.
 *
 * Los métodos de escritura siguen siendo síncronos (mutan el estado local y
 * devuelven el objeto) y empujan el cambio al backend en segundo plano: así no
 * hay que tocar las vistas que ya los usan.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export interface Team {
  id: string
  name: string
  description?: string
  memberEmails: string[]
  /** IDs de las aplicaciones asignadas a este equipo. */
  applicationIds: string[]
}

const STORAGE_KEY_TEAMS = 'corestream_teams_list'
const STORAGE_KEY_APP_TEAMS = 'corestream_app_teams_map'
/**
 * Marca la migración única de los equipos que solo existían en localStorage
 * hacia el backend. Evita re-subirlos si luego se borran a propósito.
 */
const STORAGE_KEY_MIGRATED = 'corestream_teams_migrated'

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
      const parsed = savedTeams ? JSON.parse(savedTeams) : []
      // Normalizar: los equipos cacheados antes de que existiera la
      // persistencia no tienen `applicationIds`.
      teams.value = (Array.isArray(parsed) ? parsed : []).map((team: any) => ({
        ...team,
        memberEmails: (team?.memberEmails ?? [])
          .map((email: string) => (email || '').trim().toLowerCase())
          .filter(Boolean),
        applicationIds: (team?.applicationIds ?? []).map((appId: any) => String(appId))
      }))

      const savedAppTeams = localStorage.getItem(STORAGE_KEY_APP_TEAMS)
      appTeams.value = savedAppTeams ? JSON.parse(savedAppTeams) : {}

      // Limpiar referencias huérfanas
      purgeStaleAppTeams()
    } catch (err) {
      console.error('Error al cargar equipos:', err)
      teams.value = []
      appTeams.value = {}
    }

    // Con la caché ya pintada, se sincroniza con el backend (fuente de verdad).
    void refreshFromServer()
  }

  /** ¿Hay sesión iniciada? Sin token no tiene sentido pedir los equipos. */
  const hasSession = (): boolean =>
    Boolean(localStorage.getItem('accessToken') || localStorage.getItem('authTokens'))

  /** Convierte un equipo al payload que espera la API. */
  const toPayload = (team: Team) => ({
    name: team.name,
    description: team.description ?? '',
    memberEmails: team.memberEmails ?? [],
    applicationIds: team.applicationIds ?? []
  })

  /** Reconstruye el mapa app -> equipo a partir de los equipos. */
  const rebuildAppTeams = () => {
    const mapping: Record<string, string> = {}
    for (const team of teams.value) {
      for (const appId of team.applicationIds ?? []) {
        mapping[appId] = team.id
      }
    }
    appTeams.value = mapping
  }

  /**
   * Empuja un equipo al backend (crear si aún tiene id local, actualizar si no).
   * Los errores se registran y no rompen la UI: localStorage sigue siendo el
   * respaldo, y los roles sin permiso (no ADMIN) no pueden escribir equipos.
   */
  const pushTeam = async (team: Team): Promise<void> => {
    if (!hasSession()) return
    try {
      if (team.id.startsWith('team-')) {
        await api.teams.create(toPayload(team))
      } else {
        await api.teams.update(team.id, toPayload(team))
      }
    } catch (err) {
      console.error('No se pudo guardar el equipo en el backend:', err)
    }
  }

  /**
   * Trae los equipos del backend, que es la fuente de verdad.
   *
   * - La primera vez, si el backend aún no tiene ninguno y en localStorage sí
   *   hay (los equipos creados antes de esta persistencia), se suben una sola
   *   vez para no perder la configuración existente.
   * - Si el backend responde, se reemplaza la caché con su contenido.
   * - Si falla la petición, se conserva lo cargado de localStorage.
   */
  const refreshFromServer = async (): Promise<void> => {
    if (!hasSession()) return
    try {
      let serverTeams = await api.teams.list()

      const alreadyMigrated = localStorage.getItem(STORAGE_KEY_MIGRATED) === 'true'
      if (serverTeams.length === 0 && teams.value.length > 0 && !alreadyMigrated) {
        for (const team of teams.value) {
          try {
            await api.teams.create(toPayload(team))
          } catch (err) {
            console.error('No se pudo migrar el equipo local al backend:', err)
          }
        }
        localStorage.setItem(STORAGE_KEY_MIGRATED, 'true')
        serverTeams = await api.teams.list()
      } else if (!alreadyMigrated) {
        localStorage.setItem(STORAGE_KEY_MIGRATED, 'true')
      }

      teams.value = serverTeams
      rebuildAppTeams()
      saveToStorage()
    } catch (err) {
      // Sin backend disponible se mantiene la caché local.
      console.error('Error al cargar equipos del backend:', err)
    }
  }

  const createTeam = (name: string, description: string = '', memberEmails: string[] = []): Team => {
    const newTeam: Team = {
      id: `team-${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      memberEmails: memberEmails.map((e) => e.trim().toLowerCase()).filter(Boolean),
      applicationIds: []
    }
    teams.value.push(newTeam)
    saveToStorage()

    // Persistir en el backend. Cuando responde, el id local (`team-...`) se
    // sustituye por el del servidor remapeando las asignaciones app->equipo.
    void (async () => {
      if (!hasSession()) return
      try {
        const created = await api.teams.create(toPayload(newTeam))
        if (!created?.id) return

        const localId = newTeam.id
        const index = teams.value.findIndex((t) => t.id === localId)
        if (index !== -1) {
          teams.value[index] = { ...teams.value[index], id: created.id }
        }
        for (const appId in appTeams.value) {
          if (appTeams.value[appId] === localId) {
            appTeams.value[appId] = created.id
          }
        }
        saveToStorage()
      } catch (err) {
        console.error('No se pudo crear el equipo en el backend:', err)
      }
    })()

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
        ? data.memberEmails.map((e) => e.trim().toLowerCase()).filter(Boolean)
        : existing.memberEmails,
      applicationIds: data.applicationIds
        ? data.applicationIds.map((appId) => String(appId))
        : existing.applicationIds
    }
    teams.value[index] = updated
    // Si las aplicaciones del equipo cambiaron, el mapa app->equipo también.
    if (data.applicationIds) {
      rebuildAppTeams()
    }
    saveToStorage()
    void pushTeam(updated)
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

    // Borrar también en el backend (los ids `team-...` aún no existen allí).
    void (async () => {
      if (!hasSession() || id.startsWith('team-')) return
      try {
        await api.teams.remove(id)
      } catch (err) {
        console.error('No se pudo eliminar el equipo en el backend:', err)
      }
    })()
  }

  const assignTeamToApp = (appId: string, teamId: string | null) => {
    const previousTeamId = appTeams.value[appId]

    if (!teamId) {
      delete appTeams.value[appId]
    } else {
      appTeams.value[appId] = teamId
    }

    // Reflejar la asignación en la lista de aplicaciones de cada equipo
    // afectado: es lo que se persiste en el backend (no el mapa en sí).
    const affected = new Set<string>()
    if (previousTeamId) affected.add(previousTeamId)
    if (teamId) affected.add(teamId)

    for (const affectedId of affected) {
      const index = teams.value.findIndex((t) => t.id === affectedId)
      if (index === -1) continue
      const appIds = Object.entries(appTeams.value)
        .filter(([, mappedTeamId]) => mappedTeamId === affectedId)
        .map(([mappedAppId]) => mappedAppId)
      teams.value[index] = { ...teams.value[index], applicationIds: appIds }
    }

    saveToStorage()

    void (async () => {
      for (const affectedId of affected) {
        const team = teams.value.find((t) => t.id === affectedId)
        if (team) await pushTeam(team)
      }
    })()
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

  /**
   * Emails (normalizados a minúsculas) de los miembros de un equipo concreto.
   */
  const getTeamMemberEmails = (teamId: string): string[] => {
    const team = teams.value.find((t) => t.id === teamId)
    return (team?.memberEmails ?? [])
      .map((e) => (e || '').trim().toLowerCase())
      .filter(Boolean)
  }

  /**
   * Emails de todos los miembros de los equipos a los que pertenece `userEmail`.
   * Un usuario puede estar en varios equipos: se devuelve la unión sin repetir.
   */
  const getUserTeamMemberEmails = (userEmail?: string | null): string[] => {
    const emails = new Set<string>()
    for (const team of getUserTeams(userEmail)) {
      for (const email of getTeamMemberEmails(team.id)) {
        emails.add(email)
      }
    }
    return Array.from(emails)
  }

  /**
   * Filtra una lista de usuarios para dejar solo los que pertenecen al equipo
   * del usuario actual (o al equipo indicado en `teamId`, si se pasa).
   *
   * - ADMIN no se filtra: gestiona todos los equipos.
   * - Sin equipo (ni `teamId` ni equipos del usuario) devuelve lista vacía: se
   *   prefiere no ofrecer a nadie antes que ofrecer gente de otros equipos.
   */
  const filterUsersByTeams = <T extends { email?: string | null }>(
    users: T[],
    userEmail?: string | null,
    isAdmin: boolean = false,
    teamId?: string | null
  ): T[] => {
    if (isAdmin) return users
    const allowed = new Set(
      teamId ? getTeamMemberEmails(teamId) : getUserTeamMemberEmails(userEmail)
    )
    return users.filter((u) => allowed.has((u.email || '').trim().toLowerCase()))
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
    getTeamMemberEmails,
    getUserTeamMemberEmails,
    filterUsersByTeams,
    isAppAssignedToUser,
    loadFromStorage,
    refreshFromServer,
    purgeStaleAppTeams
  }
})
