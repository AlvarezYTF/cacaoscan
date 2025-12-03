import { defineConfig } from 'cypress'

const isCI = process.env.CI === 'true' || process.env.CYPRESS_CI === 'true'

export default defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.{cy,spec}.{js,jsx,ts,tsx}',
    baseUrl: process.env.CYPRESS_BASE_URL || 'http://localhost:5173',
    trashAssetsBeforeRuns: false,
    video: !isCI,
    screenshotOnRunFailure: !isCI,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
  },
  component: {
    specPattern: 'src/**/__tests__/*.{cy,spec}.{js,ts,jsx,tsx}',
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
  },
})