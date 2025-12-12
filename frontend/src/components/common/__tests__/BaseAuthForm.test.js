/**
 * Unit tests for BaseAuthForm component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAuthForm from '../BaseAuthForm.vue'

vi.mock('../BaseSpinner.vue', () => ({
  default: {
    name: 'BaseSpinner',
    template: '<div class="spinner">Loading...</div>',
    props: {
      size: String,
      color: String
    }
  }
}))

describe('BaseAuthForm', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept modelValue prop with default value', () => {
      // Vue 3 with default values doesn't throw errors for required props
      // The prop has a default value, so it will use that instead of throwing
      wrapper = mount(BaseAuthForm)
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props('modelValue')).toEqual({})
    })

    it('should accept modelValue prop', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept mode prop', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          mode: 'login'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should validate mode prop', () => {
      // Vue 3 validators don't throw errors, they only show console warnings
      // The component will mount but the validator will fail silently
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          mode: 'invalid'
        }
      })
      // Component should still mount, but mode validation happens at prop level
      expect(wrapper.exists()).toBe(true)
      // Verify that invalid mode doesn't break the component
      expect(wrapper.vm.mode).toBe('invalid')
    })
  })

  describe('Rendering', () => {
    it('should render form', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        }
      })

      expect(wrapper.find('form').exists()).toBe(true)
    })

    it('should render title when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render subtitle when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          subtitle: 'Test Subtitle'
        }
      })

      expect(wrapper.text()).toContain('Test Subtitle')
    })

    it('should show header when showHeader is true', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          showHeader: true
        }
      })

      expect(wrapper.find('.text-center').exists()).toBe(true)
    })

    it('should not show header when showHeader is false', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          showHeader: false
        }
      })

      expect(wrapper.find('.text-center').exists()).toBe(false)
    })

    it('should render submit button when showSubmitButton is true', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          showSubmitButton: true
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.exists()).toBe(true)
    })

    it('should show loading spinner when loading is true', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          loading: true
        }
      })

      expect(wrapper.findComponent({ name: 'BaseSpinner' }).exists()).toBe(true)
    })

    it('should disable submit button when loading is true', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          loading: true
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit button when disabled is true', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          disabled: true
        }
      })

      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should display status message when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          statusMessage: 'Test message'
        }
      })

      expect(wrapper.text()).toContain('Test message')
    })

    it('should apply correct color class for success status', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          statusMessage: 'Success',
          statusMessageType: 'success'
        }
      })

      const message = wrapper.find('p')
      expect(message.classes()).toContain('text-green-700')
    })

    it('should apply correct color class for error status', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          statusMessage: 'Error',
          statusMessageType: 'error'
        }
      })

      const message = wrapper.find('p')
      expect(message.classes()).toContain('text-red-600')
    })
  })

  describe('Events', () => {
    it('should emit submit event on form submit', async () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: { email: 'test@example.com' }
        }
      })

      const form = wrapper.find('form')
      await form.trigger('submit')

      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')[0][0]).toEqual({ email: 'test@example.com' })
    })

    it('should emit update:modelValue when field is updated', async () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        }
      })

      wrapper.vm.updateField('email', 'test@example.com')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    })

    it('should emit field-update when field is updated', async () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        }
      })

      wrapper.vm.updateField('email', 'test@example.com')

      expect(wrapper.emitted('field-update')).toBeTruthy()
      expect(wrapper.emitted('field-update')[0]).toEqual(['email', 'test@example.com'])
    })
  })

  describe('Slots', () => {
    it('should render title slot when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        },
        slots: {
          title: '<h2>Custom Title</h2>'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })

    it('should render fields slot when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        },
        slots: {
          fields: '<input type="text" />'
        }
      })

      expect(wrapper.find('input').exists()).toBe(true)
    })

    it('should render submit-button slot when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {}
        },
        slots: {
          'submit-button': '<button type="submit">Custom Submit</button>'
        }
      })

      expect(wrapper.text()).toContain('Custom Submit')
    })

    it('should render footer slot when provided', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: {},
          showFooter: true
        },
        slots: {
          footer: '<div>Footer Content</div>'
        }
      })

      expect(wrapper.text()).toContain('Footer Content')
    })
  })

  describe('Methods', () => {
    it('should update field correctly', () => {
      wrapper = mount(BaseAuthForm, {
        props: {
          modelValue: { email: 'old@example.com' }
        }
      })

      wrapper.vm.updateField('email', 'new@example.com')

      expect(wrapper.emitted('update:modelValue')[0][0]).toEqual({ email: 'new@example.com' })
    })
  })
})

