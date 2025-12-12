/**
 * Unit tests for useEmailValidation composable
 * Pure functions with no external dependencies - deterministic tests
 */

import { describe, it, expect } from 'vitest'
import { isValidEmail, useEmailValidation } from '../useEmailValidation.js'

describe('useEmailValidation', () => {
  describe('isValidEmail', () => {
    it('should validate valid email addresses', () => {
      expect(isValidEmail('test@example.com')).toBe(true)
      expect(isValidEmail('user.name@example.co.uk')).toBe(true)
      expect(isValidEmail('user+tag@example.com')).toBe(true)
      expect(isValidEmail('user_name@example.com')).toBe(true)
      expect(isValidEmail('user-name@example.com')).toBe(true)
    })

    it('should reject invalid email addresses', () => {
      expect(isValidEmail('invalid')).toBe(false)
      expect(isValidEmail('invalid@')).toBe(false)
      expect(isValidEmail('@example.com')).toBe(false)
      expect(isValidEmail('user@')).toBe(false)
      expect(isValidEmail('user@domain')).toBe(false)
    })

    it('should reject emails with consecutive dots', () => {
      expect(isValidEmail('user..name@example.com')).toBe(false)
    })

    it('should reject emails starting with dot', () => {
      expect(isValidEmail('.user@example.com')).toBe(false)
    })

    it('should reject emails ending with dot', () => {
      expect(isValidEmail('user.@example.com')).toBe(false)
    })

    it('should reject emails without domain extension', () => {
      expect(isValidEmail('user@domain')).toBe(false)
    })

    it('should reject empty email', () => {
      expect(isValidEmail('')).toBe(false)
      expect(isValidEmail('   ')).toBe(false)
    })

    it('should reject null email', () => {
      expect(isValidEmail(null)).toBe(false)
    })

    it('should reject undefined email', () => {
      expect(isValidEmail(undefined)).toBe(false)
    })

    it('should reject non-string email', () => {
      expect(isValidEmail(123)).toBe(false)
      expect(isValidEmail({})).toBe(false)
    })

    it('should reject emails that are too long', () => {
      const longEmail = 'a'.repeat(250) + '@example.com'
      expect(isValidEmail(longEmail)).toBe(false)
    })

    it('should reject local part that is too long', () => {
      const longLocal = 'a'.repeat(65) + '@example.com'
      expect(isValidEmail(longLocal)).toBe(false)
    })

    it('should validate emails with numbers', () => {
      expect(isValidEmail('user123@example.com')).toBe(true)
      expect(isValidEmail('user@example123.com')).toBe(true)
    })

    it('should validate emails with mixed case', () => {
      expect(isValidEmail('User@Example.com')).toBe(true)
    })

    it('should reject emails with invalid characters in local part', () => {
      expect(isValidEmail('user#name@example.com')).toBe(false)
      expect(isValidEmail('user$name@example.com')).toBe(false)
    })

    it('should reject emails with invalid characters in domain part', () => {
      expect(isValidEmail('user@exam_ple.com')).toBe(false)
      expect(isValidEmail('user@exam+ple.com')).toBe(false)
    })

    it('should reject domain part that is too long', () => {
      const longDomain = 'a'.repeat(254) + '.com'
      expect(isValidEmail(`user@${longDomain}`)).toBe(false)
    })

    it('should reject domain with empty parts', () => {
      expect(isValidEmail('user@.com')).toBe(false)
      expect(isValidEmail('user@example.')).toBe(false)
    })

    it('should reject domain with less than 2 parts', () => {
      expect(isValidEmail('user@domain')).toBe(false)
    })

    it('should handle codePointAt returning undefined', () => {
      // This tests the edge case where codePointAt might return undefined
      // We can't directly test this, but we can test with empty string
      expect(isValidEmail('')).toBe(false)
    })

    it('should validate domain with multiple dots', () => {
      expect(isValidEmail('user@example.co.uk')).toBe(true)
    })

    it('should reject local part with invalid characters', () => {
      expect(isValidEmail('user@name@example.com')).toBe(false)
    })
  })

  describe('useEmailValidation', () => {
    it('should return validation functions', () => {
      const { isValidEmail: validate } = useEmailValidation()
      
      expect(typeof validate).toBe('function')
      expect(validate('test@example.com')).toBe(true)
      expect(validate('invalid')).toBe(false)
    })
  })
})

