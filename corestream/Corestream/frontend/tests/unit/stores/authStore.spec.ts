import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// ── Mocks antes de cualquier import del store ──────────────────────────────

vi.mock('@/services/api', () => ({
  api: {
    auth: {
      login: vi.fn(),
      logout: vi.fn(),
      getMe: vi.fn(),
      register: vi.fn(),
      refresh: vi.fn(),
      updateProfile: vi.fn(),
      changePassword: vi.fn(),
      requestPasswordReset: vi.fn(),
      confirmPasswordReset: vi.fn(),
    },
  },
  setAuthTokens: vi.fn(),
  clearAuthTokens: vi.fn(),
}))

vi.mock('@/stores/theme', () => ({
  useThemeStore: () => ({ applyTheme: vi.fn() }),
}))

// ── Helpers ────────────────────────────────────────────────────────────────

import { useAuthStore } from '@/stores/auth'
import type { User, AuthTokens } from '@/types'
import { api, setAuthTokens, clearAuthTokens } from '@/services/api'

const makeUser = (overrides: Partial<User> = {}): User => ({
  id: 'user-1',
  email: 'dev@corestream.com',
  fullName: 'Test Dev',
  role: 'DEVELOPER' as any,
  specialty: 'Backend',
  avatar: null,
  isActive: true,
  preferences: {},
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides,
} as User)

const makeTokens = (): AuthTokens => ({
  accessToken: 'header.payload.signature',
  refreshToken: 'refresh-token-value',
  tokenType: 'Bearer',
})

// ── Tests ──────────────────────────────────────────────────────────────────

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.clear()
  })

  // ── Estado inicial ──────────────────────────────────────────────────────

  describe('estado inicial', () => {
    it('inicia sin usuario', () => {
      const store = useAuthStore()
      expect(store.user).toBeNull()
    })

    it('inicia sin tokens', () => {
      const store = useAuthStore()
      expect(store.tokens).toBeNull()
    })

    it('inicia sin autenticar', () => {
      const store = useAuthStore()
      expect(store.isAuthenticated).toBe(false)
    })

    it('inicia sin carga', () => {
      const store = useAuthStore()
      expect(store.isLoading).toBe(false)
    })

    it('inicia sin error', () => {
      const store = useAuthStore()
      expect(store.error).toBeNull()
    })
  })

  // ── Computeds de rol ────────────────────────────────────────────────────

  describe('computed de roles', () => {
    it('isAdmin es true para rol ADMIN', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'ADMIN' as any })
      expect(store.isAdmin).toBe(true)
    })

    it('isAdmin es false para rol DEVELOPER', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'DEVELOPER' as any })
      expect(store.isAdmin).toBe(false)
    })

    it('isDeveloper es true para rol DEVELOPER', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'DEVELOPER' as any })
      expect(store.isDeveloper).toBe(true)
    })

    it('isDeveloper es false para rol TEAM_LEADER', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'TEAM_LEADER' as any })
      expect(store.isDeveloper).toBe(false)
    })

    it('isTeamLeader es true para rol TEAM_LEADER', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'TEAM_LEADER' as any })
      expect(store.isTeamLeader).toBe(true)
    })

    it('isTeamLeader es false cuando user es null', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.isTeamLeader).toBe(false)
    })

    it('userRole refleja el rol del usuario', () => {
      const store = useAuthStore()
      store.user = makeUser({ role: 'TEAM_LEADER' as any })
      expect(store.userRole).toBe('TEAM_LEADER')
    })

    it('userRole es undefined cuando user es null', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.userRole).toBeUndefined()
    })
  })

  // ── Computeds de datos ──────────────────────────────────────────────────

  describe('computed de datos de usuario', () => {
    it('fullName retorna el nombre del usuario', () => {
      const store = useAuthStore()
      store.user = makeUser({ fullName: 'Paolo Sepúlveda' })
      expect(store.fullName).toBe('Paolo Sepúlveda')
    })

    it('fullName retorna string vacío sin usuario', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.fullName).toBe('')
    })

    it('userEmail retorna el email del usuario', () => {
      const store = useAuthStore()
      store.user = makeUser({ email: 'paolo@test.com' })
      expect(store.userEmail).toBe('paolo@test.com')
    })

    it('userEmail retorna string vacío sin usuario', () => {
      const store = useAuthStore()
      store.user = null
      expect(store.userEmail).toBe('')
    })
  })

  // ── clearSession ────────────────────────────────────────────────────────

  describe('clearSession', () => {
    it('limpia el usuario', () => {
      const store = useAuthStore()
      store.user = makeUser()
      store.clearSession()
      expect(store.user).toBeNull()
    })

    it('limpia los tokens', () => {
      const store = useAuthStore()
      store.tokens = makeTokens()
      store.clearSession()
      expect(store.tokens).toBeNull()
    })

    it('pone isAuthenticated en false', () => {
      const store = useAuthStore()
      store.isAuthenticated = true
      store.clearSession()
      expect(store.isAuthenticated).toBe(false)
    })

    it('limpia el error', () => {
      const store = useAuthStore()
      store.error = 'Error anterior'
      store.clearSession()
      expect(store.error).toBeNull()
    })

    it('llama a clearAuthTokens del cliente HTTP', () => {
      const store = useAuthStore()
      store.clearSession()
      expect(clearAuthTokens).toHaveBeenCalled()
    })

    it('elimina authTokens del localStorage', () => {
      localStorage.setItem('authTokens', JSON.stringify(makeTokens()))
      const store = useAuthStore()
      store.clearSession()
      expect(localStorage.getItem('authTokens')).toBeNull()
    })
  })

  // ── login ───────────────────────────────────────────────────────────────

  describe('login', () => {
    it('establece isAuthenticated en true tras login exitoso', async () => {
      const mockUser = makeUser()
      vi.mocked(api.auth.login).mockResolvedValue({
        tokens: makeTokens(),
        user: mockUser,
      } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(mockUser)

      const store = useAuthStore()
      await store.login('dev@corestream.com', 'Test1234!')
      expect(store.isAuthenticated).toBe(true)
    })

    it('guarda los tokens tras login exitoso', async () => {
      const tokens = makeTokens()
      vi.mocked(api.auth.login).mockResolvedValue({ tokens, user: makeUser() } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(makeUser())

      const store = useAuthStore()
      await store.login('dev@corestream.com', 'Test1234!')
      expect(store.tokens).toEqual(tokens)
    })

    it('llama a setAuthTokens con los tokens recibidos', async () => {
      const tokens = makeTokens()
      vi.mocked(api.auth.login).mockResolvedValue({ tokens, user: makeUser() } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(makeUser())

      const store = useAuthStore()
      await store.login('dev@corestream.com', 'Test1234!')
      expect(setAuthTokens).toHaveBeenCalledWith(tokens)
    })

    it('retorna el usuario tras login exitoso', async () => {
      const mockUser = makeUser({ email: 'dev@corestream.com' })
      vi.mocked(api.auth.login).mockResolvedValue({ tokens: makeTokens(), user: mockUser } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(mockUser)

      const store = useAuthStore()
      const result = await store.login('dev@corestream.com', 'Test1234!')
      expect(result.email).toBe('dev@corestream.com')
    })

    it('guarda isLoading=false al terminar (éxito)', async () => {
      vi.mocked(api.auth.login).mockResolvedValue({ tokens: makeTokens(), user: makeUser() } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(makeUser())

      const store = useAuthStore()
      await store.login('dev@corestream.com', 'Test1234!')
      expect(store.isLoading).toBe(false)
    })

    it('lanza error y limpia sesión si el login falla', async () => {
      vi.mocked(api.auth.login).mockRejectedValue(new Error('Credenciales inválidas'))

      const store = useAuthStore()
      await expect(store.login('x@x.com', 'wrong')).rejects.toThrow()
      expect(store.isAuthenticated).toBe(false)
      expect(store.isLoading).toBe(false)
    })

    it('persiste accessToken en localStorage', async () => {
      const tokens = makeTokens()
      vi.mocked(api.auth.login).mockResolvedValue({ tokens, user: makeUser() } as any)
      vi.mocked(api.auth.getMe).mockResolvedValue(makeUser())

      const store = useAuthStore()
      await store.login('dev@corestream.com', 'Test1234!')
      expect(localStorage.getItem('accessToken')).toBe(tokens.accessToken)
    })
  })

  // ── logout ──────────────────────────────────────────────────────────────

  describe('logout', () => {
    it('limpia el usuario al hacer logout', async () => {
      vi.mocked(api.auth.logout).mockResolvedValue(undefined as any)

      const store = useAuthStore()
      store.user = makeUser()
      store.isAuthenticated = true
      await store.logout()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('limpia sesión incluso si el logout del servidor falla', async () => {
      vi.mocked(api.auth.logout).mockRejectedValue(new Error('Network error'))

      const store = useAuthStore()
      store.user = makeUser()
      store.isAuthenticated = true
      await store.logout()
      expect(store.user).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })
  })

  // ── refreshToken ────────────────────────────────────────────────────────

  describe('refreshToken', () => {
    it('lanza error si no hay refresh token', async () => {
      const store = useAuthStore()
      store.tokens = null
      await expect(store.refreshToken()).rejects.toThrow('No hay refresh token disponible')
    })

    it('actualiza tokens tras refresh exitoso', async () => {
      const newTokens = makeTokens()
      newTokens.accessToken = 'new.header.payload'
      vi.mocked(api.auth.refresh).mockResolvedValue(newTokens as any)

      const store = useAuthStore()
      store.tokens = makeTokens()
      await store.refreshToken()
      expect(store.tokens?.accessToken).toBe('new.header.payload')
    })
  })
})
