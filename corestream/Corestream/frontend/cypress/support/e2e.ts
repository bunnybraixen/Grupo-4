// Comandos custom para CoreStream E2E
// Credenciales de prueba según plan de desarrollo CS-046

// /auth/login está limitado a 8 intentos / 5min por cuenta (plan 3.5) — a
// propósito, para frenar fuerza bruta. Sin algo de caché, cada it() de cada
// spec haría un login real y agotaría ese cupo dentro de la misma corrida
// (25 tests × 3 cuentas en unos pocos minutos).
//
// cy.session (experimentalSessionAndOrigin) se probó primero, pero en esta
// versión de Cypress (10.11) el snapshot/restore de la cookie httpOnly del
// refresh token no sobrevive el roundtrip por CDP.
//
// Segundo hallazgo, más de fondo: /auth/refresh ROTA refresh_token y
// csrf_token en cada llamada (por diseño — plan 3.3). Un login real
// (cy.visit('/#/login') + submit) seguido INMEDIATAMENTE por una recarga
// completa (cy.visit(otraRuta)) dispara un /auth/refresh casi al instante
// después de que el login acabe de fijar las cookies — y ese refresh vuelve
// con 403 (CSRF inválido) de forma reproducible en este entorno (Electron +
// proxy de Vite), aunque el mismo ciclo login→refresh→refresh funciona bien
// por curl con cualquier margen de tiempo real. Es una carrera de la
// rotación bajo recargas de página consecutivas y sin apenas intervalo —
// algo que un usuario real casi nunca provoca (no recarga la página dos
// veces en milisegundos justo después de iniciar sesión).
//
// La solución de fondo, no un parche: no forzar una recarga completa
// aparte para "llegar" a una ruta tras el login. LoginView ya sabe navegar
// directo a `?redirect=` con router.replace (navegación SPA, sin recargar),
// así que loguear CON el destino evita la segunda recarga por completo.
Cypress.Cookies.defaults({ preserve: ['refresh_token', 'csrf_token'] })

// Variable de módulo, NO Cypress.env(): este archivo se recarga una vez por
// spec (nuevo contexto de navegador, cookies vacías), así que el flag debe
// resetear en ese mismo momento. Cypress.env() vive a nivel del driver y
// sobrevive entre specs — usarlo aquí hacía creer que había sesión cuando
// el navegador del spec siguiente no tenía ninguna cookie todavía.
let loggedInAs: string | null = null

Cypress.Commands.add('login', (email: string, password: string, redirectPath?: string) => {
  if (loggedInAs === email) {
    // Ya autenticado: si el destino pedido es distinto de donde estamos,
    // una sola recarga a esa ruta (sin ninguna otra inmediatamente antes o
    // después) no dispara la carrera — solo es un problema cuando se
    // encadenan dos recargas pegadas a un login recién hecho.
    if (redirectPath) {
      cy.visit(`/#${redirectPath}`)
      cy.url({ timeout: 10000 }).should('not.match', /#\/login$/)
    } else {
      cy.location('hash').then((hash) => {
        if (hash === '#/login' || hash === '') {
          cy.visit('/')
          cy.url({ timeout: 10000 }).should('not.match', /#\/login$/)
        }
      })
    }
    return
  }

  const loginUrl = redirectPath
    ? `/#/login?redirect=${encodeURIComponent(redirectPath)}`
    : '/#/login'
  cy.visit(loginUrl)
  cy.intercept('POST', '**/api/auth/login').as('loginRequest')
  cy.get('input[type="email"]', { timeout: 10000 }).should('be.visible').type(email)
  cy.get('input[type="password"]').type(password)
  cy.get('button[type="submit"]').click()
  cy.wait('@loginRequest').its('response.statusCode').should('eq', 200)
  cy.url({ timeout: 10000 }).should('not.match', /#\/login$/)
  loggedInAs = email
})

// Para usar después de un logout real en un test: sin esto, el próximo
// cy.loginAsX() de este mismo spec seguiría creyendo que la cookie vive.
Cypress.Commands.add('forgetLogin', () => {
  loggedInAs = null
})

Cypress.Commands.add('loginAsAdmin', (redirectPath?: string) => {
  cy.login('admin@example.com', 'Admin@123!', redirectPath)
})

Cypress.Commands.add('loginAsDeveloper', (redirectPath?: string) => {
  cy.login('userdev@example.com', 'Jjgg11@!', redirectPath)
})

Cypress.Commands.add('loginAsLeader', (redirectPath?: string) => {
  cy.login('leader@example.com', 'Leader@123!', redirectPath)
})

/**
 * Token de admin para setup por API, cacheado en Cypress.env() durante toda
 * la corrida (sobrevive entre specs, a diferencia de una variable de módulo)
 * para no gastar cupo del rate limiter de /auth/login en cada llamada.
 */
function getAdminApiToken() {
  const cached = Cypress.env('__adminApiToken')
  if (cached) {
    return cy.wrap(cached, { log: false })
  }
  return cy
    .request({
      method: 'POST',
      url: '/api/auth/login',
      body: { email: 'admin@example.com', password: 'Admin@123!' },
    })
    .then(function (resp) {
      Cypress.env('__adminApiToken', resp.body.access_token)
      return resp.body.access_token
    })
}

// El RBAC bloquea a un ADMIN de ejecutar acciones de trabajo sobre tickets
// ("Los administradores no pueden ejecutar acciones de trabajo en
// tickets") — correcto por diseño (plan 4.6). /start hay que llamarlo como
// el propio developer asignado, no como admin.
function getDeveloperApiToken() {
  const cached = Cypress.env('__devApiToken')
  if (cached) {
    return cy.wrap(cached, { log: false })
  }
  return cy
    .request({
      method: 'POST',
      url: '/api/auth/login',
      body: { email: 'userdev@example.com', password: 'Jjgg11@!' },
    })
    .then(function (resp) {
      Cypress.env('__devApiToken', resp.body.access_token)
      return resp.body.access_token
    })
}

/**
 * Crea un ticket de prueba asignado al developer y lo inicia (IN_PROGRESS).
 * Requiere que exista al menos una aplicación con una épica.
 * Usa la API directamente para evitar dependencia de la UI.
 */
Cypress.Commands.add('ensureDeveloperHasInProgressTicket', () => {
  getAdminApiToken().then(function(adminToken) {
    const headers = { Authorization: 'Bearer ' + adminToken }

    // 2. Obtener usuario developer
    cy.request({ method: 'GET', url: '/api/users/', headers: headers }).then(function(usersResp) {
      const rawUsers = usersResp.body
      const users = Array.isArray(rawUsers) ? rawUsers : (rawUsers.items || [])
      const dev = users.find(function(u) { return u.email === 'userdev@example.com' })
      if (!dev) return

      // 3. Obtener primera aplicación disponible
      cy.request({ method: 'GET', url: '/api/applications/', headers: headers }).then(function(appsResp) {
        const rawApps = appsResp.body
        const apps = Array.isArray(rawApps) ? rawApps : (rawApps.items || rawApps.data || [])
        if (!apps.length) return

        const appId = apps[0].id

        // 4. Obtener épicas de la aplicación
        cy.request({ method: 'GET', url: '/api/epics/by-app/' + appId, headers: headers }).then(function(epicsResp) {
          const epics = Array.isArray(epicsResp.body) ? epicsResp.body : []
          if (!epics.length) return

          const epicId = epics[0].id

          // 5. Crear ticket asignado al developer
          cy.request({
            method: 'POST',
            url: '/api/tickets/',
            headers: headers,
            body: {
              title: 'Ticket Dev E2E',
              description: 'Test ticket para E2E',
              epic_id: epicId,
              assignee_id: dev.id,
              priority: 'MEDIUM',
            },
          }).then(function(ticketResp) {
            const ticketId = ticketResp.body.id

            // 6. Iniciar el ticket (IN_PROGRESS) — como el developer asignado
            getDeveloperApiToken().then(function (devToken) {
              cy.request({
                method: 'POST',
                url: '/api/tickets/' + ticketId + '/start',
                headers: { Authorization: 'Bearer ' + devToken },
              })
            })
          })
        })
      })
    })
  })
})
