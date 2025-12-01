describe('Admin Dashboard E2E Tests', () => {
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/dashboard')
  })

  it('should display dashboard header', () => {
    cy.contains('Dashboard de Administración').should('be.visible')
  })

  it('should display KPI cards', () => {
    cy.get('[data-cy="kpi-cards"]').should('be.visible')
  })

  it('should display charts section', () => {
    cy.get('[data-cy="dashboard-charts"]').should('be.visible')
  })

  it('should display recent users table', () => {
    cy.get('[data-cy="recent-users-table"]').should('be.visible')
  })

  it('should display recent activities table', () => {
    cy.get('[data-cy="recent-activities-table"]').should('be.visible')
  })

  it('should refresh dashboard data', () => {
    cy.get('[data-cy="refresh-button"]').click()
    cy.wait(1000)
    // Verify data is refreshed
    cy.get('[data-cy="kpi-cards"]').should('be.visible')
  })

  it('should navigate to users page', () => {
    cy.get('[data-cy="view-all-users"]').click()
    cy.url().should('include', '/admin/usuarios')
  })

  it('should navigate to activities page', () => {
    cy.get('[data-cy="view-all-activities"]').click()
    cy.url().should('include', '/auditoria')
  })
})

