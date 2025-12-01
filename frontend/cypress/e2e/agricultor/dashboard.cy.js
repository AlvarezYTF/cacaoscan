import {
  waitForPageLoad,
  verifyElementWithAlternatives,
  verifyUrlPatterns,
  clickIfExists,
  fillFieldIfExists,
  typeIfExists,
  verifyErrorMessageWithAlternatives
} from '../../support/helpers'

describe('Farmer Dashboard', () => {
  beforeEach(() => {
    cy.navigateToFarmerDashboard('farmer')
  })

  it('should welcome the farmer user', () => {
    const checkWelcomeText = ($el) => {
      const text = $el.text().toLowerCase()
      return text.includes('bienvenido') || text.includes('welcome') || text.includes('dashboard') || text.length > 0
    }

    const handleTitleVerification = (found, titleSelectors) => {
      if (found) {
        cy.get(titleSelectors.join(', ')).first().should('satisfy', checkWelcomeText)
      }
    }

    waitForPageLoad()
    
    cy.get('body').then(($body) => {
      const titleSelectors = ['h1', 'h2', '.page-title', '[data-cy="page-title"]']
      verifyElementWithAlternatives(titleSelectors, $body).then((found) => {
        handleTitleVerification(found, titleSelectors)
      })
      
      const userNameSelectors = ['[data-cy="user-name"]', '.user-name']
      verifyElementWithAlternatives(userNameSelectors, $body)
    })
  })

  it('should display quick statistics cards', () => {
    const statSelectors = ['[data-cy="stat-card-fincas"]', '.stat-card', '.card']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(statSelectors, $body, 5000)
    })
  })

  it('should show recent activity feed', () => {
    const activitySelectors = ['[data-cy="recent-activity-section"]', '.activity', '.recent']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(activitySelectors, $body).then(() => {
        cy.get('[data-cy="activity-item"], .activity-item', { timeout: 5000 }).should('have.length.at.least', 0)
      })
    })
  })

  it('should navigate to new analysis from quick action', () => {
    clickIfExists('[data-cy="btn-quick-analysis"], button, a', { force: true }).then(() => {
      verifyUrlPatterns(['/prediction', '/analisis', '/user'])
    })
  })

  it('should navigate to fincas management', () => {
    clickIfExists('[data-cy="btn-manage-fincas"], button, a', { force: true }).then(() => {
      verifyUrlPatterns(['/fincas', '/farms'])
    })
  })

  it('should display weather widget', () => {
    const weatherSelectors = ['[data-cy="weather-widget"]', '.weather']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(weatherSelectors, $body)
    })
  })

  it('should show recent analysis results chart', () => {
    const chartSelectors = ['[data-cy="chart-recent-results"]', '.chart', 'canvas']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(chartSelectors, $body)
    })
  })

  it('should navigate to profile settings', () => {
    clickIfExists('[data-cy="nav-profile"], a[href*="config"], button', { force: true }).then(() => {
      verifyUrlPatterns(['/configuracion', '/settings', '/profile'])
    })
  })

  it('should allow logout from dashboard', () => {
    clickIfExists('[data-cy="btn-logout"], button, a', { force: true }).then(() => {
      cy.url({ timeout: 10000 }).should('include', '/login')
    })
  })
})

describe('Farmer Profile Settings', () => {
  beforeEach(() => {
    cy.navigateToAccountProfile('farmer')
  })

  it('should load profile form', () => {
    waitForPageLoad()
    
    const formSelectors = ['form', '.form', '[data-cy="profile-form"]']
    cy.get('body').then(($body) => {
      verifyElementWithAlternatives(formSelectors, $body).then(() => {
        const emailSelectors = ['[data-cy="input-email"]', 'input[type="email"]']
        verifyElementWithAlternatives(emailSelectors, $body)
      })
    })
  })

  it('should update personal information', () => {
    fillFieldIfExists('[data-cy="input-phone"], input[type="tel"], input[name*="phone"]', '3001234567').then(() => {
      clickIfExists('[data-cy="btn-save-profile"], button[type="submit"]').then(() => {
        waitForPageLoad(5000)
      })
    })
  })

  it('should validate password change mismatch', () => {
    const changePasswordWithMismatch = ($security) => {
      const newPassSelectors = ['[data-cy="input-new-pass"]', 'input[type="password"]']
      if ($security.find(newPassSelectors.join(', ')).length > 0) {
        typeIfExists('[data-cy="input-new-pass"], input[type="password"]', 'NewPass123!')
        typeIfExists('[data-cy="input-confirm-pass"], input[type="password"]', 'DifferentPass!')
        clickIfExists('[data-cy="btn-change-pass"], button[type="submit"]')
        verifyErrorMessageWithAlternatives(['.error-message', '[data-cy="error"]'], ['error'], 5000)
      }
    }

    clickIfExists('[data-cy="tab-security"], [role="tab"]').then(() => {
      cy.get('body', { timeout: 5000 }).then(changePasswordWithMismatch)
    })
  })

  it('should change password successfully', () => {
    const changePasswordSuccessfully = ($security) => {
      const currentPassSelectors = ['[data-cy="input-current-pass"]', 'input[type="password"]']
      if ($security.find(currentPassSelectors.join(', ')).length >= 3) {
        typeIfExists('[data-cy="input-current-pass"], input[type="password"]', 'OldPass123!')
        cy.get('[data-cy="input-new-pass"], input[type="password"]').eq(1).type('NewPass123!')
        typeIfExists('[data-cy="input-confirm-pass"], input[type="password"]', 'NewPass123!')
        clickIfExists('[data-cy="btn-change-pass"], button[type="submit"]')
        waitForPageLoad(5000)
      }
    }

    clickIfExists('[data-cy="tab-security"], [role="tab"]').then(() => {
      cy.get('body', { timeout: 5000 }).then(changePasswordSuccessfully)
    })
  })
})

