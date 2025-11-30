/**
 * Test helpers for Cypress
 * Provides reusable helper functions for common test operations
 */
import { SELECTORS } from './selectors'
import { TEST_CREDENTIALS } from './test-data'

/**
 * Creates a test user object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test user object
 */
export function createTestUser(overrides = {}) {
  return {
    email: 'test@example.com',
    password: TEST_CREDENTIALS.testPassword,
    firstName: 'Test',
    lastName: 'User',
    document: '1234567890',
    phone: '+573001234567',
    role: 'agricultor',
    ...overrides
  }
}

/**
 * Creates a test finca object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test finca object
 */
export function createTestFinca(overrides = {}) {
  return {
    nombre: 'Test Finca',
    ubicacion: 'Test Location',
    area_total: 10.5,
    descripcion: 'Test description',
    ...overrides
  }
}

/**
 * Creates a test lote object
 * @param {Object} overrides - Properties to override
 * @returns {Object} Test lote object
 */
export function createTestLote(overrides = {}) {
  return {
    nombre: 'Test Lote',
    area: 5,
    variedad: 'Criollo',
    edad_plantas: 5,
    descripcion: 'Test lote description',
    ...overrides
  }
}

/**
 * Sets up authentication for tests
 * @param {string} userType - Type of user (admin, agricultor, analyst)
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function setupAuth(userType = 'admin') {
  return cy.login(userType)
}

/**
 * Tears down authentication after tests
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function teardownAuth() {
  return cy.logout()
}

/**
 * Mocks common API responses
 * @param {Object} responses - Object mapping endpoints to responses
 * @returns {void}
 */
export function mockApiResponses(responses) {
  const defaultResponses = {
    '/api/auth/login/': { access: 'mock-token', refresh: 'mock-refresh', user: {} },
    '/api/fincas/': { results: [], count: 0 },
    '/api/lotes/': { results: [], count: 0 },
    '/api/predictions/': { results: [], count: 0 },
    '/api/notifications/': { results: [], count: 0 },
    '/api/audit/': { results: [], count: 0 },
    ...responses
  }

  for (const [endpoint, response] of Object.entries(defaultResponses)) {
    cy.intercept('GET', endpoint, { statusCode: 200, body: response }).as(`api-${endpoint.replaceAll('/', '-')}`)
    cy.intercept('POST', endpoint, { statusCode: 201, body: response }).as(`api-post-${endpoint.replaceAll('/', '-')}`)
  }
}

/**
 * Fills a form with provided data
 * @param {Object} formData - Data to fill in the form
 * @param {string} formType - Type of form (finca, lote, login, etc.)
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function fillForm(formData, formType = 'generic') {
  const formSelectors = {
    finca: SELECTORS.finca,
    lote: SELECTORS.lote,
    login: {
      email: SELECTORS.inputs.email,
      password: SELECTORS.inputs.password
    }
  }

  const selectors = formSelectors[formType] || {}

  for (const [field, value] of Object.entries(formData)) {
    const selector = selectors[field] || `[data-cy="${field}"]`
    if (value !== undefined && value !== null) {
      cy.get(selector).clear().type(value.toString())
    }
  }

  return cy.wrap(null)
}

/**
 * Waits for API call to complete
 * @param {string} alias - API alias to wait for
 * @param {number} timeout - Timeout in milliseconds
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function waitForApi(alias, timeout = 10000) {
  return cy.wait(`@${alias}`, { timeout })
}

/**
 * Interacts with a table (sort, filter, paginate)
 * @param {string} action - Action to perform (sort, filter, paginate)
 * @param {Object} options - Options for the action
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function interactWithTable(action, options = {}) {
  const { column, direction, filterValue, page } = options

  switch (action) {
    case 'sort':
      if (column) {
        cy.get(`${SELECTORS.tables.dataTable} [data-cy="column-${column}"]`).click()
        if (direction === 'desc') {
          cy.get(`${SELECTORS.tables.dataTable} [data-cy="column-${column}"]`).click()
        }
      }
      break
    case 'filter':
      if (filterValue) {
        cy.get(SELECTORS.inputs.filter).clear().type(filterValue)
        cy.get(SELECTORS.buttons.filter).click()
      }
      break
    case 'paginate':
      if (page) {
        cy.get(`${SELECTORS.tables.pagination} [data-cy="page-${page}"]`).click()
      }
      break
  }

  return cy.wrap(null)
}

/**
 * Verifies table data
 * @param {Array} expectedData - Expected data in the table
 * @param {string} tableSelector - Selector for the table
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function verifyTableData(expectedData, tableSelector = SELECTORS.tables.dataTable) {
  cy.get(tableSelector).should('be.visible')
  
  if (expectedData.length === 0) {
    cy.get(`${tableSelector} ${SELECTORS.tables.tableRow}`).should('not.exist')
    return cy.wrap(null)
  }

  for (let index = 0; index < expectedData.length; index++) {
    const row = expectedData[index]
    cy.get(`${tableSelector} ${SELECTORS.tables.tableRow}`).eq(index).within(() => {
      for (const value of Object.values(row)) {
        cy.contains(value.toString()).should('be.visible')
      }
    })
  }

  return cy.wrap(null)
}

/**
 * Cleans up test data
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function cleanupTestData() {
  return cy.cleanupTestData()
}

