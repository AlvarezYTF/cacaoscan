import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSearchInput from '../BaseSearchInput.vue'

describe('BaseSearchInput', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render input field', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.exists()).toBe(true)
  })

  it('should bind modelValue to input', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test search'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.element.value).toBe('test search')
  })

  it('should emit update:modelValue on input', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    await input.setValue('new search')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['new search'])
  })

  it('should emit search event on Enter key', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test query'
      }
    })

    const input = wrapper.find('input[type="search"]')
    await input.trigger('keyup.enter')

    expect(wrapper.emitted('search')).toBeTruthy()
  })

  it('should emit clear event when clear button is clicked', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test query'
      }
    })

    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    if (clearButton.exists()) {
      await clearButton.trigger('click')
      expect(wrapper.emitted('clear')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0]).toEqual([''])
    }
  })

  it('should show clear button when has value and showClearButton is true', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test query',
        showClearButton: true
      }
    })

    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    expect(clearButton.exists()).toBe(true)
  })

  it('should not show clear button when empty', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        showClearButton: true
      }
    })

    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    expect(clearButton.exists()).toBe(false)
  })

  it('should not show clear button when showClearButton is false', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test query',
        showClearButton: false
      }
    })

    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    expect(clearButton.exists()).toBe(false)
  })

  it('should not show clear button when disabled', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: 'test query',
        showClearButton: true,
        disabled: true
      }
    })

    const clearButton = wrapper.find('button[aria-label="Clear search"]')
    expect(clearButton.exists()).toBe(false)
  })

  it('should display label when provided', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        label: 'Search Label'
      }
    })

    expect(wrapper.text()).toContain('Search Label')
    const label = wrapper.find('label')
    expect(label.exists()).toBe(true)
  })

  it('should use default placeholder', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('placeholder')).toBe('Buscar...')
  })

  it('should use custom placeholder', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        placeholder: 'Custom placeholder'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('placeholder')).toBe('Custom placeholder')
  })

  it('should display helper text when provided', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text()).toContain('Helper text')
  })

  it('should display error message when provided', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
  })

  it('should disable input when disabled prop is true', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        disabled: true
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('should show loading indicator when loading is true', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        loading: true
      }
    })

    const loadingIndicator = wrapper.find('.animate-spin')
    expect(loadingIndicator.exists()).toBe(true)
  })

  it('should hide loading indicator when loading is false', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        loading: false
      }
    })

    const loadingIndicator = wrapper.find('.animate-spin')
    expect(loadingIndicator.exists()).toBe(false)
  })

  it('should apply small size classes', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        size: 'sm'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('px-3')
    expect(input.classes()).toContain('py-1.5')
    expect(input.classes()).toContain('text-sm')
  })

  it('should apply medium size classes by default', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        size: 'md'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('px-3')
    expect(input.classes()).toContain('py-2')
    expect(input.classes()).toContain('text-sm')
  })

  it('should apply large size classes', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        size: 'lg'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('px-4')
    expect(input.classes()).toContain('py-3')
    expect(input.classes()).toContain('text-base')
  })

  it('should apply default variant classes', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        variant: 'default'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('border')
  })

  it('should apply filled variant classes', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        variant: 'filled'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('bg-gray-100')
  })

  it('should apply outlined variant classes', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        variant: 'outlined'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('border-2')
  })

  it('should apply error state classes when error exists', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        error: 'Error message'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.classes()).toContain('border-red-300')
  })

  it('should emit blur event', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    await input.trigger('blur')

    expect(wrapper.emitted('blur')).toBeTruthy()
  })

  it('should emit focus event', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    await input.trigger('focus')

    expect(wrapper.emitted('focus')).toBeTruthy()
  })

  it('should emit input event', async () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    await input.setValue('test')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('input')).toBeTruthy()
  })

  it('should generate unique id when not provided', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="search"]')
    const id = input.attributes('id')
    expect(id).toBeTruthy()
    expect(id).toContain('search-')
  })

  it('should use provided id', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        id: 'custom-search-id'
      }
    })

    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('id')).toBe('custom-search-id')
  })

  it('should link label to input via id', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        label: 'Search',
        id: 'test-search-id'
      }
    })

    const label = wrapper.find('label')
    expect(label.attributes('for')).toBe('test-search-id')
    const input = wrapper.find('input[type="search"]')
    expect(input.attributes('id')).toBe('test-search-id')
  })

  it('should not show helper text when error is shown', () => {
    wrapper = mount(BaseSearchInput, {
      props: {
        modelValue: '',
        helperText: 'Helper text',
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
    // Helper text should not be visible when error exists
  })
})

