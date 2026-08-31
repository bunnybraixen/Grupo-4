/**
 * Configuración de Vue Router para CoreStream
 * 
 * Define todas las rutas de la aplicación y sus componentes asociados.
 * Incluye:
 * - Rutas públicas (login)
 * - Rutas protegidas para administradores
 * - Rutas protegidas para desarrolladores
 * - Guards de navegación para validar autenticación y autorización
 * 
 * Las rutas utilizan layout anidados para mantener consistencia visual
 * en diferentes secciones de la aplicación.
 */

import { createRouter, createWebHistory, RouteRecordRaw, NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import type { UserRole } from '@/types'

/**
 * ========================================
 * DEFINICIÓN DE RUTAS
 * ========================================
 * 
 * Las rutas están organizadas por áreas funcionales:
 * - / : Raíz (redirige a login o dashboard)
 * - /login : Autenticación (pública)
 * - /admin/* : Panel de administración (requiere rol ADMIN)
 * - /dev/* : Área de desarrollo (requiere rol DEVELOPER o GROUP_LEADER)
 */
const routes: RouteRecordRaw[] = [
  {
    /**
     * Ruta raíz
     * Redirige al dashboard apropiado basado en el rol del usuario
     */
    path: '/',
    redirect: () => {
      /**
       * La redirección real ocurre en el guard de navegación
       * que valida la autenticación primero
       */
      const userRole = localStorage.getItem('userRole')
      return userRole === 'ADMIN' ? '/admin' : '/dev'
    }
  },

  /**
   * ========================================
   * RUTAS PÚBLICAS
   * ========================================
   */
  {
    /**
     * Ruta de login
     * Accesible a usuarios no autenticados
     * Redirige al dashboard si ya está autenticado
     */
    path: '/login',
    name: 'Login',
    /**
     * Carga el componente de login
     * Utiliza lazy loading para optimizar el bundle inicial
     */
    component: () => import('@/views/LoginView.vue'),
    /**
     * Meta información de la ruta
     */
    meta: {
      /**
       * Indica que esta ruta es pública y no requiere autenticación
       */
      requiresAuth: false,
      /**
       * Título de la página
       */
      title: 'Iniciar Sesión - CoreStream'
    }
  },

  /**
   * ========================================
   * RUTAS DE ADMINISTRACIÓN
   * ========================================
   * 
   * Todas las subrutas bajo /admin requieren rol ADMIN
   * Utilizan un layout común para el panel de administración
   */
  {
    /**
     * Layout raíz para todas las rutas de administración
     */
    path: '/admin',
    name: 'AdminLayout',
    /**
     * Componente de layout que proporciona navegación y estructura común
     */
    component: () => import('@/layouts/AdminLayout.vue'),
    /**
     * Guards de navegación específicos para rutas admin
     */
    meta: {
      requiresAuth: true,
      requiredRoles: ['ADMIN'],
      title: 'Administración - CoreStream'
    },
    /**
     * Rutas anidadas dentro del layout de administración
     */
    children: [
      {
        /**
         * Ruta por defecto: /admin
         * Redirige a /admin/builder
         */
        path: '',
        redirect: 'builder'
      },

      {
        /**
         * Vista principal de administración
         * Constructor de aplicaciones y épicas
         */
        path: 'builder',
        name: 'Builder',
        component: () => import('@/views/admin/BuilderView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['ADMIN'],
          title: 'Constructor - CoreStream Admin'
        }
      },

      {
        /**
         * Vista de analítica para administradores
         * Estadísticas globales del sistema, rendimiento del equipo
         */
        path: 'analytics',
        name: 'AdminAnalytics',
        component: () => import('@/views/admin/AnalyticsView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['ADMIN'],
          title: 'Analítica - CoreStream Admin'
        }
      },

      {
        /**
         * Vista de documentación de código
         * Gestión de especificaciones, documentos técnicos
         */
        path: 'code-docs',
        name: 'CodeDocs',
        component: () => import('@/views/admin/CodeDocsView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['ADMIN'],
          title: 'Documentación de Código - CoreStream Admin'
        }
      },

      {
        /**
         * Vista de gestión de equipo
         * Administración de usuarios, roles, permisos
         */
        path: 'team',
        name: 'TeamManagement',
        component: () => import('@/views/admin/TeamView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['ADMIN'],
          title: 'Gestión de Equipo - CoreStream Admin'
        }
      },

      {
        /**
         * Vista de gestión de incidentes (Admin)
         * Tablero Kanban por categoría, filtros, creación y asignación de incidentes.
         * Permite al administrador priorizar, agrupar y dar seguimiento a todos
         * los incidentes del sistema organizados por categoría.
         */
        path: 'incidents',
        name: 'Incidents',
        component: () => import('@/views/admin/IncidentsView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['ADMIN'],
          title: 'Incidentes - CoreStream Admin'
        }
      }
    ]
  },

  /**
   * ========================================
   * RUTAS DE DESARROLLO
   * ========================================
   * 
   * Rutas para desarrolladores y líderes de grupo
   * Incluye área de trabajo personal y herramientas de desarrollo
   */
  {
    /**
     * Layout para todas las rutas de desarrollo
     */
    path: '/dev',
    name: 'DeveloperLayout',
    component: () => import('@/layouts/DeveloperLayout.vue'),
    /**
     * Guards: requiere autenticación y rol DEVELOPER o GROUP_LEADER
     */
    meta: {
      requiresAuth: true,
      requiredRoles: ['DEVELOPER', 'GROUP_LEADER'],
      title: 'Área de Desarrollo - CoreStream'
    },
    /**
     * Rutas anidadas bajo el layout de desarrollo
     */
    children: [
      {
        /**
         * Ruta por defecto: /dev
         * Redirige a /dev/workbench
         */
        path: '',
        redirect: 'workbench'
      },

      {
        /**
         * Workbench del desarrollador
         * Vista principal de tareas asignadas y en progreso
         * Proporciona información rápida y fácil acceso a tareas
         */
        path: 'workbench',
        name: 'Workbench',
        component: () => import('@/views/dev/WorkbenchView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['DEVELOPER', 'GROUP_LEADER'],
          title: 'Mi Workbench - CoreStream'
        }
      },

      {
        /**
         * Vista de gestión de cargas/documentos
         * Subir, organizar y descargar archivos de proyecto
         */
        path: 'uploads',
        name: 'Uploads',
        component: () => import('@/views/dev/UploadsView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['DEVELOPER', 'GROUP_LEADER'],
          title: 'Mis Cargas - CoreStream'
        }
      },

      {
        /**
         * Vista de asignación de tareas del equipo
         * Solo disponible para líderes de grupo (GROUP_LEADER)
         * Permite asignar tareas a miembros del equipo
         */
        path: 'team-assignment',
        name: 'TeamAssignment',
        component: () => import('@/views/dev/TeamAssignmentView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['GROUP_LEADER'],
          title: 'Asignación de Equipo - CoreStream'
        }
      },

      {
        /**
         * Vista de incidentes del desarrollador
         * Muestra los incidentes asignados al usuario actual agrupados por estado.
         * Permite acciones rápidas (iniciar, enviar a revisión, etc.)
         * y un panel lateral de detalle completo.
         */
        path: 'my-incidents',
        name: 'MyIncidents',
        component: () => import('@/views/dev/MyIncidentsView.vue'),
        meta: {
          requiresAuth: true,
          requiredRoles: ['DEVELOPER', 'GROUP_LEADER'],
          title: 'Mis Incidentes - CoreStream'
        }
      }
    ]
  },

  /**
   * ========================================
   * RUTAS 404
   * ========================================
   */
  {
    /**
     * Ruta catch-all para páginas no encontradas
     * Debe ser la última ruta definida
     */
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: {
      title: 'Página No Encontrada - CoreStream'
    }
  }
]

/**
 * Crea la instancia de Router
 * Configuración:
 * - Modo history: URLs limpias sin # (requiere configuración en servidor)
 * - Base URL: '/' (raíz del dominio)
 */
const router = createRouter({
  /**
   * Modo de historial: usa History API del navegador
   * URLs se ven como /admin/builder en lugar de /#/admin/builder
   */
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

/**
 * ========================================
 * GUARDS DE NAVEGACIÓN
 * ========================================
 * 
 * Los guards se ejecutan antes de navegar a una ruta
 * Se utilizan para:
 * - Validar que el usuario está autenticado
 * - Validar que el usuario tiene los permisos necesarios
 * - Actualizar el título de la página
 * - Redirigir a login si no está autenticado
 */

/**
 * Guard global que se ejecuta antes de cada navegación
 * 
 * El orden es importante:
 * 1. Comprueba si la ruta requiere autenticación
 * 2. Comprueba si el usuario tiene el rol necesario
 * 3. Actualiza el título de la página
 * 4. Permite la navegación o redirige
 */
router.beforeEach(
  /**
   * @param to - Ruta destino hacia la que se intenta navegar
   * @param from - Ruta de origen desde la que se navega
   * @param next - Función para continuar la navegación
   */
  async (
    to: RouteLocationNormalized,
    from: RouteLocationNormalized,
    next: NavigationGuardNext
  ): Promise<void> => {
    /**
     * Obtiene el token de autenticación almacenado
     * Normalmente se guardaría en el store de Pinia
     * Aquí se simplifca extrayéndolo del localStorage
     */
    const token = localStorage.getItem('accessToken')
    const userRole = localStorage.getItem('userRole') as UserRole | null

    /**
     * Meta información de la ruta
     */
    const requiresAuth = to.meta.requiresAuth as boolean | undefined
    const requiredRoles = to.meta.requiredRoles as string[] | undefined

    /**
     * CASO 1: Ruta requiere autenticación pero usuario no tiene token
     */
    if (requiresAuth && !token) {
      /**
       * Redirige a login y guarda la ruta destino para volver después
       */
      next({
        name: 'Login',
        /**
         * Parámetro query: ruta a la que ir después de autenticarse
         */
        query: { redirect: to.path }
      })
      return
    }

    /**
     * CASO 2: Usuario intenta acceder a login pero ya está autenticado
     */
    if (to.name === 'Login' && token) {
      /**
       * Redirige al dashboard apropiado basado en rol
       */
      const targetPath = userRole === 'ADMIN' ? '/admin' : '/dev'
      next(targetPath)
      return
    }

    /**
     * CASO 3: Ruta requiere un rol específico y usuario no lo tiene
     */
    if (requiredRoles && userRole && !requiredRoles.includes(userRole)) {
      /**
       * Redirige a la página de acceso denegado o al dashboard principal
       */
      next({
        name: userRole === 'ADMIN' ? 'AdminLayout' : 'DeveloperLayout'
      })
      return
    }

    /**
     * CASO 4: Actualiza el título de la página
     * Se toma del meta.title definido en cada ruta
     */
    const title = to.meta.title as string | undefined
    if (title) {
      document.title = title
    }

    /**
     * Continúa con la navegación
     */
    next()
  }
)

/**
 * Hook que se ejecuta después de cada navegación
 * Útil para logging, analytics, etc.
 */
router.afterEach((to: RouteLocationNormalized) => {
  /**
   * Scroll a la parte superior de la página en nuevas rutas
   */
  window.scrollTo(0, 0)

  /**
   * Aquí se podrían enviar eventos de analytics o logging
   * Ejemplo: trackPageView(to.path)
   */
})

/**
 * Exporta la instancia del router
 * Se utiliza en main.ts para instalar en la aplicación
 */
export default router
