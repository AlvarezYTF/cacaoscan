import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FormField from '../FormField.vue'

describe('FormField', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label'
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render label', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label'
        }
      })

      expect(wrapper.text()).toContain('Test Label')
    })

    it('should render required asterisk when required is true', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          required: true
        }
      })

      const asterisk = wrapper.find('.text-red-500')
      expect(asterisk.exists()).toBe(true)
      expect(asterisk.text()).toBe('*')
    })

    it('should not render required asterisk when required is false', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          required: false
        }
      })

      const asterisk = wrapper.find('.text-red-500')
      expect(asterisk.exists()).toBe(false)
    })
  })

  describe('Input Field', () => {
    it('should render input element for text type', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          type: 'text'
        }
      })

      const input = wrapper.find('input[type="text"]')
      expect(input.exists()).toBe(true)
    })

    it('should bind modelValue to input', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          modelValue: 'test value'
        }
      })

      const input = wrapper.find('input')
      expect(input.element.value).toBe('test value')
    })

    it('should emit update:modelValue on input', async () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          modelValue: ''
        }
      })

      const input = wrapper.find('input')
      await input.setValue('new value')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['new value'])
    })

    it('should set input attributes correctly', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          name: 'test-name',
          label: 'Test Label',
          placeholder: 'Enter value',
          required: true,
          disabled: true,
          autocomplete: 'off',
          min: '0',
          max: '100'
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('id')).toBe('test-field')
      expect(input.attributes('name')).toBe('test-name')
      expect(input.attributes('placeholder')).toBe('Enter value')
      expect(input.attributes('required')).toBeDefined()
      expect(input.attributes('disabled')).toBeDefined()
      expect(input.attributes('autocomplete')).toBe('off')
      expect(input.attributes('min')).toBe('0')
      expect(input.attributes('max')).toBe('100')
    })

    it('should support different input types', () => {
      const types = ['text', 'email', 'password', 'number', 'date', 'time']
      
      for (const type of types) {
        wrapper = mount(FormField, {
          props: {
            id: `test-${type}`,
            label: 'Test Label',
            type: type
          }
        })

        const input = wrapper.find(`input[type="${type}"]`)
        expect(input.exists()).toBe(true)
        wrapper.unmount()
      })
    })
  })

  describe('Select Field', () => {
    const mockOptions = [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' }
    ]

    it('should render select element when type is select', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: mockOptions
        }
      })

      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
      expect(wrapper.find('input').exists()).toBe(false)
    })

    it('should render options from options prop', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: mockOptions
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBe(3)
      expect(wrapper.text()).toContain('Option 1')
      expect(wrapper.text()).toContain('Option 2')
      expect(wrapper.text()).toContain('Option 3')
    })

    it('should show loading message when loading is true', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: [],
          loading: true
        }
      })

      expect(wrapper.text()).toContain('Cargando...')
    })

    it('should show empty message when no options', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: [],
          loading: false,
          emptyMessage: 'No options available'
        }
      })

      expect(wrapper.text()).toContain('No options available')
    })

    it('should emit update:modelValue on select change', async () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: mockOptions,
          modelValue: ''
        }
      })

      const select = wrapper.find('select')
      await select.setValue('option2')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual(['option2'])
    })

    it('should handle string options', () => {
      const stringOptions = ['option1', 'option2', 'option3']
      
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: stringOptions
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBe(3)
    })

    it('should handle number options', () => {
      const numberOptions = [1, 2, 3]
      
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: numberOptions
        }
      })

      const options = wrapper.findAll('option')
      expect(options.length).toBe(3)
    })

    it('should use custom optionValue prop', () => {
      const customOptions = [
        { codigo: '001', nombre: 'Option 1' },
        { codigo: '002', nombre: 'Option 2' }
      ]
      
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: customOptions,
          optionValue: 'codigo',
          optionLabel: 'nombre'
        }
      })

      const options = wrapper.findAll('option')
      expect(options[0].attributes('value')).toBe('001')
      expect(options[1].attributes('value')).toBe('002')
    })

    it('should use custom optionLabel prop', () => {
      const customOptions = [
        { codigo: '001', nombre: 'Opción 1' },
        { codigo: '002', nombre: 'Opción 2' }
      ]
      
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: customOptions,
          optionValue: 'codigo',
          optionLabel: 'nombre'
        }
      })

      expect(wrapper.text()).toContain('Opción 1')
      expect(wrapper.text()).toContain('Opción 2')
    })
  })

  describe('Error and Hint Messages', () => {
    it('should display error message when error prop is provided', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          error: 'This field is required'
        }
      })

      expect(wrapper.text()).toContain('This field is required')
      const errorElement = wrapper.find('.text-red-600')
      expect(errorElement.exists()).toBe(true)
    })

    it('should display hint message when hint prop is provided and no error', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          hint: 'Enter a valid value'
        }
      })

      expect(wrapper.text()).toContain('Enter a valid value')
      const hintElement = wrapper.find('.text-gray-500')
      expect(hintElement.exists()).toBe(true)
    })

    it('should prioritize error over hint', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          error: 'Error message',
          hint: 'Hint message'
        }
      })

      expect(wrapper.text()).toContain('Error message')
      expect(wrapper.text()).not.toContain('Hint message')
    })

    it('should apply error styling when hasError is true', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          hasError: true
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('border-red-500')
    })

    it('should apply error styling when error prop is provided', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          error: 'Error message'
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('border-red-500')
    })
  })

  describe('Styling and Classes', () => {
    it('should apply containerClass prop', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          containerClass: 'custom-container'
        }
      })

      const container = wrapper.find('.custom-container')
      expect(container.exists()).toBe(true)
    })

    it('should apply inputClass prop', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          inputClass: 'custom-input'
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('custom-input')
    })

    it('should apply default input classes', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label'
        }
      })

      const input = wrapper.find('input')
      expect(input.classes()).toContain('w-full')
      expect(input.classes()).toContain('px-4')
      expect(input.classes()).toContain('py-2.5')
    })
  })

  describe('Slots', () => {
    it('should render options slot when provided', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select'
        },
        slots: {
          options: '<option value="slot-option">Slot Option</option>'
        }
      })

      expect(wrapper.text()).toContain('Slot Option')
    })

    it('should render suffix slot when provided', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label'
        },
        slots: {
          suffix: '<span class="suffix-content">Suffix</span>'
        }
      })

      const suffix = wrapper.find('.suffix-content')
      expect(suffix.exists()).toBe(true)
      expect(suffix.text()).toBe('Suffix')
    })
  })

  describe('Disabled State', () => {
    it('should disable input when disabled prop is true', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-field',
          label: 'Test Label',
          disabled: true
        }
      })

      const input = wrapper.find('input')
      expect(input.attributes('disabled')).toBeDefined()
      expect(input.classes()).toContain('disabled:bg-gray-100')
    })

    it('should disable select when disabled prop is true', () => {
      wrapper = mount(FormField, {
        props: {
          id: 'test-select',
          label: 'Test Label',
          type: 'select',
          options: [{ value: 'opt1', label: 'Option 1' }],
          disabled: true
        }
      })

      const select = wrapper.find('select')
      expect(select.attributes('disabled')).toBeDefined()
    })
  })
})



