/**
 * Unit tests for useFormSectionIcons utility
 */

import { describe, it, expect } from 'vitest'
import { FORM_SECTION_ICONS, getFormSectionIcon } from '../useFormSectionIcons.js'

describe('useFormSectionIcons', () => {
  describe('FORM_SECTION_ICONS', () => {
    it('should export icon constants', () => {
      expect(FORM_SECTION_ICONS.PERSONAL).toBeDefined()
      expect(FORM_SECTION_ICONS.DOCUMENT).toBeDefined()
      expect(FORM_SECTION_ICONS.LOCATION).toBeDefined()
      expect(FORM_SECTION_ICONS.CREDENTIALS).toBeDefined()
    })
  })

  describe('getFormSectionIcon', () => {
    it('should return icon path for PERSONAL', () => {
      const icon = getFormSectionIcon('PERSONAL')
      
      expect(icon).toBe(FORM_SECTION_ICONS.PERSONAL)
      expect(icon).toBeTruthy()
    })

    it('should return icon path for DOCUMENT', () => {
      const icon = getFormSectionIcon('DOCUMENT')
      
      expect(icon).toBe(FORM_SECTION_ICONS.DOCUMENT)
    })

    it('should return icon path for LOCATION', () => {
      const icon = getFormSectionIcon('LOCATION')
      
      expect(icon).toBe(FORM_SECTION_ICONS.LOCATION)
    })

    it('should return icon path for CREDENTIALS', () => {
      const icon = getFormSectionIcon('CREDENTIALS')
      
      expect(icon).toBe(FORM_SECTION_ICONS.CREDENTIALS)
    })

    it('should throw error for invalid section', () => {
      expect(() => getFormSectionIcon('INVALID')).toThrow()
    })
  })
})

