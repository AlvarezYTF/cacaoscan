import { 
  visitAndWaitForBody, 
  verifyElementsVisible
} from '../../support/helpers'

describe('Gestión de Reportes - ReportsManagement', () => {
  beforeEach(() => {
    cy.login('analyst')
    visitAndWaitForBody('/reportes/management')
  })

  it('debe mostrar lista de reportes', () => {
    verifyElementsVisible([
      '[data-cy="reports-list"]',
      '[data-cy="reports-header"]',
      '[data-cy="create-report-button"]'
    ])
  })

  it('debe mostrar filtros de reportes', () => {
    verifyElementsVisible([
      '[data-cy="reports-filters"]',
      '[data-cy="filter-type"]',
      '[data-cy="filter-status"]',
      '[data-cy="filter-date-range"]'
    ])
  })

  it('debe crear nuevo reporte de calidad', () => {
    cy.createReport({
      type: 'calidad',
      title: 'Reporte de Calidad Mensual',
      description: 'Análisis de calidad de granos',
      format: 'pdf'
    })
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
    cy.get('[data-cy="reports-list"]').should('contain', 'Reporte de Calidad Mensual')
  })

  it('debe crear reporte de finca', () => {
    cy.createReport({
      type: 'finca',
      finca: '1',
      title: 'Reporte de Finca'
    })
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe filtrar reportes por tipo', () => {
    cy.applyReportFilter('type', 'calidad')
    
    cy.get('[data-cy="reports-list"]').within(() => {
      cy.get('[data-cy="report-item"]').each(($item) => {
        cy.wrap($item).should('contain', 'Calidad')
      })
    })
  })

  it('debe filtrar reportes por estado', () => {
    cy.applyReportFilter('status', 'completado')
    
    cy.get('[data-cy="reports-list"]').should('be.visible')
  })

  it('debe descargar reporte completado', () => {
    cy.executeInFirstItem('[data-cy="report-item"]', () => {
      cy.get('[data-cy="download-report"]').should('be.visible').click()
    })
    
    cy.checkNotification('Descargando reporte', 'info')
  })

  it('debe previsualizar reporte', () => {
    cy.executeInFirstItem('[data-cy="report-item"]', () => {
      cy.get('[data-cy="preview-report"]').click()
    })
    
    verifyElementsVisible([
      '[data-cy="report-preview-modal"]',
      '[data-cy="preview-content"]'
    ])
  })

  it('debe eliminar reporte con confirmación', () => {
    cy.executeInFirstItem('[data-cy="report-item"]', () => {
      cy.get('[data-cy="delete-report"]').click()
    })
    
    cy.confirmAction()
    
    cy.checkNotification('Reporte eliminado exitosamente', 'success')
  })

  it('debe mostrar estadísticas de reportes', () => {
    verifyElementsVisible([
      '[data-cy="reports-stats"]',
      '[data-cy="total-reports"]',
      '[data-cy="completed-reports"]',
      '[data-cy="generating-reports"]'
    ])
  })

  it('debe paginar lista de reportes', () => {
    cy.get('[data-cy="reports-list"]').should('be.visible')
    
    cy.get('[data-cy="pagination"]').should('be.visible')
    cy.get('[data-cy="next-page"]').click()
    
    cy.url().should('include', 'page=2')
  })

  it('debe mostrar mensaje cuando no hay reportes', () => {
    cy.applyReportFilter('status', 'fallido')
    
    cy.verifyEmptyStateMessage('[data-cy="empty-state"]', 'No se encontraron reportes')
  })
})
