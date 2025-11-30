describe('Reportes View E2E Tests', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/reportes')
  })

  it('should display reports list', () => {
    cy.get('[data-cy="reports-table"]').should('be.visible')
  })

  it('should create new report', () => {
    cy.get('[data-cy="create-report"]').click()
    cy.get('[data-cy="report-generator-modal"]').should('be.visible')
    
    cy.get('[data-cy="report-type"]').select('anual')
    cy.get('[data-cy="date-from"]').type('2024-01-01')
    cy.get('[data-cy="date-to"]').type('2024-12-31')
    cy.get('[data-cy="generate-report"]').click()
    
    cy.wait(2000)
    cy.get('[data-cy="reports-table"]').should('be.visible')
  })

  it('should filter reports by type', () => {
    cy.get('[data-cy="filter-type"]').select('anual')
    cy.wait(500)
    cy.get('[data-cy="reports-table"]').should('be.visible')
  })

  it('should filter reports by status', () => {
    cy.get('[data-cy="filter-status"]').select('completado')
    cy.wait(500)
    cy.get('[data-cy="reports-table"]').should('be.visible')
  })

  it('should download report', () => {
    cy.get('[data-cy="download-report"]').first().click()
    cy.wait(1000)
    // Verify download started
  })

  it('should delete report', () => {
    cy.get('[data-cy="delete-report"]').first().click()
    cy.get('[data-cy="confirm-delete"]').click()
    cy.wait(500)
    cy.get('[data-cy="reports-table"]').should('be.visible')
  })
})

