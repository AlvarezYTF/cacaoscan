import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSearchBar from './BaseSearchBar.vue'

describe('BaseSearchBar', () => {
  it('should render search bar', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: ''
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('should emit update:modelValue on input', async () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.setValue('test search')
    await input.trigger('input')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['test search'])
  })

  it('should emit input event on input', async () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    await input.setValue('test search')
    await input.trigger('input')

    expect(wrapper.emitted('input')).toBeTruthy()
    expect(wrapper.emitted('input')[0]).toEqual(['test search'])
  })

  it('should emit clear event when clear button is clicked', async () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: 'test'
      }
    })

    await wrapper.vm.handleClear()

    expect(wrapper.emitted('clear')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual([''])
  })

  it('should show clear button when value is not empty', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: 'test'
      }
    })

    const clearButton = wrapper.find('button')
    expect(clearButton.exists()).toBe(true)
  })

  it('should not show clear button when value is empty', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: ''
      }
    })

    const clearButton = wrapper.find('button')
    expect(clearButton.exists()).toBe(false)
  })

  it('should have placeholder', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: '',
        placeholder: 'Search...'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Search...')
  })

  it('should use default placeholder when not provided', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBeTruthy()
  })

  it('should be disabled when disabled prop is true', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: '',
        disabled: true
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('should apply custom classes', () => {
    const wrapper = mount(BaseSearchBar, {
      props: {
        modelValue: '',
        inputClass: 'custom-input-class'
      }
    })

    const input = wrapper.find('input')
    expect(input.classes()).toContain('custom-input-class')
  })
})

