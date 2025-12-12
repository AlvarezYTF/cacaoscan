/**
 * Unit tests for usePreferences composable
 */

import { describe, it, expect, vi } from 'vitest'
import { usePreferences } from '../usePreferences.js'

describe('usePreferences', () => {
  describe('updateValue', () => {
    it('should update single value and emit', () => {
      const emit = vi.fn()
      const props = {
        modelValue: { setting1: 'value1', setting2: 'value2' }
      }

      const preferences = usePreferences(props, emit)

      preferences.updateValue('setting1', 'newValue')

      expect(emit).toHaveBeenCalledWith('update:modelValue', {
        setting1: 'newValue',
        setting2: 'value2'
      })
    })

    it('should add new value', () => {
      const emit = vi.fn()
      const props = {
        modelValue: { setting1: 'value1' }
      }

      const preferences = usePreferences(props, emit)

      preferences.updateValue('setting2', 'value2')

      expect(emit).toHaveBeenCalledWith('update:modelValue', {
        setting1: 'value1',
        setting2: 'value2'
      })
    })
  })

  describe('handleSave', () => {
    it('should emit save event with modelValue', () => {
      const emit = vi.fn()
      const props = {
        modelValue: { setting1: 'value1' }
      }

      const preferences = usePreferences(props, emit)

      preferences.handleSave()

      expect(emit).toHaveBeenCalledWith('save', { setting1: 'value1' })
    })
  })

  describe('handleReset', () => {
    it('should emit reset event', () => {
      const emit = vi.fn()
      const props = {
        modelValue: {}
      }

      const preferences = usePreferences(props, emit)

      preferences.handleReset()

      expect(emit).toHaveBeenCalledWith('reset')
    })
  })
})

