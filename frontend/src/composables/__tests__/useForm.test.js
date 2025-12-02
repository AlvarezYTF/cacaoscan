/**
 * Unit tests for useForm composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useForm } from '../useForm.js'
import { useFormValidation } from '../useFormValidation'
import { useCatalogos } from '../useCatalogos'

// Mock dependencies
vi.mock('../useFormValidation', () => ({
  useFormValidation: vi.fn(() => ({
    errors: {},
    isValidEmail: vi.fn(),
    isValidPhone: vi.fn(),
    isValidDocument: vi.fn(),
    isValidBirthdate: vi.fn(),
    validatePassword: vi.fn(),
    clearErrors: vi.fn(),
    setError: vi.fn(),
    removeError: vi.fn(),
    hasErrors: vi.fn(() => false),
    mapServerErrors: vi.fn(),
    handleFormSubmit: vi.fn(async (submitFn, validateFn, onSuccess, onError) => {
      try {
        const result = await submitFn()
        return onSuccess ? onSuccess(result) : result
      } catch (error) {
        if (onError) {
          onError(error)
        }
        throw error
      }
    }),
    scrollToFirstError: vi.fn(),
    validateNameField: vi.fn(),
    validateEmailField: vi.fn(),
    validatePhoneField: vi.fn(),
    validateDocumentField: vi.fn(),
    validatePasswordFields: vi.fn(),
    validateBirthdateField: vi.fn()
  }))
}))

vi.mock('../useCatalogos', () => ({
  useCatalogos: vi.fn(() => ({
    tiposDocumento: { value: [] },
    generos: { value: [] },
    departamentos: { value: [] },
    municipios: { value: [] },
    isLoadingCatalogos: { value: false },
    cargarCatalogos: vi.fn()
  }))
}))

describe('useForm', () => {
  let form

  beforeEach(() => {
    vi.clearAllMocks()
    form = useForm()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(form.isSubmitting.value).toBe(false)
      expect(form.isDirty.value).toBe(false)
      expect(form.submitCount.value).toBe(0)
    })

    it('should accept initial values', () => {
      const initialValues = { name: 'Test', email: 'test@example.com' }
      const customForm = useForm({ initialValues })
      
      expect(customForm.form.name).toBe('Test')
      expect(customForm.form.email).toBe('test@example.com')
    })
  })

  describe('computed properties', () => {
    it('should compute isValid', () => {
      expect(form.isValid.value).toBe(true)
    })

    it('should compute canSubmit', () => {
      expect(form.canSubmit.value).toBe(true)
    })

    it('should not allow submit when submitting', () => {
      form.isSubmitting.value = true
      
      expect(form.canSubmit.value).toBe(false)
    })
  })

  describe('resetForm', () => {
    it('should reset form to initial values', () => {
      form.form.name = 'Changed'
      form.isDirty.value = true
      
      form.resetForm()
      
      expect(form.isDirty.value).toBe(false)
      expect(form.submitCount.value).toBe(0)
    })

    it('should reset to new values when provided', () => {
      form.resetForm({ name: 'New Name' })
      
      expect(form.form.name).toBe('New Name')
    })
  })

  describe('updateField', () => {
    it('should update field value', () => {
      form.updateField('name', 'New Name')
      
      expect(form.form.name).toBe('New Name')
    })

    it('should remove error when updating field', () => {
      const removeError = vi.fn()
      useFormValidation.mockReturnValueOnce({
        errors: {},
        removeError,
        hasErrors: vi.fn(() => false),
        clearErrors: vi.fn(),
        setError: vi.fn(),
        mapServerErrors: vi.fn(),
        handleFormSubmit: vi.fn(),
        scrollToFirstError: vi.fn(),
        isValidEmail: vi.fn(),
        isValidPhone: vi.fn(),
        isValidDocument: vi.fn(),
        isValidBirthdate: vi.fn(),
        validatePassword: vi.fn(),
        validateNameField: vi.fn(),
        validateEmailField: vi.fn(),
        validatePhoneField: vi.fn(),
        validateDocumentField: vi.fn(),
        validatePasswordFields: vi.fn(),
        validateBirthdateField: vi.fn()
      })
      
      const newForm = useForm()
      newForm.updateField('name', 'Test')
      
      expect(removeError).toHaveBeenCalledWith('name')
    })
  })

  describe('handleSubmit', () => {
    it('should call onSubmit handler', async () => {
      const onSubmit = vi.fn().mockResolvedValue({ success: true })
      const formWithHandler = useForm({ onSubmit })

      await formWithHandler.handleSubmit()

      expect(onSubmit).toHaveBeenCalled()
      expect(formWithHandler.isSubmitting.value).toBe(false)
    })

    it('should handle submit errors', async () => {
      const onSubmit = vi.fn().mockRejectedValue(new Error('Submit failed'))
      const formWithHandler = useForm({ onSubmit })

      await expect(formWithHandler.handleSubmit()).rejects.toThrow('Submit failed')

      expect(onSubmit).toHaveBeenCalled()
      expect(formWithHandler.isSubmitting.value).toBe(false)
    })
  })
})

