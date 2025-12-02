/**
 * Unit tests for errorMessages utility
 */

import { describe, it, expect, vi } from 'vitest'
import { getErrorMessages } from '../errorMessages.js'
import { buildPasswordErrorMessages } from '../formHelpers'

// Mock formHelpers
vi.mock('../formHelpers', () => ({
  buildPasswordErrorMessages: vi.fn(() => ({
    password_required: 'Password is required',
    password_too_short: 'Password is too short'
  }))
}))

describe('errorMessages', () => {
  describe('getErrorMessages', () => {
    it('should return error messages object', () => {
      const messages = getErrorMessages()
      
      expect(messages).toBeDefined()
      expect(messages.password_required).toBeDefined()
      expect(buildPasswordErrorMessages).toHaveBeenCalled()
    })

    it('should delegate to buildPasswordErrorMessages', () => {
      getErrorMessages()
      
      expect(buildPasswordErrorMessages).toHaveBeenCalled()
    })
  })
})

