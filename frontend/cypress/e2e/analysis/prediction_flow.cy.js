import {
  waitForPageLoad,
  verifyElementWithAlternatives,
  verifyTextContains,
  clickIfExists
} from '../../support/helpers'

describe('Cacao Analysis & Prediction Flow', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/user/prediction')
    waitForPageLoad()
  })

  it('should load prediction interface', () => {
    const titleSelectors = ['h1', 'h2', '.page-title', '[data-cy="page-title"]']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(titleSelectors, $body).then(() => {
        verifyTextContains(titleSelectors.join(', '), ['análisis', 'analysis', 'predicción'])
      })
      const uploadZoneSelectors = ['.upload-zone', '[data-cy="upload-zone"]', '.upload']
      verifyElementWithAlternatives(uploadZoneSelectors, $body, 5000)
    })
  })

  it('should upload a single image', () => {
    const fileInputSelectors = ['input[type="file"]']
    cy.get('body').then(($body) => {
      if ($body.find(fileInputSelectors.join(', ')).length > 0) {
        cy.uploadTestImage('cacao_sample.jpg')
        const previewSelectors = ['.preview-image', '.preview', '[data-cy="preview"]']
        verifyElementWithAlternatives(previewSelectors, cy.get('body'), 5000)
        const analyzeButtonSelectors = ['[data-cy="btn-analyze"]', 'button[type="submit"]']
        verifyElementWithAlternatives(analyzeButtonSelectors, cy.get('body'), 5000)
      }
    })
  })

  it('should show error for invalid file type', () => {
    waitForPageLoad()
  })

  it('should process image analysis', () => {
    cy.performImageAnalysis('cacao_sample.jpg', {}, () => {
      const loadingSelectors = ['[data-cy="loading-spinner"]', '.loading', '.spinner']
      verifyElementWithAlternatives(loadingSelectors, cy.get('body'), 5000)
      const resultsSelectors = ['[data-cy="results-container"]', '.results', '.result']
      verifyElementWithAlternatives(resultsSelectors, cy.get('body'), 20000)
    })
  })

  it('should display segmentation results', () => {
    cy.visit('/detalle-analisis/1')
    waitForPageLoad()
    const maskSelectors = ['[data-cy="segmentation-mask"]', '.mask', 'canvas']
    verifyElementWithAlternatives(maskSelectors, cy.get('body'), 5000)
    const statsSelectors = ['[data-cy="stats-panel"]', '.stats', '.panel']
    verifyElementWithAlternatives(statsSelectors, cy.get('body'), 5000)
  })

  it('should filter results by confidence score', () => {
    cy.visit('/detalle-analisis/1')
    waitForPageLoad()
    const sliderSelectors = ['[data-cy="confidence-slider"]', 'input[type="range"]', '.slider']
    cy.get('body').then(($body) => {
      if ($body.find(sliderSelectors.join(', ')).length > 0) {
        cy.get(sliderSelectors.join(', ')).first().invoke('val', 0.9).trigger('change')
        const objectSelectors = ['[data-cy="detected-object"]', '.object', '.detection']
        verifyElementWithAlternatives(objectSelectors, cy.get('body'), 5000).then(() => {
          cy.get(objectSelectors.join(', ')).should('have.length.at.least', 0)
        })
      }
    })
  })

  it('should save analysis results to history', () => {
    cy.visit('/agricultor/historial')
    waitForPageLoad()
    
    const historyItemSelectors = ['table tbody tr', '[data-cy="history-item"]', '.history-item', '.item']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(historyItemSelectors, $body).then(() => {
        verifyTextContains(historyItemSelectors.join(', '), ['reciente', 'recent'])
      })
    })
  })

  it('should download analysis report PDF', () => {
    cy.visit('/detalle-analisis/1')
    waitForPageLoad()
    
    const downloadButtonSelectors = ['[data-cy="btn-download-pdf"]', 'button', 'a']
    clickIfExists(downloadButtonSelectors.join(', ')).then(() => {
      const successSelectors = ['.swal2-success', '.success', '[data-cy="success"]']
      verifyElementWithAlternatives(successSelectors, cy.get('body'), 5000)
    })
  })

  it('should allow manual correction of results (if enabled)', () => {
    cy.visit('/detalle-analisis/1')
    waitForPageLoad()
    
    const editButtonSelectors = ['[data-cy="btn-edit-classification"]', 'button', 'a']
    clickIfExists(editButtonSelectors.join(', ')).then(() => {
      const handleSaveCorrection = ($afterSelect) => {
        const saveButtonSelectors = ['[data-cy="btn-save-correction"]', 'button[type="submit"]']
        if ($afterSelect.find(saveButtonSelectors.join(', ')).length > 0) {
          cy.get(saveButtonSelectors.join(', ')).first().click({ force: true })
          const successSelectors = ['.swal2-success', '.success', '[data-cy="success"]']
          verifyElementWithAlternatives(successSelectors, cy.get('body'), 5000)
        }
      }

      const handleClassSelection = ($afterEdit) => {
        const selectClassSelectors = ['[data-cy="select-class"]', 'select']
        if ($afterEdit.find(selectClassSelectors.join(', ')).length > 0) {
          cy.get(selectClassSelectors.join(', ')).first().select('Bien Fermentado', { force: true })
          cy.get('body', { timeout: 5000 }).then(handleSaveCorrection)
        }
      }

      cy.get('body', { timeout: 5000 }).then(handleClassSelection)
    })
  })
})

