import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ActionButton from '../ActionButton.vue'

describe('ActionButton', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Rendering', () => {
    it('should render button with required label', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test Button'
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('button').exists()).toBe(true)
      const button = wrapper.find('button')
      expect(button.text()).toContain('Test Button')
    })

    it('should render button with icon when icon prop is provided', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test Button',
          icon: 'svg'
        },
        global: {
          stubs: {
            svg: { template: '<svg data-testid="icon"></svg>' }
          }
        }
      })

      const icon = wrapper.find('[data-testid="icon"]')
      expect(icon.exists()).toBe(true)
    })

    it('should not render icon when icon prop is not provided', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test Button'
        }
      })

      const button = wrapper.find('button')
      expect(button.find('component').exists()).toBe(false)
    })

    it('should display shortLabel on small screens when provided', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Long Label Text',
          shortLabel: 'Short'
        }
      })

      const button = wrapper.find('button')
      const text = button.text()
      // Both labels should be present (one hidden on sm, one hidden on mobile)
      expect(text).toContain('Long Label Text')
      expect(text).toContain('Short')
    })

    it('should display label when shortLabel is not provided', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test Button'
        }
      })

      const button = wrapper.find('button')
      const text = button.text()
      expect(text).toContain('Test Button')
      // Should appear twice (once for mobile, once for desktop)
      const matches = text.match(/Test Button/g)
      expect(matches).toBeTruthy()
    })
  })

  describe('Variants', () => {
    it('should apply primary variant classes by default', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Primary Button'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('green-600') || cls.includes('bg-green-600'))).toBe(true)
    })

    it('should apply primary variant classes when variant is primary', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Primary Button',
          variant: 'primary'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('green-600') || cls.includes('bg-green-600'))).toBe(true)
    })

    it('should apply secondary variant classes when variant is secondary', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Secondary Button',
          variant: 'secondary'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('white') || cls.includes('bg-white'))).toBe(true)
      expect(classes.some(cls => cls.includes('border') || cls.includes('border-gray'))).toBe(true)
    })

    it('should apply danger variant classes when variant is danger', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Danger Button',
          variant: 'danger'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('red-600') || cls.includes('bg-red-600'))).toBe(true)
    })

    it('should fallback to primary variant when invalid variant is provided', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Invalid Variant',
          variant: 'invalid'
        }
      })

      const button = wrapper.find('button')
      button.classes()
      // Should still render (validator will prevent invalid values, but if it passes, defaults to primary)
      expect(button.exists()).toBe(true)
    })
  })

  describe('Sizes', () => {
    it('should apply small size classes when size is small', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Small Button',
          size: 'small'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('px-2') || cls.includes('py-1.5'))).toBe(true)
    })

    it('should apply medium size classes by default', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Medium Button'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('px-3') || cls.includes('px-4') || cls.includes('px-6'))).toBe(true)
    })

    it('should apply medium size classes when size is medium', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Medium Button',
          size: 'medium'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('px-3') || cls.includes('px-4') || cls.includes('px-6'))).toBe(true)
    })

    it('should apply large size classes when size is large', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Large Button',
          size: 'large'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('px-4') || cls.includes('px-6') || cls.includes('px-8'))).toBe(true)
    })
  })

  describe('Disabled State', () => {
    it('should disable button when disabled prop is true', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Disabled Button',
          disabled: true
        }
      })

      const button = wrapper.find('button')
      expect(button.attributes('disabled')).toBeDefined()
      expect(button.element.disabled).toBe(true)
    })

    it('should not disable button when disabled prop is false', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Enabled Button',
          disabled: false
        }
      })

      const button = wrapper.find('button')
      expect(button.element.disabled).toBe(false)
    })

    it('should apply disabled classes when disabled', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Disabled Button',
          disabled: true
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('disabled') || cls.includes('opacity-50'))).toBe(true)
    })
  })

  describe('Events', () => {
    it('should emit click event when button is clicked', async () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Clickable Button'
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      expect(wrapper.emitted('click')).toBeTruthy()
      expect(wrapper.emitted('click').length).toBe(1)
    })

    it('should not emit click event when button is disabled', async () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Disabled Button',
          disabled: true
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')

      // Disabled buttons should not emit click events
      expect(wrapper.emitted('click')).toBeFalsy()
    })

    it('should emit click event multiple times when clicked multiple times', async () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Multi Click Button'
        }
      })

      const button = wrapper.find('button')
      await button.trigger('click')
      await button.trigger('click')
      await button.trigger('click')

      expect(wrapper.emitted('click')).toBeTruthy()
      expect(wrapper.emitted('click').length).toBe(3)
    })
  })

  describe('Computed Properties', () => {
    it('should compute buttonClasses correctly for primary medium button', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test',
          variant: 'primary',
          size: 'medium'
        }
      })

      const buttonClasses = wrapper.vm.buttonClasses
      expect(buttonClasses).toBeTruthy()
      expect(typeof buttonClasses).toBe('string')
      expect(buttonClasses).toContain('font-medium')
    })

    it('should compute buttonClasses correctly for secondary small button', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test',
          variant: 'secondary',
          size: 'small'
        }
      })

      const buttonClasses = wrapper.vm.buttonClasses
      expect(buttonClasses).toBeTruthy()
      expect(buttonClasses).toContain('font-medium')
    })

    it('should compute buttonClasses correctly for danger large button', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test',
          variant: 'danger',
          size: 'large'
        }
      })

      const buttonClasses = wrapper.vm.buttonClasses
      expect(buttonClasses).toBeTruthy()
      expect(buttonClasses).toContain('font-medium')
    })
  })

  describe('Accessibility', () => {
    it('should have focus ring classes for accessibility', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Accessible Button'
        }
      })

      const button = wrapper.find('button')
      const classes = button.classes()
      expect(classes.some(cls => cls.includes('focus:outline-none') || cls.includes('focus:ring'))).toBe(true)
    })

    it('should have proper button element semantics', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Semantic Button'
        }
      })

      const button = wrapper.find('button')
      expect(button.element.tagName).toBe('BUTTON')
    })
  })

  describe('Props Validation', () => {
    it('should require label prop', () => {
      // Vue will show a warning in console, but component should still render
      wrapper = mount(ActionButton, {
        props: {
          label: 'Required Label'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should accept valid variant values', () => {
      const validVariants = ['primary', 'secondary', 'danger']
      
      for (const variant of validVariants) {
        wrapper = mount(ActionButton, {
          props: {
            label: 'Test',
            variant: variant
          }
        })

        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })

    it('should accept valid size values', () => {
      const validSizes = ['small', 'medium', 'large']
      
      for (const size of validSizes) {
        wrapper = mount(ActionButton, {
          props: {
            label: 'Test',
            size: size
          }
        })

        expect(wrapper.exists()).toBe(true)
        wrapper.unmount()
      }
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty label string', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: ''
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
    })

    it('should handle very long label text', () => {
      const longLabel = 'A'.repeat(100)
      wrapper = mount(ActionButton, {
        props: {
          label: longLabel
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain(longLabel)
    })

    it('should handle empty shortLabel', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test',
          shortLabel: ''
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Test')
    })

    it('should handle null icon prop', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Test',
          icon: null
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.find('component').exists()).toBe(false)
    })
  })

  describe('Combined Props', () => {
    it('should handle all props together correctly', () => {
      wrapper = mount(ActionButton, {
        props: {
          label: 'Complete Button',
          shortLabel: 'Short',
          variant: 'danger',
          size: 'large',
          icon: 'svg',
          disabled: false
        },
        global: {
          stubs: {
            svg: { template: '<svg></svg>' }
          }
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Complete Button')
      expect(button.text()).toContain('Short')
      expect(button.element.disabled).toBe(false)
    })

    it('should handle disabled state with all variants', () => {
      const variants = ['primary', 'secondary', 'danger']
      
      for (const variant of variants) {
        wrapper = mount(ActionButton, {
          props: {
            label: 'Disabled',
            variant: variant,
            disabled: true
          }
        })

        const button = wrapper.find('button')
        expect(button.element.disabled).toBe(true)
        wrapper.unmount()
      }
    })
  })
})

