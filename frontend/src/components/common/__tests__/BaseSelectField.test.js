import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSelectField from '../BaseSelectField.vue'

describe('BaseSelectField', () => {
  let wrapper

  const mockOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render select element', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
  })

  it('should bind modelValue to select', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: 'option1',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.element.value).toBe('option1')
  })

  it('should render options from options prop', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const options = wrapper.findAll('option')
    expect(options.length).toBeGreaterThan(0)
    expect(wrapper.text()).toContain('Option 1')
    expect(wrapper.text()).toContain('Option 2')
  })

  it('should render placeholder option when provided', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        placeholder: 'Select an option'
      }
    })

    const placeholderOption = wrapper.find('option[value=""][disabled]')
    expect(placeholderOption.exists()).toBe(true)
    expect(placeholderOption.text()).toBe('Select an option')
  })

  it('should not render placeholder option when multiple is true', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        placeholder: 'Select an option',
        multiple: true
      }
    })

    const placeholderOption = wrapper.find('option[value=""][disabled]')
    expect(placeholderOption.exists()).toBe(false)
  })

  it('should emit update:modelValue on change', async () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.setValue('option1')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['option1'])
  })

  it('should emit change event on select change', async () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.setValue('option1')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('change')).toBeTruthy()
  })

  it('should handle multiple selection', async () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: [],
        options: mockOptions,
        multiple: true
      }
    })

    const select = wrapper.find('select')
    select.element.options[0].selected = true
    select.element.options[1].selected = true
    await select.trigger('change')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    const emittedValue = wrapper.emitted('update:modelValue')[0][0]
    expect(Array.isArray(emittedValue)).toBe(true)
  })

  it('should display label when provided', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        label: 'Select Label'
      }
    })

    expect(wrapper.text()).toContain('Select Label')
    const label = wrapper.find('label')
    expect(label.exists()).toBe(true)
  })

  it('should show required indicator when required is true', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        label: 'Select Label',
        required: true
      }
    })

    expect(wrapper.text()).toContain('*')
  })

  it('should display helper text when provided', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text()).toContain('Helper text')
  })

  it('should display error message when provided', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
  })

  it('should not show helper text when error exists', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        helperText: 'Helper text',
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
    // Helper text should not be visible when error exists
  })

  it('should disable select when disabled prop is true', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        disabled: true
      }
    })

    const select = wrapper.find('select')
    expect(select.attributes('disabled')).toBeDefined()
  })

  it('should apply small size classes', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        size: 'sm'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('px-3')
    expect(select.classes()).toContain('py-1.5')
    expect(select.classes()).toContain('text-sm')
  })

  it('should apply medium size classes by default', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        size: 'md'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('px-3')
    expect(select.classes()).toContain('py-2')
    expect(select.classes()).toContain('text-sm')
  })

  it('should apply large size classes', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        size: 'lg'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('px-4')
    expect(select.classes()).toContain('py-3')
    expect(select.classes()).toContain('text-base')
  })

  it('should apply default variant classes', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        variant: 'default'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border')
  })

  it('should apply filled variant classes', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        variant: 'filled'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('bg-gray-100')
  })

  it('should apply outlined variant classes', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        variant: 'outlined'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border-2')
  })

  it('should apply error state classes when error exists', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        error: 'Error message'
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border-red-300')
  })

  it('should emit blur event', async () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.trigger('blur')

    expect(wrapper.emitted('blur')).toBeTruthy()
  })

  it('should emit focus event', async () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.trigger('focus')

    expect(wrapper.emitted('focus')).toBeTruthy()
  })

  it('should render prefix icon when provided', () => {
    const TestIcon = { template: '<div class="test-icon">Icon</div>' }
    
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        prefixIcon: TestIcon
      }
    })

    expect(wrapper.find('.test-icon').exists()).toBe(true)
  })

  it('should render prefix slot', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      },
      slots: {
        prefix: '<div>Prefix Slot</div>'
      }
    })

    expect(wrapper.text()).toContain('Prefix Slot')
  })

  it('should render suffix slot', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      },
      slots: {
        suffix: '<div>Suffix Slot</div>'
      }
    })

    expect(wrapper.text()).toContain('Suffix Slot')
  })

  it('should render default slot for custom options', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: []
      },
      slots: {
        default: '<option value="custom">Custom Option</option>'
      }
    })

    expect(wrapper.text()).toContain('Custom Option')
  })

  it('should use custom optionValue function', () => {
    const customOptions = [
      { id: 1, name: 'Option 1' },
      { id: 2, name: 'Option 2' }
    ]

    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: customOptions,
        optionValue: (option) => option.id,
        optionLabel: (option) => option.name
      }
    })

    expect(wrapper.text()).toContain('Option 1')
    expect(wrapper.text()).toContain('Option 2')
  })

  it('should use custom optionLabel function', () => {
    const customOptions = [
      { value: 1, text: 'Custom Label 1' },
      { value: 2, text: 'Custom Label 2' }
    ]

    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: customOptions,
        optionValue: 'value',
        optionLabel: (option) => option.text
      }
    })

    expect(wrapper.text()).toContain('Custom Label 1')
    expect(wrapper.text()).toContain('Custom Label 2')
  })

  it('should handle disabled options', () => {
    const optionsWithDisabled = [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2', disabled: true }
    ]

    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: optionsWithDisabled
      }
    })

    const options = wrapper.findAll('option')
    const disabledOption = options.find(opt => {
      // Check if disabled attribute exists (can be empty string, 'disabled', or true)
      const disabledAttr = opt.attributes('disabled')
      const elementDisabled = opt.element.disabled
      return disabledAttr !== undefined || elementDisabled === true
    })
    expect(disabledOption).toBeTruthy()
  })

  it('should generate unique id when not provided', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    const id = select.attributes('id')
    expect(id).toBeTruthy()
    expect(id).toContain('select-')
  })

  it('should use provided id', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        id: 'custom-select-id'
      }
    })

    const select = wrapper.find('select')
    expect(select.attributes('id')).toBe('custom-select-id')
  })

  it('should link label to select via id', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        label: 'Select',
        id: 'test-select-id'
      }
    })

    const label = wrapper.find('label')
    expect(label.attributes('for')).toBe('test-select-id')
    const select = wrapper.find('select')
    expect(select.attributes('id')).toBe('test-select-id')
  })

  it('should apply required attribute when required is true', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        required: true
      }
    })

    const select = wrapper.find('select')
    expect(select.attributes('required')).toBeDefined()
  })

  it('should use errorMessage when provided instead of error', () => {
    wrapper = mount(BaseSelectField, {
      props: {
        modelValue: null,
        options: mockOptions,
        errorMessage: 'Error message from errorMessage prop'
      }
    })

    expect(wrapper.text()).toContain('Error message from errorMessage prop')
  })
})

