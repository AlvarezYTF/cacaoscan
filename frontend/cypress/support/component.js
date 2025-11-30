// ***********************************************************
// This example support/component.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Import selectors and helpers for use in component tests
import { SELECTORS } from './selectors'
import * as helpers from './helpers'

// Make SELECTORS and helpers available globally for component tests
globalThis.SELECTORS = SELECTORS
globalThis.helpers = helpers

// Import global styles
import '@/assets/main.css'

import { mount } from 'cypress/vue'

Cypress.Commands.add('mount', mount)

// Example use:
// cy.mount(MyComponent)
