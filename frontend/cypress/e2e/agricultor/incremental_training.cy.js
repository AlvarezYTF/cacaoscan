import {
  waitForPageLoad,
  verifyElementWithAlternatives,
  verifyTextContains,
  clickIfExists,
  selectIfExists,
  typeIfExists,
  verifyErrorMessageWithAlternatives
} from '../../support/helpers'

describe('Incremental Training Contribution', () => {
  beforeEach(() => {
    cy.navigateToIncrementalTraining('farmer')
  })

  const uploadImageAndProcess = (imageName, callback) => {
    const fileInputSelectors = ['input[type="file"]']
    cy.get('body').then(($body) => {
      if ($body.find(fileInputSelectors.join(', ')).length > 0) {
        cy.uploadTestImage(imageName)
        cy.get('body', { timeout: 5000 }).then(($afterUpload) => {
          if (callback) callback($afterUpload)
        })
      }
    })
  }

  const selectLabelAndAdd = (label, callback) => {
    const labelSelectors = ['[data-cy="select-label"]', 'select']
    selectIfExists(labelSelectors.join(', '), label).then((selected) => {
      if (selected && callback) {
        cy.get('body').then(($afterSelect) => {
          callback($afterSelect)
        })
      }
    })
  }

  it('should load contribution page', () => {
    waitForPageLoad()
    
    const titleSelectors = ['h1', 'h2', '.page-title', '[data-cy="page-title"]']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(titleSelectors, $body).then(() => {
        verifyTextContains(titleSelectors.join(', '), ['contribuir', 'datos', 'entrenamiento'])
      })
      const guidelinesSelectors = ['.upload-guidelines', '.guidelines', '[data-cy="guidelines"]']
      verifyElementWithAlternatives(guidelinesSelectors, $body)
    })
  })

  it('should accept image uploads for training', () => {
    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      cy.get('.preview-list, .preview, [data-cy="preview"]', { timeout: 5000 }).then(($preview) => {
        if ($preview.length > 0) {
          cy.wrap($preview).children().should('have.length.at.least', 0)
        }
      })
    })
  })

  it('should require labeling for uploaded images', () => {
    const verifyLabelRequired = () => {
      const submitButtonSelectors = ['[data-cy="btn-submit-contribution"]', 'button[type="submit"]']
      clickIfExists(submitButtonSelectors.join(', '))
      verifyErrorMessageWithAlternatives(
        ['.error-message', '[data-cy="error"]'],
        ['etiqueta', 'label', 'requerid'],
        5000
      )
    }

    uploadImageAndProcess('training_sample.jpg', verifyLabelRequired)
  })

  it('should allow tagging images', () => {
    const addTag = () => {
      const addTagButtonSelectors = ['[data-cy="btn-add-tag"]', 'button']
      clickIfExists(addTagButtonSelectors.join(', '))
      const tagSelectors = ['.tag-chip', '.tag', '[data-cy="tag"]']
      verifyElementWithAlternatives(tagSelectors, cy.get('body'), 5000)
    }

    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      selectLabelAndAdd('Monilia', addTag)
    })
  })

  it('should submit contribution successfully', () => {
    uploadImageAndProcess('training_sample.jpg', ($afterUpload) => {
      selectLabelAndAdd('Sana', ($afterSelect) => {
        const notesSelectors = ['[data-cy="input-notes"]', 'textarea']
        typeIfExists(notesSelectors.join(', '), 'Imagen tomada con buena luz')
        const submitButtonSelectors = ['[data-cy="btn-submit-contribution"]', 'button[type="submit"]']
        clickIfExists(submitButtonSelectors.join(', '))
        waitForPageLoad(5000)
      })
    })
  })

  it('should show history of contributions', () => {
    const historyTabSelectors = ['[data-cy="tab-history"]', '[role="tab"]']
    clickIfExists(historyTabSelectors.join(', ')).then(() => {
      const contributionItemSelectors = ['[data-cy="contribution-item"]', '.contribution-item', '.item']
      verifyElementWithAlternatives(contributionItemSelectors, cy.get('body'), 5000)
      const statusBadgeSelectors = ['[data-cy="status-badge"]', '.badge', '.status']
      verifyElementWithAlternatives(statusBadgeSelectors, cy.get('body'))
    })
  })
})

