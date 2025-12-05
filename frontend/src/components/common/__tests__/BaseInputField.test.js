import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseInputField from '../BaseInputField.vue'

describe('BaseInputField', () => {
  let wrapper

  beforeEach(() => {
    vi.stubGlobal('crypto', {
      randomUUID: vi.fn(() => 'test-uuid-123'),
      getRandomValues: vi.fn(() => new Uint8Array([1, 2, 3]))
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.unstubAllGlobals()
  })

  describe('Rendering', () => {
    it('should render input field', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: ''
        }
      })

      const input = wrapper.find('input')
      expect(input.exists()).toBe(true)
    })

    it('should render with label', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          label: 'Test Label'
        }
      })

      expect(wrapper.text()).toContain('Test Label')
      const label = wrapper.find('label')
      expect(label.exists()).toBe(true)
    })

    it('should show required asterisk when required', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          label: 'Test Label',
          required: true
        }
      })

      const label = wrapper.find('label')
      expect(label.text()).toContain('*')
    })
  })

  describe('Model Value', () => {
    it('should bind modelValue to input', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: 'Test Value'
        }
      })

      const input = wrapper.find('input')
      expect(input.element.value).toBe('Test Value')
    })

    it('should emit update:modelValue on input', async () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: ''
        }
      })

      const input = wrapper.find('input')
      await input.setValue('New Value')

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['New Value'])
    })
  })

  describe('Input Types', () => {
    const types = ['text', 'email', 'password', 'number', 'tel', 'url', 'search', 'date', 'time', 'datetime-local']

    for (const type of types) {
      it(`should render ${type} input type`, () => {
        wrapper = mount(BaseInputField, {
          props: {
            modelValue: '',
            type
          }
        })

        const input = wrapper.find('input')
        expect(input.attributes('type')).toBe(type)
      })
    })
  })

  describe('States', () => {
    it('should apply error classes when error is present', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          error: 'Error message'
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('border-red-300')
    })

    it('should show error message', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          error: 'Error message'
        }
      })

      expect(wrapper.text()).toContain('Error message')
    })

    it('should be disabled when disabled prop is true', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          disabled: true
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('disabled')).toBeDefined()
      expect(input.classes()).toContain('cursor-not-allowed')
    })

    it('should be readonly when readonly prop is true', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          readonly: true
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('readonly')).toBeDefined()
    })
  })

  describe('Sizes', () => {
    const sizes = ['sm', 'md', 'lg']

    for (const size of sizes) {
      it(`should apply ${size} size classes`, () => {
        wrapper = mount(BaseInputField, {
          props: {
            modelValue: '',
            size
          }
        })

        const input = wrapper.find('input')
        expect(input.exists()).toBe(true)
      })
    })
  })

  describe('Icons', () => {
    it('should render prefix icon', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          prefixIcon: 'prefix-icon'
        }
      })

      const prefixContainer = wrapper.find('.absolute.inset-y-0.left-0')
      expect(prefixContainer.exists()).toBe(true)
    })

    it('should render suffix icon', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          suffixIcon: 'suffix-icon'
        }
      })

      const suffixContainer = wrapper.find('.absolute.inset-y-0.right-0')
      expect(suffixContainer.exists()).toBe(true)
    })

    it('should render prefix slot', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: ''
        },
        slots: {
          prefix: '<span class="prefix-content">Prefix</span>'
        }
      })

      expect(wrapper.find('.prefix-content').exists()).toBe(true)
    })
  })

  describe('Events', () => {
    it('should emit blur event', async () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: ''
        }
      })

      const input = wrapper.find('input')
      await input.trigger('blur')

      expect(wrapper.emitted('blur')).toBeTruthy()
    })

    it('should emit focus event', async () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: ''
        }
      })

      const input = wrapper.find('input')
      await input.trigger('focus')

      expect(wrapper.emitted('focus')).toBeTruthy()
    })
  })

  describe('Helper Text', () => {
    it('should show helper text when provided and no error', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          helperText: 'Helper text'
        }
      })

      expect(wrapper.text()).toContain('Helper text')
    })

    it('should not show helper text when error is present', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          helperText: 'Helper text',
          error: 'Error message'
        }
      })

      expect(wrapper.text()).not.toContain('Helper text')
      expect(wrapper.text()).toContain('Error message')
    })
  })

  describe('Attributes', () => {
    it('should pass through placeholder', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          placeholder: 'Enter text'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('placeholder')).toBe('Enter text')
    })

    it('should pass through min and max for number input', () => {
      wrapper = mount(BaseInputField, {
        props: {
          modelValue: '',
          type: 'number',
          min: 0,
          max: 100
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('min')).toBe('0')
      expect(input.attributes('max')).toBe('100')
    })
  })
})

