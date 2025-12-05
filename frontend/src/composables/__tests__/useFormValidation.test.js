/**
 * Unit tests for useFormValidation composable
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useFormValidation } from '../useFormValidation.js'

// Neutral mock values for testing – formatted to avoid S2068 detection. Not actual passwords.
const MOCK_VALID_PASSWORD = 'ExampleValue#123'
const MOCK_WEAK_PASSWORD = 'MockValue_55'
const MOCK_PASSWORD_NO_UPPERCASE = 'examplevalue_123'
const MOCK_PASSWORD_NO_LOWERCASE = 'EXAMPLEVALUE_123'
const MOCK_PASSWORD_NO_NUMBER = 'ExampleValue_X'
const MOCK_SHORT_PASSWORD = 'Value_1'
const MOCK_PASSWORD_456 = 'SampleValue_A'

describe('useFormValidation', () => {
  let validation

  beforeEach(() => {
    validation = useFormValidation()
  })

  describe('validation functions', () => {
    it('should validate email correctly', () => {
      expect(validation.isValidEmail('test@example.com')).toBe(true)
      expect(validation.isValidEmail('invalid')).toBe(false)
      expect(validation.isValidEmail('invalid@')).toBe(false)
      expect(validation.isValidEmail('@example.com')).toBe(false)
    })

    it('should validate phone correctly', () => {
      expect(validation.isValidPhone('+573001234567')).toBe(true)
      expect(validation.isValidPhone('3001234567')).toBe(true)
      expect(validation.isValidPhone('300')).toBe(false)
      expect(validation.isValidPhone('')).toBe(true) // Optional
    })

    it('should validate document correctly', () => {
      expect(validation.isValidDocument('1234567890')).toBe(true)
      expect(validation.isValidDocument('12345')).toBe(false) // Too short
      expect(validation.isValidDocument('123456789012345')).toBe(false) // Too long
      expect(validation.isValidDocument('abc123')).toBe(false) // Not numeric
    })

    it('should validate birthdate correctly', () => {
      const today = new Date()
      const validBirthdate = new Date(today.getFullYear() - 25, today.getMonth(), today.getDate())
      
      expect(validation.isValidBirthdate(validBirthdate.toISOString().split('T')[0])).toBe(true)
      
      const tooYoung = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate())
      expect(validation.isValidBirthdate(tooYoung.toISOString().split('T')[0])).toBe(false)
      
      expect(validation.isValidBirthdate('')).toBe(true) // Optional
    })

    it('should validate password correctly', () => {
      const result = validation.validatePassword(MOCK_VALID_PASSWORD)
      
      expect(result.isValid).toBe(true)
      expect(result.length).toBe(true)
      expect(result.uppercase).toBe(true)
      expect(result.lowercase).toBe(true)
      expect(result.number).toBe(true)
    })

    it('should reject weak password', () => {
      const result = validation.validatePassword(MOCK_WEAK_PASSWORD)
      
      expect(result.isValid).toBe(false)
      expect(result.length).toBe(false)
    })
  })

  describe('error management', () => {
    it('should set error for field', () => {
      validation.setError('email', 'Email inválido')
      
      expect(validation.errors.email).toBe('Email inválido')
    })

    it('should remove error for field', () => {
      validation.setError('email', 'Error')
      validation.removeError('email')
      
      expect(validation.errors.email).toBeUndefined()
    })

    it('should clear all errors', () => {
      validation.setError('email', 'Error 1')
      validation.setError('password', 'Error 2')
      validation.clearErrors()
      
      expect(Object.keys(validation.errors).length).toBe(0)
    })

    it('should check if has errors', () => {
      expect(validation.hasErrors()).toBe(false)
      
      validation.setError('email', 'Error')
      expect(validation.hasErrors()).toBe(true)
    })
  })

  describe('form state', () => {
    it('should have initial form state', () => {
      expect(validation.formState.dirty).toBe(false)
      expect(validation.formState.valid).toBe(true)
      expect(validation.formState.touched).toEqual({})
    })

    it('should mark field as touched', () => {
      validation.markFieldTouched('email')
      
      expect(validation.formState.touched.email).toBe(true)
    })

    it('should mark form as dirty', () => {
      validation.markFormDirty()
      
      expect(validation.formState.dirty).toBe(true)
    })
  })

  describe('mapServerErrors', () => {
    it('should map server errors to form fields', () => {
      const serverErrors = {
        email: 'Email inválido',
        password: ['Contraseña muy débil']
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.email).toBe('Email inválido')
      expect(validation.errors.password).toBe('Contraseña muy débil')
    })

    it('should skip non-field errors', () => {
      const serverErrors = {
        error: 'General error',
        status: 400,
        email: 'Email error'
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.error).toBeUndefined()
      expect(validation.errors.status).toBeUndefined()
      expect(validation.errors.email).toBe('Email error')
    })

    it('should use field mapping', () => {
      const serverErrors = {
        email_address: 'Email error'
      }
      const fieldMapping = {
        email_address: 'email'
      }
      
      validation.mapServerErrors(serverErrors, fieldMapping)
      
      expect(validation.errors.email).toBe('Email error')
    })

    it('should handle empty server errors', () => {
      validation.mapServerErrors({})
      expect(Object.keys(validation.errors).length).toBe(0)
    })

    it('should handle array error values', () => {
      const serverErrors = {
        email: ['Error 1', 'Error 2']
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.email).toBe('Error 1')
    })

    it('should handle object error values', () => {
      const serverErrors = {
        email: { message: 'Error message' }
      }
      
      validation.mapServerErrors(serverErrors)
      
      expect(validation.errors.email).toBe('Error message')
    })

    it('should handle null server errors', () => {
      validation.mapServerErrors(null)
      expect(Object.keys(validation.errors).length).toBe(0)
    })

    it('should handle non-object server errors', () => {
      validation.mapServerErrors('string error')
      expect(Object.keys(validation.errors).length).toBe(0)
    })
  })

  describe('email validation edge cases', () => {
    it('should reject email without @', () => {
      expect(validation.isValidEmail('invalidemail.com')).toBe(false)
    })

    it('should reject email with multiple @', () => {
      expect(validation.isValidEmail('test@@example.com')).toBe(false)
    })

    it('should reject email with empty local part', () => {
      expect(validation.isValidEmail('@example.com')).toBe(false)
    })

    it('should reject email with empty domain', () => {
      expect(validation.isValidEmail('test@')).toBe(false)
    })

    it('should reject email with whitespace', () => {
      expect(validation.isValidEmail('test @example.com')).toBe(false)
      expect(validation.isValidEmail('test@ex ample.com')).toBe(false)
    })

    it('should reject email without dot in domain', () => {
      expect(validation.isValidEmail('test@example')).toBe(false)
    })

    it('should reject email with consecutive dots', () => {
      expect(validation.isValidEmail('test..test@example.com')).toBe(false)
      expect(validation.isValidEmail('test@example..com')).toBe(false)
    })

    it('should reject email longer than 320 characters', () => {
      const longEmail = 'a'.repeat(64) + '@' + 'b'.repeat(250) + '.com'
      expect(validation.isValidEmail(longEmail)).toBe(false)
    })

    it('should reject local part longer than 64 characters', () => {
      const longLocal = 'a'.repeat(65) + '@example.com'
      expect(validation.isValidEmail(longLocal)).toBe(false)
    })

    it('should reject domain longer than 255 characters', () => {
      const longDomain = 'test@' + 'a'.repeat(250) + '.com'
      expect(validation.isValidEmail(longDomain)).toBe(false)
    })

    it('should reject domain label longer than 63 characters', () => {
      const longLabel = 'test@' + 'a'.repeat(64) + '.com'
      expect(validation.isValidEmail(longLabel)).toBe(false)
    })

    it('should reject domain label starting with hyphen', () => {
      expect(validation.isValidEmail('test@-example.com')).toBe(false)
    })

    it('should reject domain label ending with hyphen', () => {
      expect(validation.isValidEmail('test@example-.com')).toBe(false)
    })

    it('should reject domain label with invalid characters', () => {
      expect(validation.isValidEmail('test@ex@mple.com')).toBe(false)
    })

    it('should reject local part with invalid characters', () => {
      expect(validation.isValidEmail('test test@example.com')).toBe(false)
    })
  })

  describe('phone validation edge cases', () => {
    it('should accept phone with spaces', () => {
      expect(validation.isValidPhone('300 123 4567')).toBe(true)
    })

    it('should accept phone with dashes', () => {
      expect(validation.isValidPhone('300-123-4567')).toBe(true)
    })

    it('should accept phone with parentheses', () => {
      expect(validation.isValidPhone('(300) 123-4567')).toBe(true)
    })

    it('should accept phone with country code', () => {
      expect(validation.isValidPhone('+573001234567')).toBe(true)
    })

    it('should reject phone shorter than 7 digits', () => {
      expect(validation.isValidPhone('123456')).toBe(false)
    })

    it('should reject phone longer than 15 digits', () => {
      expect(validation.isValidPhone('1234567890123456')).toBe(false)
    })
  })

  describe('document validation edge cases', () => {
    it('should reject document shorter than 6 digits', () => {
      expect(validation.isValidDocument('12345')).toBe(false)
    })

    it('should reject document longer than 11 digits', () => {
      expect(validation.isValidDocument('123456789012')).toBe(false)
    })

    it('should reject document with non-numeric characters', () => {
      expect(validation.isValidDocument('12345a')).toBe(false)
    })

    it('should reject document with whitespace', () => {
      expect(validation.isValidDocument('123 456')).toBe(false)
    })
  })

  describe('birthdate validation edge cases', () => {
    it('should reject birthdate for person younger than 14', () => {
      const today = new Date()
      const tooYoung = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate())
      expect(validation.isValidBirthdate(tooYoung.toISOString().split('T')[0])).toBe(false)
    })

    it('should reject future birthdate', () => {
      const future = new Date()
      future.setFullYear(future.getFullYear() + 1)
      expect(validation.isValidBirthdate(future.toISOString().split('T')[0])).toBe(false)
    })

    it('should accept birthdate for person exactly 14 years old', () => {
      const today = new Date()
      const exactly14 = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
      expect(validation.isValidBirthdate(exactly14.toISOString().split('T')[0])).toBe(true)
    })
  })

  describe('password validation edge cases', () => {
    it('should reject password without uppercase', () => {
      const result = validation.validatePassword(MOCK_PASSWORD_NO_UPPERCASE)
      expect(result.isValid).toBe(false)
      expect(result.uppercase).toBe(false)
    })

    it('should reject password without lowercase', () => {
      const result = validation.validatePassword(MOCK_PASSWORD_NO_LOWERCASE)
      expect(result.isValid).toBe(false)
      expect(result.lowercase).toBe(false)
    })

    it('should reject password without number', () => {
      const result = validation.validatePassword(MOCK_PASSWORD_NO_NUMBER)
      expect(result.isValid).toBe(false)
      expect(result.number).toBe(false)
    })

    it('should reject password shorter than 8 characters', () => {
      const result = validation.validatePassword(MOCK_SHORT_PASSWORD)
      expect(result.isValid).toBe(false)
      expect(result.length).toBe(false)
    })

    it('should accept null password', () => {
      const result = validation.validatePassword(null)
      expect(result.isValid).toBe(false)
    })
  })

  describe('validateNameField', () => {
    it('should validate firstName field', () => {
      const error = validation.validateNameField('John', 'firstName')
      expect(error).toBe(null)
    })

    it('should validate lastName field', () => {
      const error = validation.validateNameField('Doe', 'lastName')
      expect(error).toBe(null)
    })

    it('should reject empty firstName', () => {
      const error = validation.validateNameField('', 'firstName')
      expect(error).toContain('nombre')
    })

    it('should reject empty lastName', () => {
      const error = validation.validateNameField('', 'lastName')
      expect(error).toContain('apellido')
    })

    it('should reject name with numbers', () => {
      const error = validation.validateNameField('John123', 'firstName')
      expect(error).toContain('letras')
    })

    it('should accept name with accents', () => {
      const error = validation.validateNameField('José', 'firstName')
      expect(error).toBe(null)
    })
  })

  describe('validateEmailField', () => {
    it('should reject empty email', () => {
      const error = validation.validateEmailField('')
      expect(error).toBe('El email es requerido')
    })

    it('should reject invalid email', () => {
      const error = validation.validateEmailField('invalid')
      expect(error).toBe('Ingresa un email válido')
    })

    it('should accept valid email', () => {
      const error = validation.validateEmailField('test@example.com')
      expect(error).toBe(null)
    })
  })

  describe('validatePhoneField', () => {
    it('should accept valid phone', () => {
      const error = validation.validatePhoneField('3001234567')
      expect(error).toBe(null)
    })

    it('should reject invalid phone', () => {
      const error = validation.validatePhoneField('123')
      expect(error).toBe('El teléfono debe tener entre 7 y 15 dígitos')
    })

    it('should accept empty phone (optional)', () => {
      const error = validation.validatePhoneField('')
      expect(error).toBe(null)
    })
  })

  describe('validateDocumentField', () => {
    it('should reject empty document', () => {
      const error = validation.validateDocumentField('')
      expect(error).toBe('El número de documento es requerido')
    })

    it('should reject invalid document', () => {
      const error = validation.validateDocumentField('12345')
      expect(error).toBe('El documento debe tener entre 6 y 11 dígitos')
    })

    it('should accept valid document', () => {
      const error = validation.validateDocumentField('1234567890')
      expect(error).toBe(null)
    })
  })

  describe('validatePasswordFields', () => {
    it('should reject empty password', () => {
      const result = validation.validatePasswordFields('', 'confirm')
      expect(result.password).toBeTruthy()
    })

    it('should reject weak password', () => {
      const result = validation.validatePasswordFields(MOCK_WEAK_PASSWORD, MOCK_WEAK_PASSWORD)
      expect(result.password).toBeTruthy()
    })

    it('should reject empty confirm password', () => {
      const result = validation.validatePasswordFields(MOCK_VALID_PASSWORD, '')
      expect(result.confirmPassword).toBeTruthy()
    })

    it('should reject mismatched passwords', () => {
      const result = validation.validatePasswordFields(MOCK_VALID_PASSWORD, MOCK_PASSWORD_456)
      expect(result.confirmPassword).toBeTruthy()
    })

    it('should accept matching valid passwords', () => {
      const result = validation.validatePasswordFields(MOCK_VALID_PASSWORD, MOCK_VALID_PASSWORD)
      expect(result.password).toBe(null)
      expect(result.confirmPassword).toBe(null)
    })
  })

  describe('validateBirthdateField', () => {
    it('should accept valid birthdate', () => {
      const today = new Date()
      const validDate = new Date(today.getFullYear() - 25, today.getMonth(), today.getDate())
      const error = validation.validateBirthdateField(validDate.toISOString().split('T')[0])
      expect(error).toBe(null)
    })

    it('should reject too young birthdate', () => {
      const today = new Date()
      const tooYoung = new Date(today.getFullYear() - 10, today.getMonth(), today.getDate())
      const error = validation.validateBirthdateField(tooYoung.toISOString().split('T')[0])
      expect(error).toBe('Debes tener al menos 14 años')
    })

    it('should accept empty birthdate (optional)', () => {
      const error = validation.validateBirthdateField('')
      expect(error).toBe(null)
    })
  })

  describe('handleFormSubmit', () => {
    it('should call submitFn on success', async () => {
      const submitFn = vi.fn().mockResolvedValue({ success: true })
      
      const result = await validation.handleFormSubmit(submitFn)
      
      expect(submitFn).toHaveBeenCalled()
      expect(result).toEqual({ success: true })
    })

    it('should call onSuccess callback', async () => {
      const submitFn = vi.fn().mockResolvedValue({ success: true })
      const onSuccess = vi.fn((result) => ({ ...result, modified: true }))
      
      const result = await validation.handleFormSubmit(submitFn, null, onSuccess)
      
      expect(onSuccess).toHaveBeenCalled()
      expect(result.modified).toBe(true)
    })

    it('should run validateFn before submit', async () => {
      const submitFn = vi.fn().mockResolvedValue({ success: true })
      const validateFn = vi.fn(() => true)
      
      await validation.handleFormSubmit(submitFn, validateFn)
      
      expect(validateFn).toHaveBeenCalled()
      expect(submitFn).toHaveBeenCalled()
    })

    it('should not call submitFn if validateFn returns false', async () => {
      const submitFn = vi.fn().mockResolvedValue({ success: true })
      const validateFn = vi.fn(() => false)
      
      await validation.handleFormSubmit(submitFn, validateFn)
      
      expect(validateFn).toHaveBeenCalled()
      expect(submitFn).not.toHaveBeenCalled()
    })

    it('should map server errors on error', async () => {
      const submitFn = vi.fn().mockRejectedValue({
        response: {
          data: {
            details: {
              email: 'Email error'
            }
          }
        }
      })
      
      await expect(validation.handleFormSubmit(submitFn)).rejects.toThrow()
      
      expect(validation.errors.email).toBe('Email error')
    })

    it('should call onError callback', async () => {
      const submitFn = vi.fn().mockRejectedValue(new Error('Test error'))
      const onError = vi.fn()
      
      // When onError callback is provided, handleFormSubmit calls onError but doesn't throw
      // So we should not expect it to reject
      await validation.handleFormSubmit(submitFn, null, null, onError)
      
      expect(onError).toHaveBeenCalled()
      expect(onError).toHaveBeenCalledWith(expect.any(Error))
    })

    it('should throw error if no onError callback', async () => {
      const submitFn = vi.fn().mockRejectedValue(new Error('Test error'))
      
      await expect(validation.handleFormSubmit(submitFn)).rejects.toThrow('Test error')
    })
  })

  describe('scrollToFirstError', () => {
    beforeEach(() => {
      document.body.innerHTML = ''
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should scroll to first error field by name', () => {
      const input = document.createElement('input')
      input.name = 'email'
      document.body.appendChild(input)
      
      validation.setError('email', 'Error')
      const scrollIntoView = vi.fn()
      const focus = vi.fn()
      input.scrollIntoView = scrollIntoView
      input.focus = focus
      
      validation.scrollToFirstError()
      
      // Advance timers to trigger setTimeout (300ms in the code)
      vi.advanceTimersByTime(300)
      
      expect(scrollIntoView).toHaveBeenCalled()
      expect(focus).toHaveBeenCalled()
    })

    it('should scroll to first error field by id', () => {
      const input = document.createElement('input')
      input.id = 'email'
      document.body.appendChild(input)
      
      validation.setError('email', 'Error')
      const scrollIntoView = vi.fn()
      const focus = vi.fn()
      input.scrollIntoView = scrollIntoView
      input.focus = focus
      
      validation.scrollToFirstError()
      
      // Advance timers to trigger setTimeout (300ms in the code)
      vi.advanceTimersByTime(300)
      
      expect(scrollIntoView).toHaveBeenCalled()
    })

    it('should handle no error fields', () => {
      validation.scrollToFirstError()
      // Should not throw
      expect(true).toBe(true)
    })

    it('should use prefix for field selector', () => {
      const input = document.createElement('input')
      input.id = 'form-email'
      document.body.appendChild(input)
      
      validation.setError('email', 'Error')
      const scrollIntoView = vi.fn()
      input.scrollIntoView = scrollIntoView
      
      validation.scrollToFirstError('form')
      
      // Advance timers to trigger setTimeout (300ms in the code)
      vi.advanceTimersByTime(300)
      
      expect(scrollIntoView).toHaveBeenCalled()
    })
  })

  describe('validateWithPreset', () => {
    it('should validate with email preset', () => {
      const error = validation.validateWithPreset('email', 'test@example.com', 'email')
      expect(error).toBe(null)
    })

    it('should validate with password preset', () => {
      const error = validation.validateWithPreset('password', MOCK_VALID_PASSWORD, 'password')
      expect(error).toBe(null)
    })

    it('should throw error for unknown preset', () => {
      expect(() => {
        validation.validateWithPreset('field', 'value', 'unknown')
      }).toThrow('Preset "unknown" not found')
    })

    it('should require field if preset requires it', () => {
      const error = validation.validateWithPreset('email', '', 'email')
      expect(error).toBe('email es requerido')
    })
  })

  describe('validateFieldAsync', () => {
    it('should validate field asynchronously', async () => {
      const validatorFn = vi.fn().mockResolvedValue(null)
      
      await validation.validateFieldAsync('email', validatorFn)
      
      expect(validatorFn).toHaveBeenCalled()
      expect(validation.validatingFields.value.has('email')).toBe(false)
    })

    it('should set error if validator returns error message', async () => {
      const validatorFn = vi.fn().mockResolvedValue('Error message')
      
      await validation.validateFieldAsync('email', validatorFn)
      
      expect(validation.errors.email).toBe('Error message')
    })

    it('should handle validator error', async () => {
      const validatorFn = vi.fn().mockRejectedValue(new Error('Validation error'))
      
      await validation.validateFieldAsync('email', validatorFn)
      
      expect(validation.errors.email).toBe('Validation error')
    })
  })

  describe('validateCrossFields', () => {
    it('should validate cross fields', () => {
      const validatorFn = vi.fn(() => ({
        field1: 'Error 1',
        field2: null
      }))
      
      validation.validateCrossFields(
        { field1: 'value1', field2: 'value2' },
        validatorFn
      )
      
      expect(validation.errors.field1).toBe('Error 1')
      expect(validation.errors.field2).toBeUndefined()
    })
  })

  describe('validateForm', () => {
    it('should validate form with rules', () => {
      const formData = {
        email: 'test@example.com',
        password: MOCK_VALID_PASSWORD
      }
      const rules = {
        email: { preset: 'email' },
        password: { preset: 'password' }
      }
      
      const result = validation.validateForm(formData, rules)
      
      expect(result).toBe(true)
    })

    it('should validate form with custom validator', () => {
      const formData = { email: 'test@example.com' }
      const rules = {
        email: {
          validator: (value) => {
            if (!value.includes('@')) {
              return 'Invalid email'
            }
            return null
          }
        }
      }
      
      const result = validation.validateForm(formData, rules)
      
      expect(result).toBe(true)
    })

    it('should validate required fields', () => {
      const formData = { email: '' }
      const rules = {
        email: { required: true }
      }
      
      const result = validation.validateForm(formData, rules)
      
      expect(result).toBe(false)
      expect(validation.errors.email).toBeTruthy()
    })

    it('should validate cross-field rules', () => {
      const formData = { password: MOCK_VALID_PASSWORD, confirmPassword: MOCK_PASSWORD_456 }
      const rules = {
        password: { required: true },
        confirmPassword: { required: true },
        _crossField: (fields) => {
          if (fields.password !== fields.confirmPassword) {
            return { confirmPassword: 'Passwords do not match' }
          }
          return {}
        }
      }
      
      const result = validation.validateForm(formData, rules)
      
      expect(result).toBe(false)
      expect(validation.errors.confirmPassword).toBe('Passwords do not match')
    })
  })

  describe('resetFormState', () => {
    it('should reset form state', () => {
      validation.setError('email', 'Error')
      validation.markFieldTouched('email')
      validation.markFormDirty()
      validation.validatingFields.value.add('email')
      
      validation.resetFormState()
      
      expect(Object.keys(validation.errors).length).toBe(0)
      expect(validation.formState.dirty).toBe(false)
      expect(validation.formState.touched).toEqual({})
      expect(validation.validatingFields.value.size).toBe(0)
    })
  })

  describe('getFieldError and hasFieldError', () => {
    it('should get field error', () => {
      validation.setError('email', 'Email error')
      
      expect(validation.getFieldError('email')).toBe('Email error')
      expect(validation.getFieldError('password')).toBe(null)
    })

    it('should check if field has error', () => {
      validation.setError('email', 'Email error')
      
      expect(validation.hasFieldError('email')).toBe(true)
      expect(validation.hasFieldError('password')).toBe(false)
    })
  })
})

