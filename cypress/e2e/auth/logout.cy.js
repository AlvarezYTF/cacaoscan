describe('Logout Flow', () => {
  beforeEach(() => {
    // Login before each test
    cy.visit('/login')
    cy.get('input[type="email"]').type(Cypress.env('CYPRESS_TEST_EMAIL') || 'test@example.com')
    cy.get('input[type="password"]').type(Cypress.env('CYPRESS_LOGIN_PASSWORD') || 'testpassword')
    cy.get('button[type="submit"]').click()
    cy.url().should('not.include', '/login')
  })

  it('should logout successfully', () => {
    // Find and click logout button
    cy.get('[data-testid="logout-button"]').click()
    
    // Should redirect to login
    cy.url().should('include', '/login')
    
    // Should show login form
    cy.get('input[type="email"]').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
  })

  it('should clear session on logout', () => {
    // Verify user is logged in
    cy.window().its('localStorage').should('have.property', 'access_token')
    
    // Logout
    cy.get('[data-testid="logout-button"]').click()
    
    // Verify session is cleared
    cy.window().its('localStorage').should('not.have.property', 'access_token')
  })
})

