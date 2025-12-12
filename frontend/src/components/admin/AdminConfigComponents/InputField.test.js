import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import InputField from './InputField.vue'

// Mock crypto for testing
vi.stubGlobal('crypto', {
  getRandomValues: vi.fn().mockReturnValue(new Uint32Array([123456]))
})

describe('InputField', () => {
  it('should render input field', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: ''
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('should display label when provided', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        label: 'Test Label'
      }
    })

    expect(wrapper.text().includes('Test Label')).toBe(true)
  })

  it('should show required asterisk when required', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        label: 'Test Label',
        required: true
      }
    })

    expect(wrapper.text().includes('*')).toBe(true)
  })

  it('should emit update:modelValue on input', async () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.setValue('test value')
    await input.trigger('input')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['test value'])
  })

  it('should emit blur event', async () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.trigger('blur')

    expect(wrapper.emitted('blur')).toBeTruthy()
  })

  it('should display error message', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        error: 'This field is required'
      }
    })

    expect(wrapper.text().includes('This field is required')).toBe(true)
  })

  it('should display helper text when no error', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text().includes('Helper text')).toBe(true)
  })

  it('should not display helper text when error exists', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        error: 'Error message',
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text().includes('Helper text')).toBe(false)
    expect(wrapper.text().includes('Error message')).toBe(true)
  })

  it('should apply error styling when error exists', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        error: 'Error message'
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-red-500')
  })

  it('should be disabled when disabled prop is true', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        disabled: true
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('should have correct input type', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        type: 'email'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('type')).toBe('email')
  })

  it('should have placeholder', () => {
    const wrapper = mount(InputField, {
      props: {
        modelValue: '',
        placeholder: 'Enter text'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Enter text')
  })

  it('should generate unique ID', () => {
    const wrapper1 = mount(InputField, {
      props: {
        modelValue: ''
      }
    })

    const wrapper2 = mount(InputField, {
      props: {
        modelValue: ''
      }
    })

    const id1 = wrapper1.find('input').attributes('id')
    const id2 = wrapper2.find('input').attributes('id')

    expect(id1).toBeTruthy()
    expect(id2).toBeTruthy()
  })
})

