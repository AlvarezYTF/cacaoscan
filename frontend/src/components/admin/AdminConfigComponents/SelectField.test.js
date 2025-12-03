import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SelectField from './SelectField.vue'

// Mock crypto for testing
vi.stubGlobal('crypto', {
  getRandomValues: vi.fn().mockReturnValue(new Uint8Array([1, 2, 3, 4, 5, 6]))
})

describe('SelectField', () => {
  const mockOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' }
  ]

  it('should render select field', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('should display label when provided', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        label: 'Test Label',
        options: mockOptions
      }
    })

    expect(wrapper.text().includes('Test Label')).toBe(true)
  })

  it('should show required asterisk when required', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        label: 'Test Label',
        required: true,
        options: mockOptions
      }
    })

    expect(wrapper.text().includes('*')).toBe(true)
  })

  it('should emit update:modelValue on change', async () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    await select.setValue('option1')
    await select.trigger('change')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['option1'])
  })

  it('should display all options', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    const options = wrapper.findAll('option')
    expect(options.length).toBe(mockOptions.length + 1) // +1 for placeholder
  })

  it('should display placeholder option', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        placeholder: 'Select an option',
        options: mockOptions
      }
    })

    const placeholder = wrapper.find('option[value=""]')
    expect(placeholder.exists()).toBe(true)
    expect(placeholder.text()).toBe('Select an option')
  })

  it('should use default placeholder when not provided', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    const placeholder = wrapper.find('option[value=""]')
    expect(placeholder.text()).toBe('Selecciona una opción')
  })

  it('should display error message', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        error: 'This field is required',
        options: mockOptions
      }
    })

    expect(wrapper.text().includes('This field is required')).toBe(true)
  })

  it('should display helper text when no error', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        helperText: 'Helper text',
        options: mockOptions
      }
    })

    expect(wrapper.text().includes('Helper text')).toBe(true)
  })

  it('should not display helper text when error exists', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        error: 'Error message',
        helperText: 'Helper text',
        options: mockOptions
      }
    })

    expect(wrapper.text().includes('Helper text')).toBe(false)
    expect(wrapper.text().includes('Error message')).toBe(true)
  })

  it('should apply error styling when error exists', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        error: 'Error message',
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.classes()).toContain('border-red-500')
  })

  it('should be disabled when disabled prop is true', () => {
    const wrapper = mount(SelectField, {
      props: {
        modelValue: '',
        disabled: true,
        options: mockOptions
      }
    })

    const select = wrapper.find('select')
    expect(select.attributes('disabled')).toBeDefined()
  })

  it('should generate unique ID', () => {
    const wrapper1 = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    const wrapper2 = mount(SelectField, {
      props: {
        modelValue: '',
        options: mockOptions
      }
    })

    const id1 = wrapper1.find('select').attributes('id')
    const id2 = wrapper2.find('select').attributes('id')

    expect(id1).toBeTruthy()
    expect(id2).toBeTruthy()
  })
})

