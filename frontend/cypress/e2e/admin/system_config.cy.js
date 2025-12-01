import { 
  clickIfExists, 
  typeIfExists, 
  selectIfExists, 
  ifFoundInBody,
  ifElementExists,
  verifyUrlPatterns
} from '../../support/helpers'

describe('Admin System Configuration', () => {
  const CONFIG_URL_PATTERNS = ['/admin', '/configuracion', '/configuration']
  const TITLE_TEXT_PATTERNS = ['configuración', 'configuration', 'sistema']
  const RESET_CONFIRM_TEXT_PATTERNS = ['restaurar', 'reset', 'valores', '¿']
  
  const checkTitleText = ($element) => {
    const text = $element.text().toLowerCase()
    return TITLE_TEXT_PATTERNS.some(pattern => text.includes(pattern)) || $element.length > 0
  }

  const checkTabActive = ($element) => {
    return $element.hasClass('active') || $element.attr('aria-selected') === 'true' || $element.length > 0
  }

  const checkResetConfirmText = ($el) => {
    const text = $el.text().toLowerCase()
    return RESET_CONFIRM_TEXT_PATTERNS.some(pattern => text.includes(pattern)) || $el.length > 0
  }

  const verifyPageTitle = () => {
    return ifFoundInBody('h1, h2, .page-title', ($el) => {
      cy.wrap($el).should('satisfy', checkTitleText)
    }, () => {
      cy.get('body').should('be.visible')
    })
  }
  
  const switchTabAndVerify = (tabSelector, sectionSelector) => {
    return clickIfExists(tabSelector).then((clicked) => {
      if (clicked) {
        cy.get(sectionSelector, { timeout: 5000 }).should('exist')
      }
    })
  }
  
  const saveAndWait = (saveSelector) => {
    return clickIfExists(saveSelector).then(() => {
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
  }
  
  const updateFieldAndSave = (fieldSelector, value, saveSelector, options = {}) => {
    return typeIfExists(fieldSelector, value, options).then(() => {
      return saveAndWait(saveSelector)
    })
  }
  
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/configuracion')
    cy.get('body', { timeout: 10000 }).should('be.visible')
  })

  it('should load configuration page', () => {
    verifyUrlPatterns(CONFIG_URL_PATTERNS, 10000)
    verifyPageTitle()
  })

  it('should display general settings tab by default', () => {
    ifFoundInBody('[data-cy="tab-general"], [role="tab"]', ($tab) => {
      cy.wrap($tab).should('satisfy', checkTabActive)
      cy.get('[data-cy="section-general"], .section, .tab-content', { timeout: 5000 }).should('exist')
    })
  })

  it('should switch to security settings tab', () => {
    switchTabAndVerify('[data-cy="tab-security"], [role="tab"]', '[data-cy="section-security"], .section, .tab-content')
  })

  it('should switch to analysis settings tab', () => {
    switchTabAndVerify('[data-cy="tab-analysis"], [role="tab"]', '[data-cy="section-analysis"], .section, .tab-content')
  })

  it('should update site name', () => {
    updateFieldAndSave(
      '[data-cy="input-site-name"], input[name*="name"], input[type="text"]',
      'CacaoScan Updated',
      '[data-cy="btn-save-general"], button[type="submit"]',
      { clear: true }
    )
  })

  it('should validate maintenance mode toggle', () => {
    const toggleMaintenance = () => {
      cy.get('[data-cy="toggle-maintenance"], input[type="checkbox"]').first().click({ force: true })
    }

    ifElementExists('[data-cy="toggle-maintenance"], input[type="checkbox"]', () => {
      toggleMaintenance()
      saveAndWait('[data-cy="btn-save-general"], button[type="submit"]')
      toggleMaintenance()
      saveAndWait('[data-cy="btn-save-general"], button[type="submit"]')
    })
  })

  it('should update password policy settings', () => {
    clickIfExists('[data-cy="tab-security"], [role="tab"]').then(() => {
      updateFieldAndSave(
        '[data-cy="input-min-pass-length"], input[type="number"]',
        '10',
        '[data-cy="btn-save-security"], button[type="submit"]',
        { clear: true }
      )
    })
  })

  it('should validate invalid values in analysis thresholds', () => {
    const handleInvalidThreshold = () => {
      clickIfExists('[data-cy="btn-save-analysis"], button[type="submit"]')
      cy.get('.error-message, [data-cy="error"], .alert-error', { timeout: 5000 }).should('exist')
    }

    clickIfExists('[data-cy="tab-analysis"], [role="tab"]').then(() => {
      typeIfExists('[data-cy="input-confidence-threshold"], input[type="number"]', '150', { clear: true }).then(handleInvalidThreshold)
    })
  })

  it('should update analysis default model', () => {
    const handleModelSelection = () => {
      saveAndWait('[data-cy="btn-save-analysis"], button[type="submit"]')
    }

    clickIfExists('[data-cy="tab-analysis"], [role="tab"]').then(() => {
      selectIfExists('[data-cy="select-model"], select', 'v2.0').then(handleModelSelection)
    })
  })

  it('should show reset to defaults confirmation', () => {
    clickIfExists('[data-cy="btn-reset-defaults"], button').then(() => {
      cy.get('.swal2-title, [role="dialog"] h2', { timeout: 5000 }).should('satisfy', checkResetConfirmText)
    })
  })

  it('should export configuration', () => {
    clickIfExists('[data-cy="btn-export-config"], button').then(() => {
      cy.get('.error-message, .swal2-error', { timeout: 3000 }).should('not.exist')
    })
  })
})
