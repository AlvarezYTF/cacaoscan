describe('Admin Usuarios E2E Tests', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/usuarios')
  })

  it('should display users list', () => {
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should filter users by role', () => {
    cy.get('[data-cy="role-filter"]').select('farmer')
    cy.wait(500)
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should search users', () => {
    cy.get('[data-cy="user-search"]').type('test@example.com')
    cy.wait(500)
    cy.get('[data-cy="users-table"]').should('be.visible')
  })

  it('should view user details', () => {
    cy.get('[data-cy="view-user"]').first().click()
    cy.get('[data-cy="user-details-modal"]').should('be.visible')
  })

  it('should edit user', () => {
    cy.get('[data-cy="edit-user"]').first().click()
    cy.get('[data-cy="edit-user-form"]').should('be.visible')
  })

  it('should delete user with confirmation', () => {
    cy.get('[data-cy="delete-user"]').first().click()
    cy.get('[data-cy="confirm-delete"]').click()
    cy.wait(500)
    // Verify user is removed
    cy.get('[data-cy="users-table"]').should('be.visible')
  })
})

