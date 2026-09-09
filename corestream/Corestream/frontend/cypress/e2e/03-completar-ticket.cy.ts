// NOTA: Requiere datos de prueba — al menos un ticket en estado IN_PROGRESS asignado al developer.
// Si no hay tickets asignados, los tests de click en tarjeta fallarán con gracia.

describe('Completar ticket con PR link', () => {
  before(() => {
    // Asegurar que el developer tenga al menos un ticket IN_PROGRESS
    cy.ensureDeveloperHasInProgressTicket()
  })

  beforeEach(() => {
    cy.loginAsDeveloper('/dev/workbench')
  })

  it('Botón Completar deshabilitado sin PR link válido', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="btn-completar"]').should('be.disabled')
  })

  it('PR link válido de GitHub habilita el botón Completar', () => {
    // "owner/repo" es justo el placeholder que el propio input sugiere — la
    // app lo rechaza a propósito (mismo criterio que el SECRET_KEY: no
    // aceptar el ejemplo literal sin personalizar). Un repo real sí vale.
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pr-link-input"]').clear().type('https://github.com/corestream/backend/pull/42')
    cy.get('[data-cy="btn-completar"]').should('not.be.disabled')
  })

  it('PR link de GitLab es aceptado', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pr-link-input"]').clear().type('https://gitlab.com/corestream/backend/merge_requests/42')
    cy.get('[data-cy="btn-completar"]').should('not.be.disabled')
  })

  it('URL aleatoria no habilita el botón Completar', () => {
    cy.get('[data-cy="ticket-card"][data-status="IN_PROGRESS"]').first().click()
    cy.get('[data-cy="pr-link-input"]').clear().type('https://google.com')
    cy.get('[data-cy="btn-completar"]').should('be.disabled')
  })
})
