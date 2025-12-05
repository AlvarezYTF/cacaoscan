/**
 * Unit tests for useAuthForm composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthForm } from '../useAuthForm.js'

// Test-only mock values - not actual passwords, used exclusively for unit testing
// NOSONAR S2068 - These are test fixtures, not hardcoded production passwords
const TEST_PASSWORD_VALID = 'ExampleValue#123' // NOSONAR S2068
const TEST_PASSWORD_SHORT = 'abc12' // NOSONAR S2068 - 5 characters, less than minimum 6

// Mock dependencies
const mockForm = { email: '', password: '' }
const mockClearErrors = vi.fn()
const mockSetError = vi.fn()
const mockScrollToFirstError = vi.fn()
const mockHandleSubmit = vi.fn().mockResolvedValue({ success: true })

vi.mock('../useForm', () => ({
  useForm: vi.fn(() => ({
    form: mockForm,
    isSubmitting: { value: false },
    clearErrors: mockClearErrors,
    setError: mockSetError,
    scrollToFirstError: mockScrollToFirstError,
    handleSubmit: mockHandleSubmit
  }))
}))

describe('useAuthForm', () => {
  let authForm

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset mock form
    mockForm.email = ''
    mockForm.password = ''
    authForm = useAuthForm()
  })

  describe('initial state', () => {
    it('should have initial status message state', () => {
      expect(authForm.statusMessage.value).toBe('')
      expect(authForm.statusMessageClass.value).toBe('')
    })
  })

  describe('setStatusMessage', () => {
    it('should set success message', () => {
      authForm.setStatusMessage('Success message', 'success')
      
      expect(authForm.statusMessage.value).toBe('Success message')
      expect(authForm.statusMessageClass.value).toContain('green')
    })

    it('should set error message', () => {
      authForm.setStatusMessage('Error message', 'error')
      
      expect(authForm.statusMessage.value).toBe('Error message')
      expect(authForm.statusMessageClass.value).toContain('red')
    })
  })

  describe('validateEmailOrUsername', () => {
    it('should validate valid email', () => {
      const error = authForm.validateEmailOrUsername('test@example.com')
      
      expect(error).toBeNull()
    })

    it('should validate valid username', () => {
      const error = authForm.validateEmailOrUsername('testuser')
      
      expect(error).toBeNull()
    })

    it('should reject invalid input', () => {
      const error = authForm.validateEmailOrUsername('in')
      
      expect(error).toBeTruthy()
    })

    it('should require value', () => {
      const error = authForm.validateEmailOrUsername('')
      
      expect(error).toBeTruthy()
    })
  })

  describe('validatePassword', () => {
    it('should validate password with minimum length', () => {
      const error = authForm.validatePassword(TEST_PASSWORD_VALID)
      
      expect(error).toBeNull()
    })

    it('should reject password too short', () => {
      const error = authForm.validatePassword(TEST_PASSWORD_SHORT)
      
      expect(error).toBeTruthy()
    })

    it('should require password', () => {
      const error = authForm.validatePassword('')
      
      expect(error).toBeTruthy()
    })
  })

  describe('validateAuthForm', () => {
    it('should validate form correctly', () => {
      authForm.form.email = 'test@example.com'
      authForm.form.password = TEST_PASSWORD_VALID
      
      const isValid = authForm.validateAuthForm()
      
      expect(isValid).toBe(true)
    })

    it('should fail validation with invalid email', () => {
      authForm.form.email = 'in'
      authForm.form.password = TEST_PASSWORD_VALID
      
      const isValid = authForm.validateAuthForm()
      
      expect(isValid).toBe(false)
    })
  })

  describe('handleAuthSubmit', () => {
    it('should handle form submission successfully', async () => {
      authForm.form.email = 'test@example.com'
      authForm.form.password = TEST_PASSWORD_VALID
      const onSubmit = vi.fn().mockResolvedValue({ success: true })
      
      const formWithHandler = useAuthForm({ onSubmit })
      formWithHandler.form = { email: 'test@example.com', password: TEST_PASSWORD_VALID }
      
      const result = await formWithHandler.handleAuthSubmit()
      
      expect(result).toBeDefined()
    })

    it('should prevent submission if validation fails', async () => {
      // Set invalid values directly on the form object
      // Since authForm.form should be the same reference as mockForm (spread operator copies by reference for objects)
      // We modify both to ensure they're in sync
      mockForm.email = 'invalid'
      mockForm.password = TEST_PASSWORD_SHORT
      authForm.form.email = 'invalid'
      authForm.form.password = TEST_PASSWORD_SHORT
      
      // Verify that the form values are set correctly
      expect(authForm.form.email).toBe('invalid')
      expect(authForm.form.password).toBe(TEST_PASSWORD_SHORT)
      
      const result = await authForm.handleAuthSubmit()
      
      expect(result).toBe(false)
      expect(authForm.scrollToFirstError).toHaveBeenCalled()
      expect(mockSetError).toHaveBeenCalled()
    })
  })
})

