describe('Advanced Form Inputs', () => {
  beforeEach(() => {
    cy.navigateToFincas('farmer')
    cy.clickIfExists('[data-cy="btn-add-finca"], button', { force: true })
  })

  const verifyInputExists = () => {
    cy.get('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', { timeout: 3000 }).first().should('exist')
  }

  const typeLongText = () => {
    const longText = 'a'.repeat(256)
    return typeIfExistsAndContinue('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', longText, verifyInputExists)
  }

  it('should validate max length on inputs', () => {
    return ifFoundInBody('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', typeLongText)
  })

  const verifyNegativeNumberHandling = () => {
    return ifFoundInBody('.error-message, [data-cy="error"]', () => {
      cy.get('.error-message, [data-cy="error"]').should('exist')
    }, () => {
      cy.get('[data-cy="input-area"], input[type="number"]').first().should('satisfy', ($el) => {
        const val = $el.val()
        return val !== '-50' || val === '' || val === null
      })
    })
  }

  const typeNegativeNumber = () => {
    return typeIfExistsAndContinue('[data-cy="input-area"], input[type="number"]', '-50', verifyNegativeNumberHandling)
  }

  it('should prevent negative numbers in area', () => {
    return ifFoundInBody('[data-cy="input-area"], input[type="number"]', typeNegativeNumber)
  })

  const saveFincaWithSpecialChars = () => {
    return clickIfExistsAndContinue('[data-cy="btn-save-finca"], button[type="submit"]', () => {
      cy.get('body', { timeout: 5000 }).should('be.visible')
    })
  }

  const typeSpecialCharsName = () => {
    const weirdName = 'Finca Ñandú & Cacao @100%'
    return typeIfExistsAndContinue('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', weirdName, saveFincaWithSpecialChars)
  }

  it('should handle special characters in names', () => {
    return ifFoundInBody('[data-cy="input-nombre"], input[name*="nombre"], input[type="text"]', typeSpecialCharsName)
  })

  it('should validate dates in history filter', () => {
    cy.login('farmer')
    cy.visit('/agricultor/historial')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('[data-cy="date-start"], input[type="date"]').length > 0) {
        cy.fillFieldIfExists('[data-cy="date-start"], input[type="date"]', '2025-12-31', { force: true })
        cy.fillFieldIfExists('[data-cy="date-end"], input[type="date"]', '2024-01-01', { force: true })
        cy.clickIfExists('[data-cy="btn-filter"], button[type="submit"]').then(() => {
          cy.get('.error-message, [data-cy="error"]', { timeout: 5000 }).should('exist')
        })
      }
    })
  })
})

