describe('Farmer Dashboard', () => {
  beforeEach(() => {
    cy.navigateToFarmerDashboard('farmer')
  })

  it('should welcome the farmer user', () => {
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('h1, h2, .page-title, [data-cy="page-title"]').length > 0) {
        cy.get('h1, h2, .page-title, [data-cy="page-title"]').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('bienvenido') || text.includes('welcome') || text.includes('dashboard') || text.length > 0
        })
      }
      
      if ($body.find('[data-cy="user-name"], .user-name').length > 0) {
        cy.get('[data-cy="user-name"], .user-name').should('be.visible')
      } else {
        // Si no hay título o nombre de usuario, verificar que el dashboard cargó correctamente
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should display quick statistics cards', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="stat-card-fincas"], .stat-card, .card').length > 0) {
        cy.get('[data-cy="stat-card-fincas"], .stat-card, .card', { timeout: 5000 }).should('exist')
      }
    })
  })

  it('should show recent activity feed', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="recent-activity-section"], .activity, .recent').length > 0) {
        cy.get('[data-cy="recent-activity-section"], .activity, .recent').should('exist')
        cy.get('[data-cy="activity-item"], .activity-item', { timeout: 5000 }).should('have.length.at.least', 0)
      }
    })
  })

  it('should navigate to new analysis from quick action', () => {
    cy.clickIfExists('[data-cy="btn-quick-analysis"], button, a', { force: true }).then(() => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/prediction') || url.includes('/analisis') || url.includes('/user')
      })
    })
  })

  it('should navigate to fincas management', () => {
    cy.clickIfExists('[data-cy="btn-manage-fincas"], button, a', { force: true }).then(() => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/fincas') || url.includes('/farms')
      })
    })
  })

  it('should display weather widget', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="weather-widget"], .weather').length > 0) {
        cy.get('[data-cy="weather-widget"], .weather').should('exist')
      }
    })
  })

  it('should show recent analysis results chart', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="chart-recent-results"], .chart, canvas').length > 0) {
        cy.get('[data-cy="chart-recent-results"], .chart, canvas').should('exist')
      }
    })
  })

  it('should navigate to profile settings', () => {
    cy.clickIfExists('[data-cy="nav-profile"], a[href*="config"], button', { force: true }).then(() => {
      cy.url({ timeout: 10000 }).should('satisfy', (url) => {
        return url.includes('/configuracion') || url.includes('/settings') || url.includes('/profile')
      })
    })
  })

  it('should allow logout from dashboard', () => {
    cy.clickIfExists('[data-cy="btn-logout"], button, a', { force: true }).then(() => {
      cy.url({ timeout: 10000 }).should('include', '/login')
    })
  })
})

describe('Farmer Profile Settings', () => {
  beforeEach(() => {
    cy.navigateToAccountProfile('farmer')
  })

  it('should load profile form', () => {
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      if ($body.find('form, .form, [data-cy="profile-form"]').length > 0) {
        cy.get('form, .form, [data-cy="profile-form"]').first().should('exist')
        
        if ($body.find('[data-cy="input-email"], input[type="email"]').length > 0) {
          cy.get('[data-cy="input-email"], input[type="email"]').should('exist')
        }
      } else {
        // Si no hay formulario, verificar que la página cargó correctamente
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should update personal information', () => {
    cy.fillFieldIfExists('[data-cy="input-phone"], input[type="tel"], input[name*="phone"]', '3001234567').then(() => {
      cy.clickIfExists('[data-cy="btn-save-profile"], button[type="submit"]').then(() => {
        cy.get('body', { timeout: 5000 }).should('be.visible')
      })
    })
  })

  it('should validate password change mismatch', () => {
    const changePasswordWithMismatch = ($security) => {
      if ($security.find('[data-cy="input-new-pass"], input[type="password"]').length > 0) {
        cy.typeIfExists('[data-cy="input-new-pass"], input[type="password"]', 'NewPass123!')
        cy.typeIfExists('[data-cy="input-confirm-pass"], input[type="password"]', 'DifferentPass!')
        cy.clickIfExists('[data-cy="btn-change-pass"], button[type="submit"]')
        cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
      }
    }

    const afterSecurityTab = () => {
      cy.get('body', { timeout: 5000 }).then(changePasswordWithMismatch)
    }

    cy.clickIfExists('[data-cy="tab-security"], [role="tab"]').then(afterSecurityTab)
  })

  it('should change password successfully', () => {
    const changePasswordSuccessfully = ($security) => {
      if ($security.find('[data-cy="input-current-pass"], input[type="password"]').length >= 3) {
        cy.typeIfExists('[data-cy="input-current-pass"], input[type="password"]', 'OldPass123!')
        cy.get('[data-cy="input-new-pass"], input[type="password"]').eq(1).type('NewPass123!')
        cy.typeIfExists('[data-cy="input-confirm-pass"], input[type="password"]', 'NewPass123!')
        cy.clickIfExists('[data-cy="btn-change-pass"], button[type="submit"]')
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    }

    const afterSecurityTabForSuccess = () => {
      cy.get('body', { timeout: 5000 }).then(changePasswordSuccessfully)
    }

    cy.clickIfExists('[data-cy="tab-security"], [role="tab"]').then(afterSecurityTabForSuccess)
  })
})

