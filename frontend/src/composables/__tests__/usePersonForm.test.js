/**
 * Unit tests for usePersonForm composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePersonForm } from '../usePersonForm.js'
import { useCatalogos } from '../useCatalogos'

// Mock dependencies
vi.mock('../useCatalogos', () => ({
  useCatalogos: vi.fn(() => ({
    tiposDocumento: { value: [] },
    generos: { value: [] },
    departamentos: { value: [] },
    municipios: { value: [] },
    isLoadingCatalogos: { value: false },
    cargarCatalogos: vi.fn(),
    cargarMunicipios: vi.fn(),
    limpiarMunicipios: vi.fn()
  }))
}))

vi.mock('../useFormValidation', () => {
  const createMockValidation = () => {
    const errors = {}
    return {
      errors,
      isValidEmail: vi.fn(),
      isValidPhone: vi.fn(),
      isValidDocument: vi.fn(),
      isValidBirthdate: vi.fn(),
      clearErrors: vi.fn()
    }
  }
  return {
    useFormValidation: vi.fn(createMockValidation)
  }
})

vi.mock('../useBirthdateRange', () => ({
  useBirthdateRange: () => ({
    maxBirthdate: { value: '2010-01-01' },
    minBirthdate: { value: '1900-01-01' }
  })
}))

describe('usePersonForm', () => {
  let personForm

  beforeEach(() => {
    vi.clearAllMocks()
    personForm = usePersonForm()
  })

  describe('initial state', () => {
    it('should have catalogos from useCatalogos', () => {
      expect(personForm.tiposDocumento).toBeDefined()
      expect(personForm.departamentos).toBeDefined()
      expect(personForm.generos).toBeDefined()
    })

    it('should have validation functions', () => {
      expect(typeof personForm.isValidEmail).toBe('function')
      expect(typeof personForm.isValidDocument).toBe('function')
    })

    it('should have birthdate range', () => {
      expect(personForm.maxBirthdate.value).toBeDefined()
      expect(personForm.minBirthdate.value).toBeDefined()
    })
  })

  describe('getInputClasses', () => {
    it('should return base classes when no error', () => {
      delete personForm.errors.testField
      const classes = personForm.getInputClasses('testField')
      
      expect(classes).toContain('border-gray-200')
      expect(classes).not.toContain('border-red-500')
    })

    it('should include error class when field has error', () => {
      personForm.errors.testField = 'Error message'
      const classes = personForm.getInputClasses('testField')
      
      expect(classes).toContain('border-red-500')
    })
  })

  describe('onDepartamentoChange', () => {
    it('should clear municipios', async () => {
      const limpiarMunicipios = vi.fn()
      useCatalogos.mockReturnValueOnce({
        limpiarMunicipios,
        tiposDocumento: { value: [] },
        generos: { value: [] },
        departamentos: { value: [] },
        municipios: { value: [] },
        isLoadingCatalogos: { value: false },
        cargarCatalogos: vi.fn(),
        cargarMunicipios: vi.fn()
      })

      const form = usePersonForm()
      await form.onDepartamentoChange()

      expect(limpiarMunicipios).toHaveBeenCalled()
    })

    it('should call custom callback if provided', async () => {
      const customCallback = vi.fn()
      const form = usePersonForm({ onDepartamentoChange: customCallback })
      
      await form.onDepartamentoChange()
      
      expect(customCallback).toHaveBeenCalled()
    })
  })
})

