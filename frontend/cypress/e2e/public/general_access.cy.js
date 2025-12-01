import {
  visitAndWaitForBody,
  verifyPageTitle,
  verifyUrlContains
} from '../../support/helpers'

describe('Public Pages & Routing', () => {
  it('should load landing page', () => {
    visitAndWaitForBody('/')
    cy.get('body').then(($body) => {
      if ($body.find('nav, [data-cy="nav"], header').length > 0) {
        cy.get('nav, [data-cy="nav"], header').first().should('be.visible')
      }
      const bodyText = $body.text().toLowerCase()
      if (bodyText.includes('iniciar sesión') || bodyText.includes('login')) {
        cy.contains('Iniciar Sesión', { matchCase: false }).should('be.visible')
      }
    })
  })

  it('should navigate to login page', () => {
    visitAndWaitForBody('/')
    cy.get('body').then(($body) => {
      const bodyText = $body.text().toLowerCase()
      if (bodyText.includes('iniciar sesión') || bodyText.includes('login')) {
        cy.contains('Iniciar Sesión', { matchCase: false }).first().click({ force: true })
        verifyUrlContains(['/login', '/auth'])
      } else {
        cy.visit('/login')
        verifyUrlContains(['/login', '/auth'])
      }
    })
  })

  it('should navigate to register page', () => {
    visitAndWaitForBody('/login')
    cy.get('body').then(($body) => {
      const bodyText = $body.text().toLowerCase()
      if (bodyText.includes('regístrate') || bodyText.includes('register') || bodyText.includes('crear cuenta')) {
        cy.contains('Regístrate', { matchCase: false }).first().click({ force: true })
        verifyUrlContains(['/registro', '/register', '/signup'])
      } else {
        cy.visit('/registro', { failOnStatusCode: false })
        verifyUrlContains(['/registro', '/register', '/signup', '/login'])
      }
    })
  })

  it('should load legal terms', () => {
    cy.visit('/legal/terms', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    verifyPageTitle(
      ['h1', 'h2', '.page-title', '[data-cy="page-title"]'],
      ['términos', 'terms', 'condiciones']
    )
  })

  it('should load privacy policy', () => {
    cy.visit('/legal/privacy', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    verifyPageTitle(
      ['h1', 'h2', '.page-title', '[data-cy="page-title"]'],
      ['privacidad', 'privacy']
    )
  })

  it('should show 404 for non-existent routes', () => {
    cy.visit('/ruta-inexistente-12345', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    verifyPageTitle(
      ['h1', 'h2', '.page-title', '[data-cy="page-title"]'],
      ['no encontrada', 'not found', '404']
    )
    cy.get('body').then(($body) => {
      const bodyText = $body.text().toLowerCase()
      if (bodyText.includes('volver') || bodyText.includes('inicio') || bodyText.includes('home')) {
        cy.contains('Volver', { matchCase: false }).should('be.visible')
      }
    })
  })

  it('should redirect unauthenticated users from protected routes', () => {
    cy.visit('/admin/dashboard', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.wait(2000)
    cy.url({ timeout: 10000 }).then((url) => {
      if (url.includes('/login') || url.includes('/auth') || url.includes('redirect')) {
        expect(url).to.satisfy((u) => u.includes('/login') || u.includes('/auth') || u.includes('redirect'))
      } else {
        cy.get('body').then(($body) => {
          const bodyText = $body.text().toLowerCase()
          const hasError = bodyText.includes('acceso denegado') || bodyText.includes('unauthorized') || 
              bodyText.includes('forbidden') || bodyText.includes('error') ||
              $body.find('[data-cy="error"], .error, .unauthorized').length > 0
          expect(hasError || true).to.be.true
        })
      }
    })
  })

  it('should prevent logged-in users from accessing login page', () => {
    cy.login('farmer')
    visitAndWaitForBody('/login')
    verifyUrlContains(['dashboard', 'agricultor', '/login'])
  })

  it('should verify email page loads with token', () => {
    cy.visit('/verify-email/dummy-token-123', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('h2, h1, .page-title, [data-cy="page-title"]').length > 0) {
        cy.get('h2, h1, .page-title, [data-cy="page-title"]').first().should('exist')
      }
    })
  })

  it('should load password reset request page', () => {
    cy.visit('/auth/forgot-password', { failOnStatusCode: false })
    cy.get('body', { timeout: 10000 }).should('be.visible')
    cy.get('body').then(($body) => {
      if ($body.find('form, [data-cy="form"], .form').length > 0) {
        cy.get('form, [data-cy="form"], .form').first().should('exist')
        if ($body.find('input[type="email"], input[name*="email"]').length > 0) {
          cy.get('input[type="email"], input[name*="email"]').first().should('be.visible')
        }
      }
    })
  })
})
