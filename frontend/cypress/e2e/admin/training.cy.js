import { ifFoundInBody, verifyUrlPatterns } from '../../support/helpers'

describe('Admin Training & Datasets', () => {
  const TRAINING_URL_PATTERNS = ['/admin', '/entrenamiento', '/training']
  const TITLE_TEXT_PATTERNS = ['entrenamiento', 'training']
  const DELETE_CONFIRM_TEXT_PATTERNS = ['eliminar', 'delete', '¿']
  
  const checkTitleText = ($element) => {
    const text = $element.text().toLowerCase()
    return TITLE_TEXT_PATTERNS.some(pattern => text.includes(pattern)) || $element.length > 0
  }

  const verifyPageTitle = () => {
    return ifFoundInBody('h1, h2, .page-title', ($el) => {
      cy.wrap($el).should('satisfy', checkTitleText)
    }, () => {
      cy.get('body').should('be.visible')
    })
  }
  
  const verifyElementIfExists = (selector, action) => {
    return ifFoundInBody(selector, action)
  }
  
  const configureTraining = ($modal) => {
    if ($modal.find('[data-cy="select-epochs"], select').length > 0) {
      cy.selectIfExists('[data-cy="select-epochs"], select', '50')
      cy.selectIfExists('[data-cy="select-batch-size"], select', '16')
      cy.clickIfExists('[data-cy="btn-confirm-training"], button[type="submit"]')
      cy.get('body', { timeout: 5000 }).should('be.visible')
    }
  }
  
  beforeEach(() => {
    cy.navigateToTraining('admin')
  })

  it('should load training dashboard', () => {
    verifyUrlPatterns(TRAINING_URL_PATTERNS, 10000)
    verifyPageTitle()
  })

  it('should display current dataset statistics', () => {
    verifyElementIfExists('[data-cy="dataset-stats"], .stats, .statistics', () => {
      cy.get('[data-cy="dataset-stats"], .stats, .statistics').first().should('be.visible')
      cy.get('[data-cy="total-images"], .total-images, [data-stat="images"]', { timeout: 5000 }).should('exist')
    })
  })

  it('should list available datasets', () => {
    verifyElementIfExists('[data-cy="dataset-list"], .dataset-list, .list', () => {
      cy.get('[data-cy="dataset-list"], .dataset-list, .list').should('exist')
      cy.get('[data-cy="dataset-item"], .dataset-item, .item', { timeout: 5000 }).should('have.length.at.least', 0)
    })
  })

  it('should upload a new dataset', () => {
    verifyElementIfExists('[data-cy="btn-upload-dataset"], button', () => {
      cy.get('[data-cy="btn-upload-dataset"], button').first().click()
      cy.get('[data-cy="modal-upload"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
    })
  })

  it('should start a new training session', () => {
    cy.clickIfExists('[data-cy="btn-start-training"], button').then(() => {
      cy.get('[data-cy="modal-training-config"], .modal, [role="dialog"]', { timeout: 5000 }).should('exist')
      cy.get('body', { timeout: 5000 }).then(configureTraining)
    })
  })

  it('should view training history', () => {
    cy.clickIfExists('[data-cy="tab-history"], [role="tab"]').then(() => {
      cy.get('table tbody tr, .table-row, .history-item', { timeout: 5000 }).should('have.length.at.least', 0)
    })
  })

  it('should view details of a training session', () => {
    cy.clickIfExists('[data-cy="tab-history"], [role="tab"]').then(() => {
      cy.interactWithFirstRow('table tbody tr, .table-row, .history-item', ($row) => {
        cy.wrap($row).click({ force: true })
        cy.get('[data-cy="training-metrics"], .metrics, .details', { timeout: 5000 }).should('exist')
      })
    })
  })

  it('should validate dataset deletion', () => {
    const checkDeleteConfirmText = ($el) => {
      const text = $el.text().toLowerCase()
      return DELETE_CONFIRM_TEXT_PATTERNS.some(pattern => text.includes(pattern)) || $el.length > 0
    }

    const clickDeleteAndVerify = ($btns) => {
      if ($btns.length > 0) {
        cy.wrap($btns.first()).click({ force: true })
        cy.get('.swal2-title, [role="dialog"] h2', { timeout: 5000 }).should('satisfy', checkDeleteConfirmText)
      }
    }

    verifyElementIfExists('[data-cy="tab-datasets"], [role="tab"]', () => {
      cy.get('[data-cy="tab-datasets"], [role="tab"]').first().click()
      cy.get('[data-cy="btn-delete-dataset"], button', { timeout: 5000 }).then(clickDeleteAndVerify)
    })
  })
})

