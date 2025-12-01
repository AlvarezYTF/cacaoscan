import { visitAndWaitForBody } from '../../support/helpers'

describe('Gestión de Reportes - ReportsManagement', () => {
  const createReport = (reportData) => {
    cy.get('[data-cy="create-report-button"]').click()
    
    if (reportData.type) {
      cy.get('[data-cy="report-type"]').select(reportData.type)
    }
    if (reportData.finca) {
      cy.get('[data-cy="finca-select"]').select(reportData.finca)
    }
    if (reportData.title) {
      cy.get('[data-cy="report-title"]').type(reportData.title)
    }
    if (reportData.description) {
      cy.get('[data-cy="report-description"]').type(reportData.description)
    }
    if (reportData.format) {
      cy.get('[data-cy="report-format"]').select(reportData.format)
    }
    
    cy.get('[data-cy="generate-report"]').click()
  }

  const applyFilter = (filterType, value) => {
    cy.get(`[data-cy="filter-${filterType}"]`).select(value)
    cy.get('[data-cy="apply-filters"]').click()
  }

  beforeEach(() => {
    cy.login('analyst')
    visitAndWaitForBody('/reportes/management')
  })

  it('debe mostrar lista de reportes', () => {
    cy.get('[data-cy="reports-list"]').should('be.visible')
    cy.get('[data-cy="reports-header"]').should('be.visible')
    cy.get('[data-cy="create-report-button"]').should('be.visible')
  })

  it('debe mostrar filtros de reportes', () => {
    cy.get('[data-cy="reports-filters"]').should('be.visible')
    cy.get('[data-cy="filter-type"]').should('be.visible')
    cy.get('[data-cy="filter-status"]').should('be.visible')
    cy.get('[data-cy="filter-date-range"]').should('be.visible')
  })

  it('debe crear nuevo reporte de calidad', () => {
    createReport({
      type: 'calidad',
      title: 'Reporte de Calidad Mensual',
      description: 'Análisis de calidad de granos',
      format: 'pdf'
    })
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
    cy.get('[data-cy="reports-list"]').should('contain', 'Reporte de Calidad Mensual')
  })

  it('debe crear reporte de finca', () => {
    createReport({
      type: 'finca',
      finca: '1',
      title: 'Reporte de Finca'
    })
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe filtrar reportes por tipo', () => {
    applyFilter('type', 'calidad')
    
    cy.get('[data-cy="reports-list"]').within(() => {
      cy.get('[data-cy="report-item"]').each(($item) => {
        cy.wrap($item).should('contain', 'Calidad')
      })
    })
  })

  it('debe filtrar reportes por estado', () => {
    applyFilter('status', 'completado')
    
    cy.get('[data-cy="reports-list"]').should('be.visible')
  })

  it('debe descargar reporte completado', () => {
    cy.get('[data-cy="report-item"]').first().within(() => {
      cy.get('[data-cy="download-report"]').should('be.visible').click()
    })
    
    cy.checkNotification('Descargando reporte', 'info')
  })

  it('debe previsualizar reporte', () => {
    cy.get('[data-cy="report-item"]').first().within(() => {
      cy.get('[data-cy="preview-report"]').click()
    })
    
    cy.get('[data-cy="report-preview-modal"]').should('be.visible')
    cy.get('[data-cy="preview-content"]').should('be.visible')
  })

  it('debe eliminar reporte con confirmación', () => {
    cy.get('[data-cy="report-item"]').first().within(() => {
      cy.get('[data-cy="delete-report"]').click()
    })
    
    cy.confirmAction()
    
    cy.checkNotification('Reporte eliminado exitosamente', 'success')
  })

  it('debe mostrar estadísticas de reportes', () => {
    cy.get('[data-cy="reports-stats"]').should('be.visible')
    cy.get('[data-cy="total-reports"]').should('be.visible')
    cy.get('[data-cy="completed-reports"]').should('be.visible')
    cy.get('[data-cy="generating-reports"]').should('be.visible')
  })

  it('debe paginar lista de reportes', () => {
    cy.get('[data-cy="reports-list"]').should('be.visible')
    
    cy.get('[data-cy="pagination"]').should('be.visible')
    cy.get('[data-cy="next-page"]').click()
    
    cy.url().should('include', 'page=2')
  })

  it('debe mostrar mensaje cuando no hay reportes', () => {
    applyFilter('status', 'fallido')
    
    cy.get('[data-cy="empty-state"]').should('be.visible')
    cy.get('[data-cy="empty-state"]').should('contain', 'No se encontraron reportes')
  })
})
