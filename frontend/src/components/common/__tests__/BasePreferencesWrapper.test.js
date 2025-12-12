/**
 * Unit tests for BasePreferencesWrapper component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BasePreferencesWrapper from '../BasePreferencesWrapper.vue'

vi.mock('../BasePreferences.vue', () => ({
  default: {
    name: 'BasePreferences',
    template: `
      <div class="base-preferences">
        <slot name="header-icon"></slot>
        <slot name="content" :value="modelValue" :update="updateValue"></slot>
        <slot name="actions"></slot>
      </div>
    `,
    props: {
      modelValue: Object,
      title: String,
      showHeader: Boolean,
      showActions: Boolean,
      showSaveButton: Boolean,
      showResetButton: Boolean,
      saveButtonText: String,
      resetButtonText: String,
      containerClass: String
    },
    emits: ['update:modelValue', 'save', 'reset']
  }
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

describe('BasePreferencesWrapper', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should use iconPath prop when provided', () => {
      // Note: Vue 3 doesn't throw runtime errors for missing required props in tests.
      // Required props are validated at compile time. This test verifies the prop is used correctly.
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10 L20 20',
          modelValue: {}
        }
      })

      const svgPath = wrapper.find('path')
      expect(svgPath.exists()).toBe(true)
      expect(svgPath.attributes('d')).toBe('M10 10 L20 20')
    })

    it('should accept iconPath prop', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept contentSlotName prop', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {},
          contentSlotName: 'custom-content'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render BasePreferences component', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        }
      })

      expect(wrapper.findComponent({ name: 'BasePreferences' }).exists()).toBe(true)
    })

    it('should pass props to BasePreferences', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: { setting: 'value' },
          title: 'Test Title'
        }
      })

      const basePreferences = wrapper.findComponent({ name: 'BasePreferences' })
      expect(basePreferences.props('title')).toBe('Test Title')
    })
  })

  describe('Events', () => {
    it('should emit update:modelValue event', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        }
      })

      const basePreferences = wrapper.findComponent({ name: 'BasePreferences' })
      basePreferences.vm.$emit('update:modelValue', { setting: 'value' })

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })

    it('should emit save event', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        }
      })

      const basePreferences = wrapper.findComponent({ name: 'BasePreferences' })
      basePreferences.vm.$emit('save', { setting: 'value' })

      expect(wrapper.emitted('save')).toBeTruthy()
    })

    it('should emit reset event', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        }
      })

      const basePreferences = wrapper.findComponent({ name: 'BasePreferences' })
      basePreferences.vm.$emit('reset')

      expect(wrapper.emitted('reset')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render header-icon slot when provided', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        },
        slots: {
          'header-icon': '<svg>Custom Icon</svg>'
        }
      })

      expect(wrapper.text()).toContain('Custom Icon')
    })

    it('should render content slot when provided', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        },
        slots: {
          content: '<div>Custom Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Content')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(BasePreferencesWrapper, {
        props: {
          iconPath: 'M10 10',
          modelValue: {}
        },
        slots: {
          actions: '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })
  })
})

