describe('Gestión de Reportes - ReportsManagement', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes/management')
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
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('calidad')
    cy.get('[data-cy="report-title"]').type('Reporte de Calidad Mensual')
    cy.get('[data-cy="report-description"]').type('Análisis de calidad de granos')
    cy.get('[data-cy="report-format"]').select('pdf')
    
    cy.get('[data-cy="generate-report"]').click()
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
    cy.get('[data-cy="reports-list"]').should('contain', 'Reporte de Calidad Mensual')
  })

  it('debe crear reporte de finca', () => {
    cy.get('[data-cy="create-report-button"]').click()
    
    cy.get('[data-cy="report-type"]').select('finca')
    cy.get('[data-cy="finca-select"]').select('1')
    cy.get('[data-cy="report-title"]').type('Reporte de Finca')
    
    cy.get('[data-cy="generate-report"]').click()
    
    cy.checkNotification('Reporte generado exitosamente', 'success')
  })

  it('debe filtrar reportes por tipo', () => {
    cy.get('[data-cy="filter-type"]').select('calidad')
    cy.get('[data-cy="apply-filters"]').click()
    
    cy.get('[data-cy="reports-list"]').within(() => {
      cy.get('[data-cy="report-item"]').each(($item) => {
        cy.wrap($item).should('contain', 'Calidad')
      })
    })
  })

  it('debe filtrar reportes por estado', () => {
    cy.get('[data-cy="filter-status"]').select('completado')
    cy.get('[data-cy="apply-filters"]').click()
    
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
    cy.get('[data-cy="filter-status"]').select('fallido')
    cy.get('[data-cy="apply-filters"]').click()
    
    cy.get('[data-cy="empty-state"]').should('be.visible')
    cy.get('[data-cy="empty-state"]').should('contain', 'No se encontraron reportes')
  })
})
