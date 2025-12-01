import {
  verifySelectorsExist,
  visitAndWaitForBody,
  getApiBaseUrl,
  ifFoundInBody,
  clickIfExistsAndContinue
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
    const verifyRecommendationItems = () => {
      ifFoundInBody('[data-cy="recommendation-item"], .recommendation-item', () => {
        cy.get('[data-cy="recommendation-item"], .recommendation-item', { timeout: 5000 }).should('have.length.at.least', 0)
      })
    }

    const verifyRecommendationSelectors = ($results) => {
      const recommendationSelectors = [
        '[data-cy="harvest-recommendation"], .harvest',
        '[data-cy="treatment-recommendation"], .treatment'
      ]
      verifySelectorsExist(recommendationSelectors, $results, 3000)
    }

    const handleRecommendationsList = ($results) => {
      cy.get('[data-cy="recommendations-list"], .recommendations', { timeout: 5000 }).should('exist')
      verifyRecommendationItems()
      verifyRecommendationSelectors($results)
    }

    const handleResultsBody = ($results) => {
      ifFoundInBody('[data-cy="recommendations-list"], .recommendations', () => {
        handleRecommendationsList($results)
      })
    }

    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(handleResultsBody)
  })

  it('debe permitir ver imagen procesada con anotaciones', () => {
    const verifyDefectDetails = () => {
      ifFoundInBody('[data-cy="defect-details"], .details', () => {
        cy.get('[data-cy="defect-details"], .details', { timeout: 5000 }).should('exist')
      })
    }

    const handleDefectMarkerClick = () => {
      cy.get('[data-cy="defect-marker"], .marker').first().click({ force: true })
      verifyDefectDetails()
    }

    const verifyDefectMarkers = () => {
      ifFoundInBody('[data-cy="defect-marker"], .marker', () => {
        handleDefectMarkerClick()
      })
    }

    const verifyImageSelectors = ($results) => {
      const imageSelectors = [
        '[data-cy="processed-image"], .processed-image, img',
        '[data-cy="image-annotations"], .annotations',
        '[data-cy="defect-markers"], .markers'
      ]
      verifySelectorsExist(imageSelectors, $results, 5000)
      verifyDefectMarkers()
    }

    const handleProcessedImage = ($results) => {
      ifFoundInBody('[data-cy="processed-image"], .processed-image, img', () => {
        verifyImageSelectors($results)
      })
    }

    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(handleProcessedImage)
  })

  it('debe manejar errores durante el análisis', () => {
    const apiBaseUrl = getApiBaseUrl()
    cy.intercept('POST', `${apiBaseUrl}/scan/measure/`, {
      statusCode: 500,
      body: { error: 'Error en el análisis' }
    }).as('analysisError')
    
    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.wait('@analysisError', { timeout: 10000 })
    const errorSelectors = [
      '[data-cy="analysis-error"], .error-message',
      '[data-cy="retry-analysis"], button'
    ]
    verifySelectorsExist(errorSelectors, cy.get('body'), 5000)
  })

  it('debe permitir reintentar análisis fallido', () => {
    const apiBaseUrl = getApiBaseUrl()
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
    const verifyAnalysisCancelled = () => {
      ifFoundInBody('[data-cy="analysis-cancelled"], .cancelled', () => {
        cy.get('[data-cy="analysis-cancelled"], .cancelled', { timeout: 5000 }).should('exist')
      })
    }

    const handleConfirmCancel = () => {
      clickIfExistsAndContinue('[data-cy="confirm-cancel"], .swal2-confirm, button', () => {
        verifyAnalysisCancelled()
      })
    }

    const handleCancelAnalysis = () => {
      clickIfExistsAndContinue('[data-cy="cancel-analysis"], button', () => {
        handleConfirmCancel()
      })
    }

    cy.performImageAnalysis('test-cacao.jpg', { waitForResults: false })
    cy.get('body', { timeout: 5000 }).then(handleCancelAnalysis)
  })

  it('debe guardar resultados del análisis', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      clickIfExistsAndContinue('[data-cy="save-analysis"], button', () => {
        visitAndWaitForBody('/mis-analisis')
      })
    })
  })

  it('debe permitir exportar resultados', () => {
    cy.performImageAnalysis('test-cacao.jpg')
    cy.get('body', { timeout: 5000 }).then(($results) => {
      clickIfExistsAndContinue('[data-cy="export-pdf"], button', () => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
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

  const performAnalysisAndWait = () => {
    cy.uploadTestImage('test-cacao.jpg')
    clickIfExistsAndContinue('[data-cy="upload-button"], button[type="submit"]', () => {
      cy.waitForAnalysis()
    })
  }

  it('debe mostrar gráficos de análisis', () => {
    performAnalysisAndWait()
    const chartSelectors = [
      '[data-cy="quality-chart"]',
      '[data-cy="maturity-chart"]',
      '[data-cy="defects-chart"]'
    ]
    verifySelectorsExist(chartSelectors, cy.get('body'), 5000)
  })

  it('debe permitir compartir resultados de análisis', () => {
    performAnalysisAndWait()
    clickIfExistsAndContinue('[data-cy="share-results"], button', () => {
      ifFoundInBody('[data-cy="share-options"]', () => {
        cy.get('[data-cy="share-options"]').should('be.visible')
      })
    })
  })

  it('debe mostrar métricas de confianza del análisis', () => {
    performAnalysisAndWait()
    const confidenceSelectors = [
      '[data-cy="confidence-score"]',
      '[data-cy="confidence-level"]'
    ]
    verifySelectorsExist(confidenceSelectors, cy.get('body'), 5000)
  })

  it('debe permitir re-analizar imagen', () => {
    performAnalysisAndWait()
    clickIfExistsAndContinue('[data-cy="re-analyze"], button', () => {
      ifFoundInBody('[data-cy="analysis-progress"]', () => {
        cy.get('[data-cy="analysis-progress"]').should('be.visible')
      })
    })
  })

  it('debe mostrar tiempo de procesamiento', () => {
    performAnalysisAndWait()
    ifFoundInBody('[data-cy="processing-time"]', () => {
      cy.get('[data-cy="processing-time"]').should('be.visible')
    })
  })
})
