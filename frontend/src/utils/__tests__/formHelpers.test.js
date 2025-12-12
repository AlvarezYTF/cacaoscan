/**
 * Unit tests for form helper utility functions
 */

import { describe, it, expect } from 'vitest'
import {
  buildPasswordType,
  getPasswordFieldName,
  getConfirmPasswordFieldName,
  buildPasswordErrorMessages
} from '../formHelpers.js'

describe('formHelpers', () => {
  describe('buildPasswordType', () => {
    it('should build password type string', () => {
      const result = buildPasswordType()
      expect(result).toBe('password')
    })
  })

  describe('getPasswordFieldName', () => {
    it('should return password field name', () => {
      const result = getPasswordFieldName()
      expect(result).toBe('password')
    })
  })

  describe('getConfirmPasswordFieldName', () => {
    it('should return confirm password field name', () => {
      const result = getConfirmPasswordFieldName()
      expect(result).toBe('confirmPassword')
    })
  })

  describe('buildPasswordErrorMessages', () => {
    it('should build password error messages object', () => {
      const messages = buildPasswordErrorMessages()
      
      expect(messages).toBeDefined()
      expect(messages).toHaveProperty('passwordRequired')
      expect(messages).toHaveProperty('passwordRequirements')
      expect(messages).toHaveProperty('confirmPasswordRequired')
      expect(messages).toHaveProperty('passwordsMismatch')
      expect(messages).toHaveProperty('passwordNotValid')
    })

    it('should return non-empty error messages', () => {
      const messages = buildPasswordErrorMessages()
      
      expect(messages.passwordRequired.length).toBeGreaterThan(0)
      expect(messages.passwordRequirements.length).toBeGreaterThan(0)
      expect(messages.confirmPasswordRequired.length).toBeGreaterThan(0)
      expect(messages.passwordsMismatch.length).toBeGreaterThan(0)
      expect(messages.passwordNotValid.length).toBeGreaterThan(0)
    })

    it('should return consistent messages on multiple calls', () => {
      const messages1 = buildPasswordErrorMessages()
      const messages2 = buildPasswordErrorMessages()
      
      expect(messages1).toEqual(messages2)
    })
  })
})

