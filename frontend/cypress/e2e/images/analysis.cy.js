describe('Análisis de Imágenes - Procesamiento', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/nuevo-analisis')
  })

  it('debe iniciar análisis después de cargar imagen', () => {
    // Cargar imagen
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    // Verificar que se inicia el análisis
    cy.get('[data-cy="analysis-started"]')
      .should('be.visible')
      .and('contain', 'Análisis iniciado')
    
    // Verificar indicador de progreso
    cy.get('[data-cy="analysis-progress"]').should('be.visible')
  })

  it('debe mostrar progreso del análisis en tiempo real', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    // Verificar etapas del análisis
    cy.get('[data-cy="analysis-stage"]').should('contain', 'Procesando imagen')
    
    // Simular progreso
    cy.get('[data-cy="analysis-progress"]').should('be.visible')
    cy.get('[data-cy="analysis-percentage"]').should('contain', '%')
  })

  it('debe completar análisis exitosamente', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    // Esperar que termine el análisis
    cy.waitForAnalysis(30000)
    
    // Verificar resultados
    cy.get('[data-cy="analysis-results"]').should('be.visible')
    cy.get('[data-cy="quality-score"]').should('be.visible')
    cy.get('[data-cy="maturity-percentage"]').should('be.visible')
    cy.get('[data-cy="defects-count"]').should('be.visible')
  })

  it('debe mostrar resultados detallados del análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Verificar secciones de resultados
    cy.get('[data-cy="quality-section"]').should('be.visible')
    cy.get('[data-cy="maturity-section"]').should('be.visible')
    cy.get('[data-cy="defects-section"]').should('be.visible')
    cy.get('[data-cy="recommendations-section"]').should('be.visible')
    
    // Verificar valores específicos
    cy.get('[data-cy="quality-grade"]').should('be.visible')
    // Use an anchored, bounded regex on the element text to avoid super-linear
    // backtracking on pathological inputs. Limit to 1-3 digits (0-999%).
    cy.get('[data-cy="maturity-percentage"]').invoke('text').should('match', /^\d{1,3}%$/)
    cy.get('[data-cy="defects-list"]').should('be.visible')
  })

  it('debe mostrar recomendaciones basadas en el análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Verificar recomendaciones
    cy.get('[data-cy="recommendations-list"]').should('be.visible')
    cy.get('[data-cy="recommendation-item"]').should('have.length.greaterThan', 0)
    
    // Verificar tipos de recomendaciones
    cy.get('[data-cy="harvest-recommendation"]').should('be.visible')
    cy.get('[data-cy="treatment-recommendation"]').should('be.visible')
  })

  it('debe permitir ver imagen procesada con anotaciones', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Verificar imagen procesada
    cy.get('[data-cy="processed-image"]').should('be.visible')
    
    // Verificar anotaciones
    cy.get('[data-cy="image-annotations"]').should('be.visible')
    cy.get('[data-cy="defect-markers"]').should('be.visible')
    
    // Interactuar con anotaciones
    cy.get('[data-cy="defect-marker"]').first().click()
    cy.get('[data-cy="defect-details"]').should('be.visible')
  })

  it('debe manejar errores durante el análisis', () => {
    // Simular error en el análisis
    cy.intercept('POST', '/api/scan/measure/', {
      statusCode: 500,
      body: { error: 'Error en el análisis' }
    }).as('analysisError')
    
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    cy.wait('@analysisError')
    
    // Verificar mensaje de error
    cy.get('[data-cy="analysis-error"]')
      .should('be.visible')
      .and('contain', 'Error durante el análisis')
    
    // Verificar opción de reintentar
    cy.get('[data-cy="retry-analysis"]').should('be.visible')
  })

  it('debe permitir reintentar análisis fallido', () => {
    // Primero simular error
    cy.intercept('POST', '/api/scan/measure/', {
      statusCode: 500,
      body: { error: 'Error temporal' }
    }).as('analysisError')
    
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.wait('@analysisError')
    
    // Luego simular éxito en reintento
    cy.intercept('POST', '/api/scan/measure/', {
      statusCode: 200,
      body: { 
        status: 'completed',
        results: { calidad: 'Excelente', porcentaje_madurez: 85 }
      }
    }).as('analysisSuccess')
    
    cy.get('[data-cy="retry-analysis"]').click()
    cy.wait('@analysisSuccess')
    
    // Verificar que el análisis se completó
    cy.get('[data-cy="analysis-results"]').should('be.visible')
  })

  it('debe mostrar tiempo estimado de análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    // Verificar tiempo estimado
    cy.get('[data-cy="estimated-time"]')
      .should('be.visible')
      .and('contain', 'minutos')
  })

  it('debe permitir cancelar análisis en progreso', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    
    // Cancelar análisis
    cy.get('[data-cy="cancel-analysis"]').click()
    
    // Confirmar cancelación
    cy.get('[data-cy="confirm-cancel"]').click()
    
    // Verificar que se canceló
    cy.get('[data-cy="analysis-cancelled"]')
      .should('be.visible')
      .and('contain', 'Análisis cancelado')
  })

  it('debe guardar resultados del análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Guardar análisis
    cy.get('[data-cy="save-analysis"]').click()
    
    // Verificar mensaje de éxito
    cy.get('[data-cy="save-success"]')
      .should('be.visible')
      .and('contain', 'Análisis guardado')
    
    // Verificar que aparece en historial
    cy.visit('/mis-analisis')
    cy.get('[data-cy="analysis-history"]').should('contain', 'test-cacao.jpg')
  })

  it('debe permitir exportar resultados', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Exportar como PDF
    cy.get('[data-cy="export-pdf"]').click()
    
    // Verificar descarga
    cy.verifyDownload('analisis-cacao.pdf')
    
    // Exportar como Excel
    cy.get('[data-cy="export-excel"]').click()
    cy.verifyDownload('analisis-cacao.xlsx')
  })

  it('debe mostrar comparación con análisis anteriores', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    // Verificar comparación
    cy.get('[data-cy="comparison-section"]').should('be.visible')
    cy.get('[data-cy="previous-analysis"]').should('be.visible')
    cy.get('[data-cy="improvement-indicator"]').should('be.visible')
  })
})
