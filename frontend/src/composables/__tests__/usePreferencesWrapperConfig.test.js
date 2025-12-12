/**
 * Unit tests for usePreferencesWrapperConfig utility
 */

import { describe, it, expect } from 'vitest'
import {
  PREFERENCE_ICONS,
  PREFERENCE_CONFIGS,
  createPreferenceWrapperProps,
  getPreferenceIconPath,
  getPreferenceContentSlotName
} from '../usePreferencesWrapperConfig.js'

describe('usePreferencesWrapperConfig', () => {
  describe('PREFERENCE_ICONS', () => {
    it('should export preference icons', () => {
      expect(PREFERENCE_ICONS.SCAN).toBeDefined()
      expect(PREFERENCE_ICONS.VISUAL).toBeDefined()
    })
  })

  describe('PREFERENCE_CONFIGS', () => {
    it('should export preference configs', () => {
      expect(PREFERENCE_CONFIGS.SCAN).toBeDefined()
      expect(PREFERENCE_CONFIGS.VISUAL).toBeDefined()
      expect(PREFERENCE_CONFIGS.SCAN.title).toBe('Preferencias de Escaneo')
    })
  })

  describe('createPreferenceWrapperProps', () => {
    it('should create props for SCAN type', () => {
      const props = createPreferenceWrapperProps('SCAN')
      
      expect(props.title.default).toBe('Preferencias de Escaneo')
      expect(props.saveButtonText.default).toBe('Guardar Preferencias')
    })

    it('should create props for VISUAL type', () => {
      const props = createPreferenceWrapperProps('VISUAL')
      
      expect(props.title.default).toBe('Ajustes Visuales')
    })

    it('should throw error for invalid type', () => {
      expect(() => createPreferenceWrapperProps('INVALID')).toThrow()
    })
  })

  describe('getPreferenceIconPath', () => {
    it('should return icon path for SCAN', () => {
      const path = getPreferenceIconPath('SCAN')
      
      expect(path).toBe(PREFERENCE_ICONS.SCAN)
    })

    it('should throw error for invalid type', () => {
      expect(() => getPreferenceIconPath('INVALID')).toThrow()
    })
  })

  describe('getPreferenceContentSlotName', () => {
    it('should return slot name for SCAN', () => {
      const slotName = getPreferenceContentSlotName('SCAN')
      
      expect(slotName).toBe('preferences')
    })

    it('should return slot name for VISUAL', () => {
      const slotName = getPreferenceContentSlotName('VISUAL')
      
      expect(slotName).toBe('settings')
    })
  })
})

