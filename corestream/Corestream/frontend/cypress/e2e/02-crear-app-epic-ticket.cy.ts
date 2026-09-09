// NOTA: Estos tests crean datos reales en la BD.
// Para CI, asegurarse de usar una BD de test limpia o agregar cleanup en afterEach.

describe('Crear App → Epic → Ticket', () => {
  beforeEach(() => {
    cy.loginAsAdmin('/admin/builder')
  })

  it('Crear nueva aplicación', () => {
    cy.contains('Nueva aplicación').click()
    cy.get('[data-cy="app-name-input"]').type('App E2E Test')
    cy.get('[data-cy="btn-guardar-app"]').click()
    cy.contains('App E2E Test').should('be.visible')
  })

  it('Seleccionar aplicación y crear nueva épica', () => {
    // Requiere que "App E2E Test" exista (creada en el test anterior o en seeding)
    cy.contains('App E2E Test').click()
    cy.contains('Nueva épica').click()
    cy.get('[data-cy="epic-title-input"]').type('Épica E2E')
    cy.get('[data-cy="btn-guardar-epic"]').click()
    cy.contains('Épica E2E').should('be.visible')
  })

  it('Crear nuevo ticket inline en la épica', () => {
    // Requiere que "App E2E Test" con "Épica E2E" existan
    cy.contains('App E2E Test').click()
    cy.contains('Épica E2E').should('be.visible')
    cy.contains('Agregar Ticket').click()
    cy.get('[data-cy="inline-ticket-input"]').type('Ticket E2E{enter}')
    // El ticket puede estar en un contenedor sin visibilidad completa en headless
    cy.contains('Ticket E2E').should('exist')
  })
})
