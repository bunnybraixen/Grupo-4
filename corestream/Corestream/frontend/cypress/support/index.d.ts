declare namespace Cypress {
  interface Chainable {
    login(email: string, password: string, redirectPath?: string): Chainable<void>
    loginAsAdmin(redirectPath?: string): Chainable<void>
    loginAsDeveloper(redirectPath?: string): Chainable<void>
    loginAsLeader(redirectPath?: string): Chainable<void>
    ensureDeveloperHasInProgressTicket(): Chainable<void>
    forgetLogin(): Chainable<void>
  }
}
