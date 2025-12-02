/**
 * Unit tests for testUtils utility
 */

import { describe, it, expect } from 'vitest'
import { generatePassword } from '../testUtils.js'

describe('testUtils', () => {
  describe('generatePassword', () => {
    it('should generate a password string', () => {
      const password = generatePassword()
      
      expect(typeof password).toBe('string')
      expect(password.length).toBeGreaterThan(0)
      expect(password).toContain('Pass!')
    })

    it('should generate unique passwords', () => {
      const password1 = generatePassword()
      const password2 = generatePassword()
      
      // Should be different (very unlikely to be same)
      expect(password1).not.toBe(password2)
    })

    it('should generate password with timestamp and random part', () => {
      const password = generatePassword()
      
      // Should contain timestamp and random part
      expect(password).toMatch(/Pass!.*-.*/)
    })
  })
})

