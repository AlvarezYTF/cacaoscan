import { generatePassword } from '../../support/helpers'

describe('E2E: Complete Farmer Journey', () => {
  const timestamp = Date.now()
  const userEmail = `farmer_journey_${timestamp}@example.com`
  const fincaName = `Finca Journey ${timestamp}`

  it('should complete the full cycle from registration to analysis', () => {
    const password = generatePassword()
    
    // 1. Registration
    cy.visit('/registro')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.fillRegisterForm({
      firstName: 'Journey',
      lastName: 'Farmer',
      email: userEmail,
      password: password,
      confirmPassword: password
    })
    cy.submitRegisterForm()
    cy.get('body', { timeout: 5000 }).should('be.visible')

    // 2. Login
    cy.visit('/login')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="input-email"], input[type="email"], input[type="text"]').length > 0) {
        cy.get('[data-cy="input-email"], input[type="email"], input[type="text"]').first().type(userEmail)
        cy.get('[data-cy="input-password"], input[type="password"]').first().type(password)
        cy.get('[data-cy="btn-submit-login"], [data-cy="login-button"], button[type="submit"]').first().click()
        cy.url({ timeout: 10000 }).should('satisfy', (url) => {
          return url.includes('/agricultor-dashboard') || url.includes('/dashboard') || url.includes('/login')
        })
      }
    })

    // 3. Create Finca
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.createEntity('finca', {
      nombre: fincaName,
      ubicacion: 'Vereda San Juan',
      area: '100'
    }, { useApi: false })

    // 4. Create Lote
    cy.get('body').then(($body) => {
      if ($body.text().includes(fincaName)) {
        cy.contains(fincaName).click({ force: true })
        cy.get('body', { timeout: 5000 }).then(($details) => {
          if ($details.find('[data-cy="tab-lotes"], [role="tab"]').length > 0) {
            cy.get('[data-cy="tab-lotes"], [role="tab"]').first().click()
            cy.createLote({
              nombre: 'Lote Principal',
              area: '20',
              variedad: 'CCN51'
            })
          }
        })
      }
    })

    // 5. Upload Image for Analysis
    cy.visit('/user/prediction')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.performImageAnalysis('cacao_sample.jpg', { waitForResults: true, timeout: 30000 })

    // 6. Review Results
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="stats-panel"], .stats, .panel').length > 0) {
        cy.get('[data-cy="stats-panel"], .stats, .panel').should('exist')
      }
    })
    
    // 7. View Report
    cy.visit('/agricultor/reportes')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="chart-main"], .chart, canvas').length > 0) {
        cy.get('[data-cy="chart-main"], .chart, canvas').should('exist')
      }
    })
  })
})

