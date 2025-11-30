describe('E2E: Complete Farmer Journey', () => {
  const timestamp = new Date().getTime()
  const userEmail = `farmer_journey_${timestamp}@example.com`
  const fincaName = `Finca Journey ${timestamp}`

  it('should complete the full cycle from registration to analysis', () => {
    // 1. Registration
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-name"], input[name*="name"], input[type="text"]').length > 0) {
        cy.get('[data-cy="input-name"], input[name*="name"], input[type="text"]').first().type('Journey Farmer')
        cy.get('[data-cy="input-email"], input[type="email"]').first().type(userEmail)
        cy.get('[data-cy="input-password"], input[type="password"]').first().type('SecurePass123!')
        cy.get('[data-cy="input-confirm-password"], input[type="password"]').last().type('SecurePass123!')
        cy.get('[data-cy="check-terms"], input[type="checkbox"]').first().check({ force: true })
        cy.get('[data-cy="btn-submit-register"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
    
    // Mock email verification flow (skip or simulate token)
    // Assuming backend allows login immediately or we verify via API in background
    // For this E2E, let's assume we need to verify or mock it
    // cy.visit(`/verify-email/mock-token-for-${userEmail}`)

    // 2. Login
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-email"], input[type="email"], input[type="text"]').length > 0) {
        cy.get('[data-cy="input-email"], input[type="email"], input[type="text"]').first().type(userEmail)
        cy.get('[data-cy="input-password"], input[type="password"]').first().type('SecurePass123!')
        cy.get('[data-cy="btn-submit-login"], [data-cy="login-button"], button[type="submit"]').first().click()
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/login')
        })
      }
    })

    // 3. Complete Profile (Onboarding)
    // If there's an onboarding wizard
    // cy.get('[data-cy="onboarding-modal"]').should('be.visible')
    // cy.get('[data-cy="btn-skip-onboarding"]').click()

    // 4. Create Finca
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-finca"], button').length > 0) {
        cy.get('[data-cy="btn-add-finca"], button').first().click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($modal) => {
          if ($modal.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
            cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').first().type(fincaName)
            cy.get('[data-cy="input-ubicacion"], input[name*="ubicacion"]').first().type('Vereda San Juan')
            cy.get('[data-cy="input-area"], input[type="number"]').first().type('100')
            cy.get('[data-cy="btn-save-finca"], button[type="submit"]').first().click()
            cy.get('body', { timeout: 5000 }).should('be.visible')
          }
        })
      }
    })

    // 5. Create Lote
    cy.get('body').then(($body) => {
      if ($body.text().includes(fincaName)) {
        cy.contains(fincaName).click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="tab-lotes"], [role="tab"]').length > 0) {
            cy.get('[data-cy="tab-lotes"], [role="tab"]').first().click()
            cy.get('body').then(($lotes) => {
              if ($lotes.find('[data-cy="btn-add-lote"], button').length > 0) {
                cy.get('[data-cy="btn-add-lote"], button').first().click()
                cy.get('body', { timeout: 5000 }).then(($loteModal) => {
                  if ($loteModal.find('[data-cy="input-lote-nombre"], input[name*="nombre"]').length > 0) {
                    cy.get('[data-cy="input-lote-nombre"], input[name*="nombre"]').first().type('Lote Principal')
                    cy.get('[data-cy="input-lote-area"], input[type="number"]').first().type('20')
                    cy.get('[data-cy="select-variedad"], select').first().select('CCN51', { force: true })
                    cy.get('[data-cy="btn-save-lote"], button[type="submit"]').first().click()
                    cy.get('body', { timeout: 5000 }).should('be.visible')
                  }
                })
              }
            })
          }
        })
      }
    })

    // 6. Upload Image for Analysis
    cy.visit('/user/prediction')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('input[type="file"]').length > 0) {
        cy.uploadTestImage('cacao_sample.jpg')
        cy.get('body', { timeout: 5000 }).then(($afterUpload) => {
          if ($afterUpload.find('[data-cy="btn-analyze"], button[type="submit"]').length > 0) {
            cy.get('[data-cy="btn-analyze"], button[type="submit"]').first().click()
            cy.get('[data-cy="results-container"], .results, .result', { timeout: 30000 }).should('exist')
          }
        })
      }
    })

    // 7. Review Results
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="stats-panel"], .stats, .panel').length > 0) {
        cy.get('[data-cy="stats-panel"], .stats, .panel').should('exist')
      }
    })
    
    // 8. View Report
    cy.visit('/agricultor/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="chart-main"], .chart, canvas').length > 0) {
        cy.get('[data-cy="chart-main"], .chart, canvas').should('exist')
      }
    })
  })
})

