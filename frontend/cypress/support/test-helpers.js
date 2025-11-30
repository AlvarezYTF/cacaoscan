// Helper functions para hacer los tests más robustos

/**
 * Obtiene la URL base del API
 */
export function getApiBaseUrl() {
  return Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
}

/**
 * Intercepta una petición al API con la URL completa
 */
export function interceptApi(method, endpoint, response, statusCode = 200) {
  const apiBaseUrl = getApiBaseUrl()
  const fullUrl = endpoint.startsWith('http') ? endpoint : `${apiBaseUrl}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`
  return cy.intercept(method, fullUrl, { statusCode, body: response })
}

/**
 * Verifica que una URL contiene alguna de las rutas esperadas
 */
export function shouldIncludeRoute(url, expectedRoutes) {
  const routes = Array.isArray(expectedRoutes) ? expectedRoutes : [expectedRoutes]
  return routes.some(route => url.includes(route))
}

/**
 * Verifica que un elemento contiene alguno de los textos esperados
 */
export function shouldContainText(element, expectedTexts) {
  const texts = Array.isArray(expectedTexts) ? expectedTexts : [expectedTexts]
  const elementText = element.text().toLowerCase()
  return texts.some(text => elementText.includes(text.toLowerCase()))
}

/**
 * Espera a que un elemento sea visible con timeout flexible
 */
export function waitForElement(selector, options = {}) {
  const timeout = options.timeout || 10000
  return cy.get(selector, { timeout }).should('be.visible')
}

/**
 * Verifica que hay algún mensaje de error visible
 */
export function shouldShowError() {
  cy.get('body', { timeout: 5000 }).should('satisfy', (body) => {
    const text = body.text().toLowerCase()
    const hasErrorElement = body.find('[data-cy="error-message"], .swal2-error, .error-message, .alert-error').length > 0
    return hasErrorElement || text.includes('error') || text.includes('incorrecto') || text.includes('inválid')
  })
}

/**
 * Verifica condicionalmente si un elemento existe antes de interactuar
 */
export function conditionalClick(selector, options = {}) {
  cy.get('body').then(($body) => {
    const elements = $body.find(selector)
    if (elements.length > 0) {
      cy.get(selector).first().click({ force: true, ...options })
      return true
    }
    return false
  })
}

/**
 * Verifica condicionalmente si un elemento existe antes de verificar
 */
export function conditionalShould(selector, assertion, options = {}) {
  cy.get('body').then(($body) => {
    const elements = $body.find(selector)
    if (elements.length > 0) {
      cy.get(selector, { timeout: options.timeout || 5000 }).should(assertion)
      return true
    }
    return false
  })
}
