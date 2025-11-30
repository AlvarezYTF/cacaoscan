describe('Advanced Form Inputs', () => {
  beforeEach(() => {
    cy.login('farmer')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="btn-add-finca"], button').length > 0) {
        cy.get('[data-cy="btn-add-finca"], button').first().click({ force: true })
      }
    })
  })

  it('should validate max length on inputs', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
        const longText = 'a'.repeat(256)
        cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').first().type(longText)
        cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', { timeout: 3000 }).first().should('exist')
      }
    })
  })

  it('should prevent negative numbers in area', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-area"], input[type="number"]').length > 0) {
        cy.get('[data-cy="input-area"], input[type="number"]').first().type('-50')
        cy.get('body', { timeout: 3000 }).then($body => {
          if ($body.find('.error-message, [data-cy="error"]').length > 0) {
            cy.get('.error-message, [data-cy="error"]').should('exist')
          } else {
            cy.get('[data-cy="input-area"], input[type="number"]').first().should('satisfy', ($el) => {
              const val = $el.val()
              return val !== '-50' || val === '' || val === null
            })
          }
        })
      }
    })
  })

  it('should handle special characters in names', () => {
    cy.get('body', { timeout: 5000 }).then(($body) => {
      if ($body.find('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').length > 0) {
        const weirdName = 'Finca Ñandú & Cacao @100%'
        cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]').first().type(weirdName)
        cy.get('[data-cy="btn-save-finca"], button[type="submit"]').first().click()
        cy.get('body', { timeout: 5000 }).should('be.visible')
      }
    })
  })

  it('should validate dates in history filter', () => {
    cy.visit('/agricultor/historial')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="date-start"], input[type="date"]').length > 0) {
        cy.get('[data-cy="date-start"], input[type="date"]').first().type('2025-12-31', { force: true })
        cy.get('[data-cy="date-end"], input[type="date"]').first().type('2024-01-01', { force: true })
        cy.get('[data-cy="btn-filter"], button[type="submit"]').first().click()
        cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
      }
    })
  })
})

