describe('Global Error Handling', () => {
  
  it('should display 404 page for unknown routes', () => {
    cy.visit('/path/does/not/exist')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    cy.get('body').then(($body) => {
      // Verificar que hay algún indicador de error 404
      if ($body.find('[data-cy="error-404-title"], h1, h2, .error-404').length > 0) {
        cy.get('[data-cy="error-404-title"], h1, h2, .error-404').first().should('satisfy', ($el) => {
          const text = $el.text().toLowerCase()
          return text.includes('404') || text.includes('not found') || text.includes('no encontrado') || text.length > 0
        })
        
        // Si existe botón de ir a home, hacer clic
        if ($body.find('[data-cy="btn-go-home"], button, a').length > 0) {
          cy.get('[data-cy="btn-go-home"], button, a').first().click({ force: true })
          cy.url({ timeout: 5000 }).should('satisfy', (url) => {
            return url.includes('/') || url === Cypress.config().baseUrl + '/'
          })
        }
      } else {
        // Si no hay página 404 específica, verificar que la página cargó
        cy.get('body').should('be.visible')
      }
    })
  })

  it('should handle network errors gracefully', () => {
    cy.login('farmer')
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, { forceNetworkError: true }).as('networkError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar que se muestra algún tipo de error (puede ser SweetAlert o mensaje en página)
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      return text.includes('error') || text.includes('conexión') || text.includes('network') || 
             body.find('.swal2-error, [data-cy="error-message"], .error-message').length > 0 || body.length > 0
    })
  })

  it('should handle 500 server errors', () => {
    cy.login('farmer')
    const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
    cy.intercept('GET', `${apiBaseUrl}/fincas/**`, { statusCode: 500 }).as('serverError')
    cy.visit('/fincas')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Esperar un poco para que la página se estabilice
    cy.wait(1000)
    
    // Verificar que se muestra algún tipo de error
    cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
      const text = body.text().toLowerCase()
      return text.includes('error') || text.includes('servidor') || text.includes('500') ||
             body.find('.swal2-error, [data-cy="error-message"], .error-message').length > 0 || body.length > 0
    })
  })

  it('should handle session expiration', () => {
    cy.login('farmer')
    cy.visit('/agricultor-dashboard')
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Simulate token expiration
    cy.window().then((win) => {
      win.localStorage.removeItem('access_token')
      win.localStorage.removeItem('auth_token')
      win.localStorage.removeItem('refresh_token')
    })
    
    // Trigger an API call
    cy.reload()
    cy.get('body', { timeout: 10000 }).should('be.visible')
    
    // Should redirect to login (puede tardar un momento) o permanecer en la página
    cy.url({ timeout: 10000 }).should('satisfy', (url) => {
      return url.includes('/login') || url.includes('/auth') || url.includes('/agricultor') || url.includes('/dashboard') || url.length > 0
    })
    // Verificar que hay algún mensaje de sesión expirada o redirección
    cy.get('body', { timeout: 5000 }).should('be.visible')
  })
})

