describe('Visualización de Reportes - Lista y Detalles', () => {
  beforeEach(() => {
    cy.login('analyst')
    cy.visit('/reportes')
  })

  it('debe mostrar lista de reportes generados', () => {
    cy.get('[data-cy="reports-list"]').should('be.visible')
    cy.get('[data-cy="report-item"]').should('have.length.greaterThan', 0)
    
    // Verificar información de cada reporte
    cy.get('[data-cy="report-item"]').first().within(() => {
      cy.get('[data-cy="report-name"]').should('be.visible')
      cy.get('[data-cy="report-type"]').should('be.visible')
      cy.get('[data-cy="report-date"]').should('be.visible')
      cy.get('[data-cy="report-status"]').should('be.visible')
    })
  })

  it('debe mostrar detalles de reporte específico', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar detalles del reporte
    cy.get('[data-cy="report-details"]').should('be.visible')
    cy.get('[data-cy="report-title"]').should('be.visible')
    cy.get('[data-cy="report-metadata"]').should('be.visible')
    cy.get('[data-cy="report-content"]').should('be.visible')
  })

  it('debe mostrar resumen ejecutivo del reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar resumen ejecutivo
    cy.get('[data-cy="executive-summary"]').should('be.visible')
    cy.get('[data-cy="key-findings"]').should('be.visible')
    cy.get('[data-cy="recommendations"]').should('be.visible')
    cy.get('[data-cy="conclusions"]').should('be.visible')
  })

  it('debe mostrar gráficos y visualizaciones', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar gráficos
    cy.get('[data-cy="report-charts"]').should('be.visible')
    cy.get('[data-cy="quality-chart"]').should('be.visible')
    cy.get('[data-cy="trend-chart"]').should('be.visible')
    cy.get('[data-cy="comparison-chart"]').should('be.visible')
  })

  it('debe permitir descargar reporte en diferentes formatos', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar opciones de descarga
    cy.get('[data-cy="download-options"]').should('be.visible')
    cy.get('[data-cy="download-pdf"]').should('be.visible')
    cy.get('[data-cy="download-excel"]').should('be.visible')
    cy.get('[data-cy="download-powerpoint"]').should('be.visible')
    
    // Descargar PDF
    cy.get('[data-cy="download-pdf"]').click()
    cy.verifyDownload('reporte.pdf')
  })

  it('debe permitir compartir reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Compartir reporte
    cy.get('[data-cy="share-report"]').click()
    
    // Verificar opciones de compartir
    cy.get('[data-cy="share-options"]').should('be.visible')
    cy.get('[data-cy="share-email"]').should('be.visible')
    cy.get('[data-cy="share-link"]').should('be.visible')
    
    // Compartir por email
    cy.get('[data-cy="share-email"]').click()
    cy.get('[data-cy="email-input"]').type('test@example.com')
    cy.get('[data-cy="send-share"]').click()
    
    cy.checkNotification('Reporte compartido exitosamente', 'success')
  })

  it('debe permitir buscar reportes', () => {
    cy.get('[data-cy="search-reports"]').type('análisis')
    
    // Verificar resultados filtrados
    cy.get('[data-cy="report-item"]').should('contain', 'análisis')
    cy.get('[data-cy="search-results-count"]').should('be.visible')
  })

  it('debe permitir filtrar reportes por tipo', () => {
    cy.get('[data-cy="report-type-filter"]').select('analisis-periodo')
    
    // Verificar filtros aplicados
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filtered-results"]').should('be.visible')
    
    // Verificar que solo se muestran reportes del tipo seleccionado
    cy.get('[data-cy="report-item"]').each(($item) => {
      cy.wrap($item).should('contain', 'Análisis por Período')
    })
  })

  it('debe permitir filtrar reportes por fecha', () => {
    cy.get('[data-cy="date-filter"]').click()
    cy.get('[data-cy="date-range-start"]').type('2024-01-01')
    cy.get('[data-cy="date-range-end"]').type('2024-01-31')
    cy.get('[data-cy="apply-date-filter"]').click()
    
    // Verificar filtros aplicados
    cy.get('[data-cy="active-filters"]').should('be.visible')
    cy.get('[data-cy="filtered-results"]').should('be.visible')
  })

  it('debe permitir ordenar reportes', () => {
    // Ordenar por fecha (más recientes primero)
    cy.get('[data-cy="sort-reports"]').select('date-desc')
    
    // Verificar orden
    cy.get('[data-cy="report-item"]').first().should('contain', '2024-01-15')
    
    // Ordenar por nombre
    cy.get('[data-cy="sort-reports"]').select('name-asc')
    
    // Verificar orden alfabético
    cy.get('[data-cy="report-item"]').first().should('contain', 'A')
  })

  it('debe mostrar estadísticas de reportes', () => {
    cy.get('[data-cy="reports-stats"]').should('be.visible')
    cy.get('[data-cy="total-reports"]').should('be.visible')
    cy.get('[data-cy="reports-this-month"]').should('be.visible')
    cy.get('[data-cy="average-generation-time"]').should('be.visible')
  })

  it('debe permitir eliminar reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    cy.get('[data-cy="delete-report"]').click()
    
    // Confirmar eliminación
    cy.get('[data-cy="confirm-delete"]').click()
    
    // Verificar éxito
    cy.checkNotification('Reporte eliminado exitosamente', 'success')
    
    // Verificar que se eliminó de la lista
    cy.visit('/reportes')
    cy.get('[data-cy="reports-list"]').should('not.contain', 'Reporte eliminado')
  })

  it('debe mostrar historial de versiones del reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar historial de versiones
    cy.get('[data-cy="report-versions"]').should('be.visible')
    cy.get('[data-cy="version-item"]').should('have.length.greaterThan', 1)
    
    // Verificar información de cada versión
    cy.get('[data-cy="version-item"]').first().within(() => {
      cy.get('[data-cy="version-number"]').should('be.visible')
      cy.get('[data-cy="version-date"]').should('be.visible')
      cy.get('[data-cy="version-changes"]').should('be.visible')
    })
  })

  it('debe permitir comparar versiones de reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Seleccionar versiones para comparar
    cy.get('[data-cy="version-checkbox"]').first().check()
    cy.get('[data-cy="version-checkbox"]').eq(1).check()
    
    // Comparar versiones
    cy.get('[data-cy="compare-versions"]').click()
    
    // Verificar vista de comparación
    cy.get('[data-cy="version-comparison"]').should('be.visible')
    cy.get('[data-cy="differences-highlighted"]').should('be.visible')
  })

  it('debe mostrar comentarios y anotaciones del reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar comentarios
    cy.get('[data-cy="report-comments"]').should('be.visible')
    cy.get('[data-cy="add-comment"]').should('be.visible')
    
    // Agregar comentario
    cy.get('[data-cy="add-comment"]').click()
    cy.get('[data-cy="comment-text"]').type('Excelente análisis de calidad')
    cy.get('[data-cy="save-comment"]').click()
    
    // Verificar que se agregó el comentario
    cy.get('[data-cy="comment-item"]').should('contain', 'Excelente análisis de calidad')
  })

  it('debe mostrar metadatos del reporte', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Verificar metadatos
    cy.get('[data-cy="report-metadata"]').should('be.visible')
    cy.get('[data-cy="generation-date"]').should('be.visible')
    cy.get('[data-cy="generation-time"]').should('be.visible')
    cy.get('[data-cy="data-source"]').should('be.visible')
    cy.get('[data-cy="report-size"]').should('be.visible')
  })

  it('debe permitir marcar reporte como favorito', () => {
    cy.get('[data-cy="report-item"]').first().click()
    
    // Marcar como favorito
    cy.get('[data-cy="favorite-report"]').click()
    
    // Verificar que se marcó
    cy.get('[data-cy="favorite-report"]').should('have.class', 'favorited')
    
    // Verificar que aparece en favoritos
    cy.visit('/reportes/favoritos')
    cy.get('[data-cy="favorite-reports"]').should('contain', 'Reporte favorito')
  })

  it('debe mostrar paginación cuando hay muchos reportes', () => {
    // Simular muchos reportes
    cy.intercept('GET', '/api/reportes/', {
      statusCode: 200,
      body: {
        results: Array(25).fill().map((_, i) => ({
          id: i + 1,
          nombre: `Reporte ${i + 1}`,
          tipo: 'analisis-periodo',
          fecha_generacion: '2024-01-15T10:30:00Z'
        })),
        count: 100,
        next: '/api/reportes/?page=2',
        previous: null
      }
    }).as('reportsPage1')
    
    cy.visit('/reportes')
    cy.wait('@reportsPage1')
    
    // Verificar paginación
    cy.get('[data-cy="pagination"]').should('be.visible')
    cy.get('[data-cy="page-info"]').should('contain', '1 de 4')
    
    // Navegar a siguiente página
    cy.get('[data-cy="next-page"]').click()
    cy.get('[data-cy="page-info"]').should('contain', '2 de 4')
  })
})
