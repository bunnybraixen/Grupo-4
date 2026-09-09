describe('Separación de roles Admin/Developer', () => {

  it('Admin NO ve tabs Builder/Workbench en el header', () => {
    cy.loginAsAdmin()
    // Los tabs originales eran <button> dentro del <header>.
    // El sidebar usa "Constructor" (en español), no "Builder".
    // Scoping al header evita falsos positivos con el contenido del Builder.
    cy.get('header').contains('button', 'Builder').should('not.exist')
    cy.get('header').contains('button', 'Workbench').should('not.exist')
  })

  it('Admin no puede acceder a /#/dev/workbench manualmente', () => {
    cy.loginAsAdmin()
    cy.visit('/#/dev/workbench')
    cy.url({ timeout: 10000 }).should('not.include', '/dev/workbench')
    cy.url().should('include', '/admin')
  })

  it('Admin ve su sidebar correcto', () => {
    cy.loginAsAdmin()
    cy.contains('Constructor').should('be.visible')
    cy.contains('Analítica').should('be.visible')
    cy.contains('Documentación').should('be.visible')
    cy.contains('Equipo').should('be.visible')
  })

  it('Developer entra directo a su Workbench sin tabs', () => {
    cy.loginAsDeveloper()
    cy.url().should('include', '/dev/workbench')
    cy.get('header').contains('button', 'Builder').should('not.exist')
  })

  it('Developer no puede acceder a /#/admin/builder manualmente', () => {
    cy.loginAsDeveloper()
    cy.visit('/#/admin/builder')
    cy.url({ timeout: 10000 }).should('not.include', '/admin/builder')
    cy.url().should('include', '/dev')
  })

  it('Developer ve su sidebar correcto', () => {
    cy.loginAsDeveloper()
    cy.contains('Workbench').should('be.visible')
    cy.contains('Mis Archivos').should('be.visible')
  })
})
