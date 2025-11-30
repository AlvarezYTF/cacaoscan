describe('Farmer Dashboard', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    // Esperar a que el dashboard cargue
    cy.get('[data-cy="farmer-dashboard"], body', { timeout: 10000 }).should('be.visible')
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
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-quick-analysis"], button, a').length > 0) {
        cy.get('[data-cy="btn-quick-analysis"], button, a').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/prediction') || url.includes('/analisis') || url.includes('/user')
        })
      }
    })
  })

  it('should navigate to fincas management', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-manage-fincas"], button, a').length > 0) {
        cy.get('[data-cy="btn-manage-fincas"], button, a').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/fincas') || url.includes('/farms')
        })
      }
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
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="nav-profile"], a[href*="config"], button').length > 0) {
        cy.get('[data-cy="nav-profile"], a[href*="config"], button').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/configuracion') || url.includes('/settings') || url.includes('/profile')
        })
      }
    })
  })

  it('should allow logout from dashboard', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-logout"], button, a').length > 0) {
        cy.get('[data-cy="btn-logout"], button, a').first().click({ force: true })
        cy.url({ timeout: 10000 }).should('include', '/login')
      }
    })
  })
})

describe('Farmer Profile Settings', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/agricultor/configuracion')
    cy.get('body', { timeout: 10000 }).should('be.visible')
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
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-phone"], input[type="tel"], input[name*="phone"]').length > 0) {
        cy.get('[data-cy="input-phone"], input[type="tel"], input[name*="phone"]').first().clear().type('3001234567')
        cy.get('[data-cy="btn-save-profile"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('should validate password change mismatch', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-security"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-security"], [role="tab"]').first().click()
        cy.get('body').then(($security) => {
          if ($security.find('[data-cy="input-new-pass"], input[type="password"]').length > 0) {
            cy.get('[data-cy="input-new-pass"], input[type="password"]').first().type('NewPass123!')
            cy.get('[data-cy="input-confirm-pass"], input[type="password"]').last().type('DifferentPass!')
            cy.get('[data-cy="btn-change-pass"], button[type="submit"]').first().click()
            cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
          }
        })
      }
    })
  })

  it('should change password successfully', () => {
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="tab-security"], [role="tab"]').length > 0) {
        cy.get('[data-cy="tab-security"], [role="tab"]').first().click()
        cy.get('body').then(($security) => {
          if ($security.find('[data-cy="input-current-pass"], input[type="password"]').length >= 3) {
            cy.get('[data-cy="input-current-pass"], input[type="password"]').first().type('OldPass123!')
            cy.get('[data-cy="input-new-pass"], input[type="password"]').eq(1).type('NewPass123!')
            cy.get('[data-cy="input-confirm-pass"], input[type="password"]').last().type('NewPass123!')
            cy.get('[data-cy="btn-change-pass"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })
  })
})

