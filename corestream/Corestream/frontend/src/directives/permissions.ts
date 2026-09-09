import type { Directive, DirectiveBinding } from 'vue'
import { UserRole } from '@/types'
import { useAuthStore } from '@/stores/auth'

type PermissionBindingValue =
  | UserRole
  | UserRole[]
  | {
      anyOf?: UserRole[]
      allOf?: UserRole[]
    }

const DISPLAY_ATTR = 'data-rbac-display'

function normalizeRole(role: unknown): UserRole | null {
  const roleValue = String(role ?? '').toUpperCase()

  if (roleValue === UserRole.ADMIN) return UserRole.ADMIN
  if (roleValue === UserRole.TEAM_LEADER) return UserRole.TEAM_LEADER
  if (roleValue === UserRole.DEVELOPER) return UserRole.DEVELOPER

  return null
}

function getCurrentRole(): UserRole | null {
  /**
   * Antes leía localStorage.getItem('userRole'). Desde que el estado de
   * sesión vive en el store de Pinia (plan 3.2: el access token ya no se
   * persiste), esa clave puede no reflejar la sesión real. useAuthStore()
   * es seguro de llamar aquí: Pinia ya está instalado en toda la app.
   */
  return normalizeRole(useAuthStore().userRole)
}

function isAllowed(bindingValue: PermissionBindingValue, currentRole: UserRole | null): boolean {
  if (!currentRole) return false

  if (Array.isArray(bindingValue)) {
    return bindingValue.includes(currentRole)
  }

  if (typeof bindingValue === 'object') {
    const anyOf = bindingValue.anyOf ?? []
    
// Retorna true si no hay restricciones de roles o si el rol actual está en la lista permitida
    const anyOfValid = anyOf.length === 0 || anyOf.includes(currentRole)


    return anyOfValid
  }

  return bindingValue === currentRole
}

function applyPermission(el: HTMLElement, binding: DirectiveBinding<PermissionBindingValue>): void {
  const currentRole = getCurrentRole()
  const allowed = isAllowed(binding.value, currentRole)

  if (allowed) {
    const previousDisplay = el.getAttribute(DISPLAY_ATTR)
    el.style.display = previousDisplay ?? ''
    return
  }

  if (!el.getAttribute(DISPLAY_ATTR)) {
    el.setAttribute(DISPLAY_ATTR, el.style.display || '')
  }

  el.style.display = 'none'
}

export const vCan: Directive<HTMLElement, PermissionBindingValue> = {
  mounted(el, binding) {
    applyPermission(el, binding)
  },
  updated(el, binding) {
    applyPermission(el, binding)
  }
}
