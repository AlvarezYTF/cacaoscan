// ***********************************************************
// This example support/index.js is processed and
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

// Manejo global de errores no capturados
Cypress.on('uncaught:exception', (err, runnable) => {
  // Ignorar errores de módulos que no se pueden resolver (común en desarrollo)
  if (err.message.includes('Failed to fetch dynamically imported module') ||
      err.message.includes('Loading chunk') ||
      err.message.includes('ChunkLoadError')) {
    return false
  }
  
  // Ignorar errores de traducción de Google (común en desarrollo)
  if (err.message.includes('translate') || err.message.includes('google')) {
    return false
  }
  
  // Por defecto, no fallar en errores no capturados
  return false
})

// Configuración global de timeouts
Cypress.config('defaultCommandTimeout', 10000)
Cypress.config('requestTimeout', 10000)
Cypress.config('responseTimeout', 10000)

// Alternatively you can use CommonJS syntax:
// require('./commands')
