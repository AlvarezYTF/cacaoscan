/**
 * Unit tests for usePreferencesProps utility
 */

import { describe, it, expect } from 'vitest'
import { basePreferencesProps } from '../usePreferencesProps.js'

describe('usePreferencesProps', () => {
  describe('basePreferencesProps', () => {
    it('should export base preferences props', () => {
      expect(basePreferencesProps).toBeDefined()
      expect(basePreferencesProps.modelValue).toBeDefined()
      expect(basePreferencesProps.title).toBeDefined()
    })

    it('should have modelValue as required object', () => {
      expect(basePreferencesProps.modelValue.required).toBe(true)
      expect(basePreferencesProps.modelValue.type).toBe(Object)
    })

    it('should have default values for optional props', () => {
      expect(basePreferencesProps.showHeader.default).toBe(true)
      expect(basePreferencesProps.showActions.default).toBe(true)
      expect(basePreferencesProps.showSaveButton.default).toBe(true)
      expect(basePreferencesProps.showResetButton.default).toBe(false)
    })
  })
})

