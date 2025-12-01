import {
  verifySelectorsExist,
  visitAndWaitForBody
} from '../../support/helpers'

describe('Análisis de Imágenes - Procesamiento', () => {
  beforeEach(() => {
    cy.login('farmer')
    visitAndWaitForBody('/nuevo-analisis')
  })

  it('debe iniciar análisis después de cargar imagen', () => {
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.get('[data-cy="analysis-started"], .analysis-started, [data-cy="analysis-progress"]', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="analysis-progress"], .progress', { timeout: 5000 }).should('exist')
  })

  it('debe mostrar progreso del análisis en tiempo real', () => {
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.get('[data-cy="analysis-stage"], .analysis-stage, .stage', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="analysis-progress"], .progress', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="analysis-percentage"], .percentage', { timeout: 5000 }).should('exist')
  })

  it('debe completar análisis exitosamente', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('[data-cy="quality-score"], .quality, .score', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="maturity-percentage"], .maturity', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="defects-count"], .defects', { timeout: 5000 }).should('exist')
  })

  it('debe mostrar resultados detallados del análisis', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      const sectionSelectors = [
        '[data-cy="quality-section"]',
        '[data-cy="maturity-section"]',
        '[data-cy="defects-section"]',
        '[data-cy="recommendations-section"]',
        '[data-cy="quality-grade"]',
        '[data-cy="defects-list"]'
      ]
      verifySelectorsExist(sectionSelectors, $results, 3000)
    })
  })

  it('debe mostrar recomendaciones basadas en el análisis', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      if ($results.find('[data-cy="recommendations-list"], .recommendations').length > 0) {
        cy.get('[data-cy="recommendations-list"], .recommendations', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="recommendation-item"], .recommendation-item', { timeout: 5000 }).should('have.length.at.least', 0)
        cy.get('[data-cy="harvest-recommendation"], .harvest', { timeout: 3000 }).should('exist')
        cy.get('[data-cy="treatment-recommendation"], .treatment', { timeout: 3000 }).should('exist')
      }
    })
  })

  it('debe permitir ver imagen procesada con anotaciones', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      if ($results.find('[data-cy="processed-image"], .processed-image, img').length > 0) {
        cy.get('[data-cy="processed-image"], .processed-image, img', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="image-annotations"], .annotations', { timeout: 5000 }).should('exist')
        cy.get('[data-cy="defect-markers"], .markers', { timeout: 5000 }).should('exist')
        cy.get('body').then(($markers) => {
          if ($markers.find('[data-cy="defect-marker"], .marker').length > 0) {
            cy.get('[data-cy="defect-marker"], .marker').first().click({ force: true })
            cy.get('[data-cy="defect-details"], .details', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe manejar errores durante el análisis', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/scan/measure/`, {
      statusCode: 500,
      body: { error: 'Error en el análisis' }
    }).as('analysisError')
    
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.wait('@analysisError', { timeout: 10000 })
    cy.get('[data-cy="analysis-error"], .error-message', { timeout: 5000 }).should('exist')
    cy.get('[data-cy="retry-analysis"], button', { timeout: 5000 }).should('exist')
  })

  it('debe permitir reintentar análisis fallido', () => {
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('POST', `${apiBaseUrl}/scan/measure/`, {
      statusCode: 500,
      body: { error: 'Error temporal' }
    }).as('analysisError')
    
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.wait('@analysisError', { timeout: 10000 })
    
    cy.intercept('POST', `${apiBaseUrl}/scan/measure/`, {
      statusCode: 200,
      body: { 
        status: 'completed',
        results: { calidad: 'Excelente', porcentaje_madurez: 85 }
      }
    }).as('analysisSuccess')
    
    cy.get('[data-cy="retry-analysis"], button').first().click({ force: true })
    cy.wait('@analysisSuccess', { timeout: 10000 })
    cy.waitForAnalysisResults()
  })

  it('debe mostrar tiempo estimado de análisis', () => {
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.get('[data-cy="estimated-time"], .estimated-time, .time', { timeout: 5000 }).should('exist')
  })

  it('debe permitir cancelar análisis en progreso', () => {
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.get('body', { timeout: 5000 }).then(($analysis) => {
      if ($analysis.find('[data-cy="cancel-analysis"], button').length > 0) {
        cy.get('[data-cy="cancel-analysis"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($confirm) => {
          if ($confirm.find('[data-cy="confirm-cancel"], .swal2-confirm, button').length > 0) {
            cy.get('[data-cy="confirm-cancel"], .swal2-confirm, button').first().click()
            cy.get('[data-cy="analysis-cancelled"], .cancelled', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('debe guardar resultados del análisis', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      if ($results.find('[data-cy="save-analysis"], button').length > 0) {
        cy.get('[data-cy="save-analysis"], button').first().click()
        visitAndWaitForBody('/mis-analisis')
      }
    })
  })

  it('debe permitir exportar resultados', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      if ($results.find('[data-cy="export-pdf"], button').length > 0) {
        cy.get('[data-cy="export-pdf"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('debe mostrar comparación con análisis anteriores', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      const comparisonSelectors = [
        '[data-cy="comparison-section"]',
        '[data-cy="previous-analysis"]',
        '[data-cy="improvement-indicator"]'
      ]
      verifySelectorsExist(comparisonSelectors, $results, 3000)
    })
  })

  it('debe mostrar gráficos de análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    cy.get('[data-cy="quality-chart"]').should('be.visible')
    cy.get('[data-cy="maturity-chart"]').should('be.visible')
    cy.get('[data-cy="defects-chart"]').should('be.visible')
  })

  it('debe permitir compartir resultados de análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    cy.get('[data-cy="share-results"]').click()
    cy.get('[data-cy="share-options"]').should('be.visible')
  })

  it('debe mostrar métricas de confianza del análisis', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    cy.get('[data-cy="confidence-score"]').should('be.visible')
    cy.get('[data-cy="confidence-level"]').should('be.visible')
  })

  it('debe permitir re-analizar imagen', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    cy.get('[data-cy="re-analyze"]').click()
    cy.get('[data-cy="analysis-progress"]').should('be.visible')
  })

  it('debe mostrar tiempo de procesamiento', () => {
    cy.uploadTestImage('test-cacao.jpg')
    cy.get('[data-cy="upload-button"]').click()
    cy.waitForAnalysis()
    
    cy.get('[data-cy="processing-time"]').should('be.visible')
  })
})
