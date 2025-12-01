/**
 * Shared mocks for composables
 * Centralizes composable mocks to reduce duplication across test files
 */

import { vi } from 'vitest'

/**
 * Creates a mock useCatalogos composable
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock useCatalogos composable
 */
export function createMockUseCatalogos(overrides = {}) {
  return {
    tiposDocumento: { value: [{ codigo: 'CC', nombre: 'Cédula' }] },
    generos: { value: [{ codigo: 'M', nombre: 'Masculino' }] },
    departamentos: { value: [{ codigo: 'ANT', nombre: 'Antioquia', id: 1 }] },
    municipios: { value: [{ id: 1, nombre: 'Medellín' }] },
    isLoadingCatalogos: { value: false },
    cargarCatalogos: vi.fn(),
    cargarMunicipios: vi.fn(),
    limpiarMunicipios: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock useFormValidation composable
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock useFormValidation composable
 */
export function createMockUseFormValidation(overrides = {}) {
  return {
    errors: {},
    isValidEmail: (email) => {
      if (typeof email !== 'string') return false
      const trimmed = email.trim()
      return (
        trimmed.length >= 5 &&
        trimmed.includes('@') &&
        trimmed.includes('.') &&
        trimmed.indexOf('@') > 0 &&
        trimmed.lastIndexOf('.') > trimmed.indexOf('@') + 1
      )
    },
    isValidPhone: (phone) => {
      // eslint-disable-next-line prefer-regex-literals
      const digits = String(phone).replaceAll(/\D/g, '')
      return digits.length >= 7 && digits.length <= 15
    },
    isValidDocument: (doc) => {
      // eslint-disable-next-line prefer-regex-literals
      const digits = String(doc).replaceAll(/\D/g, '')
      return digits.length >= 6 && digits.length <= 11
    },
    isValidBirthdate: () => true,
    validatePassword: (pwd) => {
      if (typeof pwd !== 'string') {
        return {
          isValid: false,
          length: false,
          uppercase: false,
          lowercase: false,
          number: false
        }
      }
      const length = pwd.length >= 8
      const uppercase = /[A-Z]/.test(pwd)
      const lowercase = /[a-z]/.test(pwd)
      const number = /\d/.test(pwd)
      return {
        isValid: length && uppercase && lowercase && number,
        length,
        uppercase,
        lowercase,
        number
      }
    },
    clearErrors: vi.fn(),
    ...overrides
  }
}

/**
 * Creates a mock useBirthdateRange composable
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock useBirthdateRange composable
 */
export function createMockUseBirthdateRange(overrides = {}) {
  return {
    maxBirthdate: '2010-01-01',
    minBirthdate: '1950-01-01',
    ...overrides
  }
}

/**
 * Creates a mock useModal composable
 * @param {Object} overrides - Properties to override
 * @returns {Object} Mock useModal composable
 */
export function createMockUseModal(overrides = {}) {
  return {
    modalContainer: { value: null },
    openModal: vi.fn(),
    closeModal: vi.fn(),
    ...overrides
  }
}

