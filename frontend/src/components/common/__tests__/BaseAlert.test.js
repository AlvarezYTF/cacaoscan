import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseAlert from '../BaseAlert.vue'

describe('BaseAlert', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Rendering', () => {
    it('should render alert with message', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message'
        }
      })

      expect(wrapper.text()).toContain('Test message')
      expect(wrapper.exists()).toBe(true)
    })

    it('should render alert with title', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message',
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
      expect(wrapper.text()).toContain('Test message')
    })

    it('should not render when show is false', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message',
          show: false
        }
      })

      expect(wrapper.find('div').exists()).toBe(false)
    })
  })

  describe('Variants', () => {
    const variants = ['error', 'success', 'warning', 'info', 'critical']

    for (const variant of variants) {
      it(`should apply correct classes for ${variant} variant`, () => {
        wrapper = mount(BaseAlert, {
          props: {
            message: 'Test message',
            variant
          }
        })

        const alertElement = wrapper.find('.border-l-4')
        expect(alertElement.exists()).toBe(true)
        let expectedBorderClass
        if (variant === 'critical') {
          expectedBorderClass = 'border-red-600'
        } else if (variant === 'error') {
          expectedBorderClass = 'border-red-400'
        } else if (variant === 'success') {
          expectedBorderClass = 'border-green-400'
        } else if (variant === 'warning') {
          expectedBorderClass = 'border-yellow-400'
        } else {
          expectedBorderClass = 'border-blue-400'
        }
        expect(alertElement.classes()).toContain(expectedBorderClass)
      })
    })
  })

  describe('Dismissible', () => {
    it('should show dismiss button when dismissible is true', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      const dismissButton = wrapper.find('button')
      expect(dismissButton.exists()).toBe(true)
    })

    it('should not show dismiss button when dismissible is false', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message',
          dismissible: false
        }
      })

      const dismissButton = wrapper.find('button')
      expect(dismissButton.exists()).toBe(false)
    })

    it('should emit dismiss event when dismiss button is clicked', async () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message',
          dismissible: true
        }
      })

      const dismissButton = wrapper.find('button')
      await dismissButton.trigger('click')

      expect(wrapper.emitted('dismiss')).toBeTruthy()
      expect(wrapper.emitted('update:show')).toBeTruthy()
      expect(wrapper.emitted('update:show')[0]).toEqual([false])
    })
  })

  describe('Slots', () => {
    it('should render slot content when provided', () => {
      wrapper = mount(BaseAlert, {
        props: {
          message: 'Test message'
        },
        slots: {
          default: '<div class="custom-content">Custom content</div>'
        }
      })

      expect(wrapper.find('.custom-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('Custom content')
    })
  })
})

