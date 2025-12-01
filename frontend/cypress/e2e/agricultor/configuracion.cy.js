describe('Agricultor Configuracion E2E Tests', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/agricultor/configuracion')
  })

  it('should display configuration form', () => {
    cy.get('[data-cy="config-form"]').should('be.visible')
  })

  it('should update personal information', () => {
    cy.get('[data-cy="first-name"]').clear().type('Juan')
    cy.get('[data-cy="last-name"]').clear().type('Pérez')
    cy.get('[data-cy="phone"]').clear().type('1234567890')
    cy.get('[data-cy="save-config"]').click()
    
    cy.wait(500)
    cy.get('[data-cy="success-message"]').should('be.visible')
  })

  it('should update password', () => {
    cy.get('[data-cy="change-password"]').click()
    cy.get('[data-cy="current-password"]').type('oldpassword')
    cy.get('[data-cy="new-password"]').type('newpassword123')
    cy.get('[data-cy="confirm-password"]').type('newpassword123')
    cy.get('[data-cy="save-password"]').click()
    
    cy.wait(500)
    cy.get('[data-cy="success-message"]').should('be.visible')
  })
})

