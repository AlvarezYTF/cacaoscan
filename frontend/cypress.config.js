import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}',
    baseUrl: 'http://localhost:4173',
    // Environment variables for test credentials can be set here or via process.env
    // Available variables: CYPRESS_TEST_PASSWORD, CYPRESS_DIFFERENT_PASSWORD,
    // CYPRESS_STRONG_PASSWORD, CYPRESS_NEW_PASSWORD, CYPRESS_TEST_EMAIL, CYPRESS_LOGIN_PASSWORD
    env: {
      // These can be overridden via environment variables or Cypress.env()
      // Defaults are defined in cypress/support/test-data.js
    },
  },
  component: {
    specPattern: 'src/**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}',
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
  },
})