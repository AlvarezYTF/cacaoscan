describe('Auditoria View E2E Tests', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/auditoria')
  })

  it('should display audit logs', () => {
    cy.get('[data-cy="audit-logs"]').should('be.visible')
  })

  it('should filter audit logs by action', () => {
    cy.get('[data-cy="filter-action"]').select('login')
    cy.wait(500)
    cy.get('[data-cy="audit-logs"]').should('be.visible')
  })

  it('should filter audit logs by date range', () => {
    cy.get('[data-cy="date-from"]').type('2024-01-01')
    cy.get('[data-cy="date-to"]').type('2024-12-31')
    cy.get('[data-cy="apply-filters"]').click()
    cy.wait(500)
    cy.get('[data-cy="audit-logs"]').should('be.visible')
  })

  it('should view audit log details', () => {
    cy.get('[data-cy="view-log-details"]').first().click()
    cy.get('[data-cy="log-details-modal"]').should('be.visible')
  })

  it('should export audit logs', () => {
    cy.get('[data-cy="export-logs"]').click()
    cy.wait(1000)
    // Verify export started
  })
})

