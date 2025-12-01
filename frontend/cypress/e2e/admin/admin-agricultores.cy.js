describe('Admin Agricultores E2E Tests', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/agricultores')
  })

  it('should display agricultores list', () => {
    cy.get('[data-cy="agricultores-table"]').should('be.visible')
  })

  it('should filter agricultores', () => {
    cy.get('[data-cy="filter-agricultores"]').type('test')
    cy.wait(500)
    cy.get('[data-cy="agricultores-table"]').should('be.visible')
  })

  it('should view agricultor details', () => {
    cy.get('[data-cy="view-agricultor"]').first().click()
    cy.get('[data-cy="agricultor-details"]').should('be.visible')
  })
})

