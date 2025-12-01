/**
 * Shared mocks for services
 * Centralizes service mocks to reduce duplication across test files
 */

import { vi } from 'vitest'

/**
 * Creates a mock authApi service
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock authApi service
 */
export function createMockAuthApi(overrides = {}) {
  return {
    register: vi.fn(),
    updateUser: vi.fn(),
    sendOtp: vi.fn(),
    confirmPasswordReset: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock personasApi service
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock personasApi service
 */
export function createMockPersonasApi(overrides = {}) {
  return {
    getPersonaByUserId: vi.fn().mockResolvedValue({
      primer_nombre: '',
      primer_apellido: '',
      tipo_documento_info: { codigo: 'CC' },
      numero_documento: ''
    }),
    updatePersonaByUserId: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock fincasApi service
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock fincasApi service
 */
export function createMockFincasApi(overrides = {}) {
  return {
    getFincas: vi.fn().mockResolvedValue({ results: [] }),
    createFinca: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock api service
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock api service
 */
export function createMockApi(overrides = {}) {
  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    ...overrides
  }
}

