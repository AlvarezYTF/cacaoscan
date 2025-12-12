/**
 * Unit tests for BasePreferences component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BasePreferences from '../BasePreferences.vue'

vi.mock('@/composables/usePreferences', () => ({
  usePreferences: vi.fn((props, emit) => ({
    updateValue: (key, value) => {
      const updated = { ...props.modelValue, [key]: value }
      emit('update:modelValue', updated)
    },
    handleSave: () => {
      emit('save', props.modelValue)
    },
    handleReset: () => {
      emit('reset')
    }
  }))
}))

vi.mock('@/composables/usePreferencesProps', () => ({
  basePreferencesProps: {
    modelValue: {
      type: Object,
      default: () => ({})
    },
    title: {
      type: String,
      default: 'Preferencias'
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    showActions: {
      type: Boolean,
      default: true
    },
    showSaveButton: {
      type: Boolean,
      default: true
    },
    showResetButton: {
      type: Boolean,
      default: true
    },
    saveButtonText: {
      type: String,
      default: 'Guardar'
    },
    resetButtonText: {
      type: String,
      default: 'Restablecer'
    },
    containerClass: {
      type: String,
      default: ''
    }
  }
}))

describe('BasePreferences', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept modelValue prop', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {}
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept title prop', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          title: 'Test Title'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render title when provided', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should show header when showHeader is true', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showHeader: true
        }
      })

      expect(wrapper.find('.flex.items-center').exists()).toBe(true)
    })

    it('should not show header when showHeader is false', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showHeader: false
        }
      })

      // Use a more specific selector that matches only the header (which has gap-3 and mb-6 classes)
      // The button also has flex items-center but doesn't have gap-3 mb-6
      const headerElement = wrapper.find('.flex.items-center.gap-3.mb-6')
      expect(headerElement.exists()).toBe(false)
    })

    it('should show save button when showSaveButton is true', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showSaveButton: true
        }
      })

      expect(wrapper.text()).toContain('Guardar')
    })

    it('should show reset button when showResetButton is true', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showResetButton: true
        }
      })

      expect(wrapper.text()).toContain('Restablecer')
    })
  })

  describe('Events', () => {
    it('should emit update:modelValue when value is updated', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {}
        }
      })

      wrapper.vm.updateValue('setting1', 'value1')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })

    it('should emit save event when save button is clicked', async () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showSaveButton: true
        }
      })

      const saveButton = wrapper.find('button')
      await saveButton.trigger('click')

      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('should emit reset event when reset button is clicked', async () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showResetButton: true
        }
      })

      const resetButton = wrapper.findAll('button').find(btn => btn.text().includes('Restablecer'))
      await resetButton.trigger('click')

      expect(wrapper.emitted('reset')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render content slot when provided', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {}
        },
        slots: {
          content: '<div>Custom Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Content')
    })

    it('should render header-icon slot when provided', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {}
        },
        slots: {
          'header-icon': '<svg>Icon</svg>'
        }
      })

      expect(wrapper.find('svg').exists()).toBe(true)
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BasePreferences, {
        props: {
          modelValue: {},
          showActions: true
        },
        slots: {
          actions: '<button>Custom Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Custom Action')
    })
  })
})

