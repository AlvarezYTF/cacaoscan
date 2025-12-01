/**
 * Centralized mocks for tests
 * Exports all mock factories for easy import
 */

import {
  createMockAuthStore,
  createMockAdminStore,
  createMockConfigStore
} from './stores'

import {
  createMockUseCatalogos,
  createMockUseFormValidation,
  createMockUseBirthdateRange,
  createMockUseModal
} from './composables'

import {
  createMockAuthApi,
  createMockPersonasApi,
  createMockFincasApi,
  createMockApi
} from './services'

// Re-export all factories
export * from './stores'
export * from './composables'
export * from './services'
export * from './components'

/**
 * Creates all common mocks for component tests
 * @param {Object} overrides - Properties to override specific mocks
 * @returns {Object} Object with all common mocks
 */
export function createCommonMocks(overrides = {}) {
  return {
    authStore: createMockAuthStore(overrides.authStore),
    adminStore: createMockAdminStore(overrides.adminStore),
    configStore: createMockConfigStore(overrides.configStore),
    useCatalogos: createMockUseCatalogos(overrides.useCatalogos),
    useFormValidation: createMockUseFormValidation(overrides.useFormValidation),
    useBirthdateRange: createMockUseBirthdateRange(overrides.useBirthdateRange),
    useModal: createMockUseModal(overrides.useModal),
    authApi: createMockAuthApi(overrides.authApi),
    personasApi: createMockPersonasApi(overrides.personasApi),
    fincasApi: createMockFincasApi(overrides.fincasApi),
    api: createMockApi(overrides.api)
  }
}

