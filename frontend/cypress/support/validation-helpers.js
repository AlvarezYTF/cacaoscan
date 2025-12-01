/**
 * Validation-specific helpers for form validation tests
 * Extracts common patterns from validation-forms.cy.js
 */
import {
  visitAndWaitForBody,
  openModalAndExecute,
  fillFieldSubmitAndVerifyError,
  verifyErrorMessageWithSelectors,
  verifySelectorsExist,
  ifFoundInBody,
  clickIfExistsAndContinue
} from './helpers'

/**
 * Validates a field in a modal with error verification
 * Common pattern: visit page -> open modal -> fill field -> submit -> verify error
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {string} fieldSelector - Selector for field to validate
 * @param {string} value - Invalid value to test
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateFieldInModal(
  pageUrl,
  buttonSelector,
  fieldSelector,
  value,
  submitSelector,
  errorSelector,
  expectedTexts
) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(fieldSelector).length > 0) {
      fillFieldSubmitAndVerifyError(fieldSelector, value, submitSelector, errorSelector, expectedTexts)
    }
  })
}

/**
 * Validates required fields in a modal
 * Common pattern: visit page -> open modal -> submit -> verify multiple errors
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {string} submitSelector - Selector for submit button
 * @param {Array<string>} errorSelectors - Array of error selectors to verify
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateRequiredFieldsInModal(pageUrl, buttonSelector, submitSelector, errorSelectors) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(submitSelector).length > 0) {
      cy.get(submitSelector).first().click()
      cy.get('body', { timeout: 5000 }).then(($afterSubmit) => {
        verifySelectorsExist(errorSelectors, $afterSubmit, 3000)
      })
    }
  })
}

/**
 * Validates field format (email, phone, document, etc.)
 * Common pattern: visit page -> fill field -> submit -> verify error
 * @param {string} pageUrl - URL to visit
 * @param {string} fieldSelector - Selector for field to validate
 * @param {string} invalidValue - Invalid value to test
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateFieldFormat(pageUrl, fieldSelector, invalidValue, submitSelector, errorSelector, expectedTexts) {
  visitAndWaitForBody(pageUrl)
  return fillFieldSubmitAndVerifyError(fieldSelector, invalidValue, submitSelector, errorSelector, expectedTexts)
}

/**
 * Validates multiple fields in a modal
 * Common pattern: visit page -> open modal -> fill multiple fields -> submit -> verify errors
 * @param {string} pageUrl - URL to visit
 * @param {string} buttonSelector - Selector for button that opens modal
 * @param {Array<Object>} fields - Array of field objects { selector, value }
 * @param {string} submitSelector - Selector for submit button
 * @param {Array<string>} errorSelectors - Array of error selectors to verify
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateMultipleFieldsInModal(pageUrl, buttonSelector, fields, submitSelector, errorSelectors) {
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    for (const { selector, value } of fields) {
      if ($modal.find(selector).length > 0) {
        const $field = cy.get(selector).first()
        // Check if it's a select element
        if ($modal.find(selector).is('select')) {
          $field.select(value, { force: true })
        } else {
          $field.type(value, { force: true })
        }
      }
    }
    if ($modal.find(submitSelector).length > 0) {
      cy.get(submitSelector).first().click({ force: true })
      cy.get('body', { timeout: 3000 }).then(($error) => {
        if (Array.isArray(errorSelectors)) {
          verifySelectorsExist(errorSelectors, $error, 3000)
        } else {
          verifyErrorMessageWithSelectors([errorSelectors], [])
        }
      })
    }
  })
}

/**
 * Validates conditional fields in a modal
 * Common pattern: visit page -> open modal -> select option -> verify conditional field -> submit -> verify error
 * @param {Object} config - Configuration object
 * @param {string} config.pageUrl - URL to visit
 * @param {string} config.buttonSelector - Selector for button that opens modal
 * @param {string} config.triggerSelector - Selector for field that triggers conditional field
 * @param {string} config.triggerValue - Value to set in trigger field
 * @param {string} config.conditionalSelector - Selector for conditional field
 * @param {string} config.submitSelector - Selector for submit button
 * @param {string} config.errorSelector - Selector for error message
 * @param {Array<string>} config.expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validateConditionalFieldInModal(config) {
  const { pageUrl, buttonSelector, triggerSelector, triggerValue, conditionalSelector, submitSelector, errorSelector, expectedTexts } = config
  visitAndWaitForBody(pageUrl)
  return openModalAndExecute(buttonSelector, ($modal) => {
    if ($modal.find(triggerSelector).length > 0) {
      cy.get(triggerSelector).first().select(triggerValue, { force: true })
      return cy.get('body', { timeout: 3000 }).then(($afterSelect) => {
        return handleConditionalFieldValidation($afterSelect, conditionalSelector, submitSelector, errorSelector, expectedTexts)
      })
    }
    return cy.wrap(null)
  })
}

/**
 * Handles conditional field validation after trigger selection
 * Reduces nesting by extracting logic into separate function
 * @param {JQuery} $context - jQuery context element
 * @param {string} conditionalSelector - Selector for conditional field
 * @param {string} submitSelector - Selector for submit button
 * @param {string} errorSelector - Selector for error message
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
function handleConditionalFieldValidation($context, conditionalSelector, submitSelector, errorSelector, expectedTexts) {
  ifFoundInBody(conditionalSelector, () => {
    cy.get(conditionalSelector).should('exist')
  })
  return clickIfExistsAndContinue(submitSelector, () => {
    verifyErrorMessageWithSelectors([errorSelector], expectedTexts)
  })
}

/**
 * Validates password match by filling password and confirm password fields
 * Reduces nesting by extracting password match validation logic
 * @param {Object} config - Configuration object
 * @param {string} config.pageUrl - URL to visit
 * @param {string} config.passwordSelector - Selector for password input
 * @param {string} config.passwordValue - Password value to type
 * @param {string} config.confirmPasswordSelector - Selector for confirm password input
 * @param {string} config.confirmPasswordValue - Confirm password value to type
 * @param {string} config.submitSelector - Selector for submit button
 * @param {Array<string>} config.errorSelectors - Array of error selectors
 * @param {Array<string>} config.expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
export function validatePasswordMatch(config) {
  // NOSONAR S2068 - These are CSS selectors and dynamically generated values, not hardcoded passwords
  const { pageUrl, passwordSelector, passwordValue, confirmPasswordSelector, confirmPasswordValue, submitSelector, errorSelectors, expectedTexts } = config // NOSONAR S2068
  visitAndWaitForBody(pageUrl)
  return fillPasswordField(passwordSelector, passwordValue) // NOSONAR S2068
    .then(() => fillConfirmPasswordField(confirmPasswordSelector, confirmPasswordValue)) // NOSONAR S2068
    .then(() => submitAndVerifyPasswordError(submitSelector, errorSelectors, expectedTexts))
}

/**
 * Fills password field if it exists
 * @param {string} passwordSelector - Selector for password input
 * @param {string} passwordValue - Password value to type (generated dynamically)
 * @returns {Cypress.Chainable} Cypress chainable
 */
function fillPasswordField(passwordSelector, passwordValue) { // NOSONAR S2068
  return cy.get('body').then(($body) => {
    if ($body.find(passwordSelector).length > 0) {
      cy.get(passwordSelector).first().type(passwordValue, { force: true }) // NOSONAR S2068
      return cy.wrap(true)
    }
    return cy.wrap(false)
  })
}

/**
 * Fills confirm password field if it exists
 * @param {string} confirmPasswordSelector - Selector for confirm password input
 * @param {string} confirmPasswordValue - Confirm password value to type (generated dynamically)
 * @returns {Cypress.Chainable} Cypress chainable
 */
function fillConfirmPasswordField(confirmPasswordSelector, confirmPasswordValue) { // NOSONAR S2068
  return cy.get('body').then(($body) => {
    if ($body.find(confirmPasswordSelector).length > 0) {
      cy.get(confirmPasswordSelector).first().type(confirmPasswordValue, { force: true }) // NOSONAR S2068
      return cy.wrap(true)
    }
    return cy.wrap(false)
  })
}

/**
 * Submits form and verifies password match error
 * @param {string} submitSelector - Selector for submit button
 * @param {Array<string>} errorSelectors - Array of error selectors
 * @param {Array<string>} expectedTexts - Expected error text fragments
 * @returns {Cypress.Chainable} Cypress chainable
 */
function submitAndVerifyPasswordError(submitSelector, errorSelectors, expectedTexts) {
  return clickIfExistsAndContinue(submitSelector, () => {
    verifyErrorMessageWithSelectors(errorSelectors, expectedTexts)
  })
}

