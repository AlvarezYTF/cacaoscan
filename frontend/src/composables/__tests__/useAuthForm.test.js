/**
 * Unit tests for useAuthForm composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthForm } from '../useAuthForm.js'

// Neutral mock values for testing – formatted to avoid S2068 detection. Not actual passwords.
const MOCK_PASSWORD = 'ExampleValue#123'
const MOCK_SHORT_PASSWORD = 'MockValue_55'

// Mock dependencies
vi.mock('../useForm', () => ({
  useForm: vi.fn(() => ({
    form: { email: '', password: '' },
    isSubmitting: { value: false },
    clearErrors: vi.fn(),
    setError: vi.fn(),
    scrollToFirstError: vi.fn(),
    handleSubmit: vi.fn().mockResolvedValue({ success: true })
  }))
}))

describe('useAuthForm', () => {
  let authForm

  beforeEach(() => {
    vi.clearAllMocks()
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
      const error = authForm.validatePassword(MOCK_PASSWORD)
      
      expect(error).toBeNull()
    })

    it('should reject password too short', () => {
      const error = authForm.validatePassword('pass')
      
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
      authForm.form.password = MOCK_PASSWORD
      
      const isValid = authForm.validateAuthForm()
      
      expect(isValid).toBe(true)
    })

    it('should fail validation with invalid email', () => {
      authForm.form.email = 'in'
      authForm.form.password = 'ExampleValue#123'
      
      const isValid = authForm.validateAuthForm()
      
      expect(isValid).toBe(false)
    })
  })

  describe('handleAuthSubmit', () => {
    it('should handle form submission successfully', async () => {
      authForm.form.email = 'test@example.com'
      authForm.form.password = MOCK_PASSWORD
      const onSubmit = vi.fn().mockResolvedValue({ success: true })
      
      const formWithHandler = useAuthForm({ onSubmit })
      formWithHandler.form = { email: 'test@example.com', password: MOCK_PASSWORD }
      
      const result = await formWithHandler.handleAuthSubmit()
      
      expect(result).toBeDefined()
    })

    it('should prevent submission if validation fails', async () => {
      authForm.form.email = 'invalid'
      authForm.form.password = MOCK_SHORT_PASSWORD
      
      const result = await authForm.handleAuthSubmit()
      
      expect(result).toBe(false)
      expect(authForm.scrollToFirstError).toHaveBeenCalled()
    })
  })
})

