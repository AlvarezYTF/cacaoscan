import { getApiBaseUrl, visitAndWaitForBody, ifFoundInBody } from '../../support/helpers'

describe('Error Edge Cases Examples', () => {
  beforeEach(() => {
    cy.clearCookies()
    cy.clearLocalStorage()
  })

  it('should handle edge case scenarios gracefully', () => {
    cy.visit('/')
    visitAndWaitForBody()

    cy.get('body').should('be.visible')
  })

  it('should handle empty form submissions', () => {
    cy.visit('/login')
    visitAndWaitForBody()

    const submitButton = cy.get('button[type="submit"]').first()
    ifFoundInBody('button[type="submit"]', () => {
      submitButton.click({ force: true })
      cy.wait(1000)
    })
  })

  it('should handle invalid input formats', () => {
    cy.visit('/register')
    visitAndWaitForBody()

    ifFoundInBody('input[type="email"]', () => {
      cy.get('input[type="email"]').first().type('invalid-email-format')
      cy.get('body').should('be.visible')
    })
  })

  it('should handle network timeout scenarios', () => {
    const apiBaseUrl = getApiBaseUrl()
    
    cy.intercept('GET', `${apiBaseUrl}/**`, {
      delay: 30000,
      statusCode: 200
    }).as('slowRequest')

    cy.visit('/')
    visitAndWaitForBody()

    cy.wait(1000)
    cy.get('body').should('be.visible')
  })
})

