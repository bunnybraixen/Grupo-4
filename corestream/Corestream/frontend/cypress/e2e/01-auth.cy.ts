describe('Autenticación', () => {
  it('Login como Admin redirige a /admin/builder', () => {
    cy.loginAsAdmin()
    cy.url().should('include', '#/admin')
    cy.contains('CoreStream Builder').should('be.visible')
  })

  it('Login como Developer redirige a /dev/workbench', () => {
    cy.loginAsDeveloper()
    cy.url().should('include', '#/dev/workbench')
  })

  it('Login con credenciales incorrectas mantiene en /login', () => {
    cy.visit('/#/login')
    cy.get('#email').type('wrong@example.com')
    cy.get('#password').type('wrongpassword')
    cy.get('button[type="submit"]').click()
    cy.url().should('include', '#/login')
  })

  it('Logout redirige a /login', () => {
    cy.loginAsAdmin()
    cy.url().should('include', '#/admin')
    cy.contains('Cerrar sesión').click()
    cy.url().should('include', '#/login')
    // La sesión cacheada por cy.login (ver support/e2e.ts) ya no es válida:
    // el próximo loginAsAdmin() de este spec debe volver a autenticarse de
    // verdad en vez de asumir que la cookie sigue viva.
    cy.forgetLogin()
  })
})
