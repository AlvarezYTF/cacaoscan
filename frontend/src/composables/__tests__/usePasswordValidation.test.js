/**
 * Unit tests for usePasswordValidation composable
 */

import { describe, it, expect } from 'vitest'
import {
  validatePasswordStrength,
  getPasswordValidationError,
  validatePasswordConfirmation,
  getPasswordRequirements,
  validatePassword,
  usePasswordValidation,
  PASSWORD_RULES,
  ERROR_MESSAGES
} from '../usePasswordValidation.js'

describe('usePasswordValidation', () => {
  describe('validatePasswordStrength', () => {
    it('should validate strong password', () => {
      const result = validatePasswordStrength('Password123')
      
      expect(result.isValid).toBe(true)
      expect(result.hasUpperCase).toBe(true)
      expect(result.hasLowerCase).toBe(true)
      expect(result.hasNumber).toBe(true)
    })

    it('should reject weak password', () => {
      const result = validatePasswordStrength('weak')
      
      expect(result.isValid).toBe(false)
      expect(result.length).toBeLessThan(8)
    })

    it('should return simple format', () => {
      const result = validatePasswordStrength('Password123', { format: 'simple' })
      
      expect(result.length).toBe(true)
      expect(result.uppercase).toBe(true)
      expect(result.lowercase).toBe(true)
      expect(result.number).toBe(true)
    })

    it('should handle empty password', () => {
      const result = validatePasswordStrength('')
      
      expect(result.isValid).toBe(false)
      expect(result.length).toBe(0)
    })
  })

  describe('getPasswordValidationError', () => {
    it('should return null for valid password', () => {
      expect(getPasswordValidationError('Password123')).toBe(null)
    })

    it('should return error for empty password', () => {
      expect(getPasswordValidationError('')).toBeTruthy()
    })

    it('should return error for short password', () => {
      expect(getPasswordValidationError('Short1')).toContain('8 caracteres')
    })

    it('should return error for missing uppercase', () => {
      expect(getPasswordValidationError('password123')).toContain('mayúscula')
    })

    it('should return error for missing lowercase', () => {
      expect(getPasswordValidationError('PASSWORD123')).toContain('minúscula')
    })

    it('should return error for missing number', () => {
      expect(getPasswordValidationError('Password')).toContain('número')
    })
  })

  describe('validatePasswordConfirmation', () => {
    it('should return null when passwords match', () => {
      expect(validatePasswordConfirmation('Password123', 'Password123')).toBe(null)
    })

    it('should return error when passwords do not match', () => {
      expect(validatePasswordConfirmation('Password123', 'Password456')).toContain('coinciden')
    })

    it('should return error when confirmation is empty and required', () => {
      expect(validatePasswordConfirmation('Password123', '')).toBeTruthy()
    })

    it('should allow empty confirmation when not required', () => {
      expect(validatePasswordConfirmation('Password123', '', { required: false })).toBe(null)
    })
  })

  describe('getPasswordRequirements', () => {
    it('should return requirements checklist', () => {
      const requirements = getPasswordRequirements('Password123')
      
      expect(Array.isArray(requirements)).toBe(true)
      expect(requirements.length).toBeGreaterThan(0)
      expect(requirements[0]).toHaveProperty('text')
      expect(requirements[0]).toHaveProperty('met')
    })

    it('should show unmet requirements for empty password', () => {
      const requirements = getPasswordRequirements('')
      
      for (const req of requirements) {
        expect(req.met).toBe(false)
      }
    })
  })

  describe('validatePassword', () => {
    it('should validate password successfully', () => {
      const result = validatePassword('Password123')
      
      expect(result.isValid).toBe(true)
      expect(Object.keys(result.errors).length).toBe(0)
    })

    it('should return errors for invalid password', () => {
      const result = validatePassword('weak')
      
      expect(result.isValid).toBe(false)
      expect(result.errors.password).toBeDefined()
    })

    it('should validate password and confirmation', () => {
      const result = validatePassword('Password123', 'Password123', { requireConfirm: true })
      
      expect(result.isValid).toBe(true)
    })

    it('should return error when confirmation does not match', () => {
      const result = validatePassword('Password123', 'Password456', { requireConfirm: true })
      
      expect(result.isValid).toBe(false)
      expect(result.errors.confirmPassword).toBeDefined()
    })
  })

  describe('usePasswordValidation', () => {
    it('should return all validation functions', () => {
      const validation = usePasswordValidation()
      
      expect(typeof validation.validatePasswordStrength).toBe('function')
      expect(typeof validation.getPasswordValidationError).toBe('function')
      expect(typeof validation.validatePasswordConfirmation).toBe('function')
      expect(typeof validation.getPasswordRequirements).toBe('function')
      expect(typeof validation.validatePassword).toBe('function')
      expect(validation.PASSWORD_RULES).toBeDefined()
      expect(validation.ERROR_MESSAGES).toBeDefined()
    })
  })

  describe('constants', () => {
    it('should export PASSWORD_RULES', () => {
      expect(PASSWORD_RULES).toBeDefined()
      expect(PASSWORD_RULES.minLength).toBe(8)
    })

    it('should export ERROR_MESSAGES', () => {
      expect(ERROR_MESSAGES).toBeDefined()
      expect(ERROR_MESSAGES.required).toBeDefined()
    })
  })
})

