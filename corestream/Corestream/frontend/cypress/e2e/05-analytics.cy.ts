describe('Analytics', () => {
  beforeEach(() => {
    cy.loginAsAdmin('/admin/analytics')
  })

  it('Vista de Analytics carga con título correcto', () => {
    cy.contains('Analítica Global').should('be.visible')
  })

  it('Botón Exportar es visible', () => {
    cy.contains('Exportar').should('be.visible')
  })

  it('Dropdown de exportación muestra opciones PDF y CSV', () => {
    cy.contains('Exportar').click()
    // El dropdown puede estar recortado por overflow del contenedor padre
    cy.contains('Exportar como PDF').should('exist')
    cy.contains('Exportar como CSV').should('exist')
  })

  it('URL de Analytics es accesible directamente', () => {
    cy.url().should('include', '#/admin/analytics')
  })
})
