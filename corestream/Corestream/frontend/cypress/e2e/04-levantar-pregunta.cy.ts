// NOTA: Requiere un ticket en estado IN_PROGRESS asignado al developer.
// La sección "Levantar Pregunta" solo aparece en tickets IN_PROGRESS o TODO.

describe('Levantar Pregunta', () => {
  before(() => {
    // Asegurar que el developer tenga al menos un ticket IN_PROGRESS
    cy.ensureDeveloperHasInProgressTicket()
  })

  beforeEach(() => {
    cy.loginAsDeveloper('/dev/workbench')
  })

  it('Sección Levantar Pregunta visible al abrir ticket en progreso', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pregunta-form"]').should('be.visible')
    cy.get('[data-cy="pregunta-textarea"]').should('be.visible')
  })

  it('Botón enviar deshabilitado con menos de 10 caracteres', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pregunta-textarea"]').type('corto')
    cy.get('[data-cy="btn-enviar-pregunta"]').should('be.disabled')
  })

  it('Botón enviar habilitado con 10 o más caracteres', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pregunta-textarea"]').type('Esta es una pregunta válida con suficientes caracteres')
    cy.get('[data-cy="btn-enviar-pregunta"]').should('not.be.disabled')
  })

  it('Contador de caracteres se actualiza al escribir', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pregunta-textarea"]').type('Hola mundo')
    cy.contains('10/500 caracteres').should('be.visible')
  })
})
