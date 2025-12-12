import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseProgressIndicator from '../BaseProgressIndicator.vue'

describe('BaseProgressIndicator', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should render progress bar with correct value', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 75
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.attributes('value')).toBe('75')
  })

  it('should use default max value of 100', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('max')).toBe('100')
  })

  it('should use custom max value', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        max: 200
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('max')).toBe('200')
  })

  it('should use default min value of 0', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('min')).toBe('0')
  })

  it('should use custom min value', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        min: 10
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('min')).toBe('10')
  })

  it('should display label when provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        label: 'Progress Label'
      }
    })

    expect(wrapper.text()).toContain('Progress Label')
  })

  it('should not display label when not provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50
      }
    })

    const label = wrapper.find('label')
    expect(label.exists()).toBe(false)
  })

  it('should display helper text when provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        helperText: 'Helper text'
      }
    })

    expect(wrapper.text()).toContain('Helper text')
  })

  it('should display error message when provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error message')
  })

  it('should display formatted value when showValue is true', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 75,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('75%')
  })

  it('should format value as percentage by default', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        showValue: true,
        format: 'percentage'
      }
    })

    expect(wrapper.text()).toContain('50%')
  })

  it('should format value as fraction', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        showValue: true,
        format: 'fraction',
        max: 100
      }
    })

    expect(wrapper.text()).toContain('50 / 100')
  })

  it('should format value as number', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        showValue: true,
        format: 'number'
      }
    })

    expect(wrapper.text()).toContain('50')
  })

  it('should apply default variant class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        variant: 'default'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('progress-bar')
  })

  it('should apply success variant class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        variant: 'success'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('bg-green-600')
  })

  it('should apply warning variant class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        variant: 'warning'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('bg-yellow-600')
  })

  it('should apply danger variant class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        variant: 'danger'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('bg-red-600')
  })

  it('should apply info variant class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        variant: 'info'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('bg-blue-500')
  })

  it('should apply small size class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        size: 'sm'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('h-1')
  })

  it('should apply medium size class by default', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        size: 'md'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('h-2')
  })

  it('should apply large size class', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        size: 'lg'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.classes()).toContain('h-3')
  })

  it('should show animated shimmer when animated is true', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        animated: true
      }
    })

    const shimmer = wrapper.find('.animate-shimmer')
    expect(shimmer.exists()).toBe(true)
  })

  it('should not show animated shimmer when animated is false', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        animated: false
      }
    })

    const shimmer = wrapper.find('.animate-shimmer')
    expect(shimmer.exists()).toBe(false)
  })

  it('should calculate percentage correctly with custom min and max', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 60,
        min: 20,
        max: 100,
        showValue: true
      }
    })

    // Value 60 in range 20-100 = (60-20)/(100-20) * 100 = 50%
    expect(wrapper.text()).toContain('50%')
  })

  it('should clamp value to min when below minimum', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: -10,
        min: 0,
        max: 100,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('0%')
  })

  it('should clamp value to max when above maximum', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 150,
        min: 0,
        max: 100,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('100%')
  })

  it('should use aria-label when provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        ariaLabel: 'Custom aria label'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('aria-label')).toBe('Custom aria label')
  })

  it('should use label as aria-label when ariaLabel not provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        label: 'Progress Label'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('aria-label')).toBe('Progress Label')
  })

  it('should generate unique id when not provided', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50
      }
    })

    const progressBar = wrapper.find('progress')
    const id = progressBar.attributes('id')
    expect(id).toBeTruthy()
    expect(id).toContain('progress-')
  })

  it('should use provided id', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        id: 'custom-progress-id'
      }
    })

    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('id')).toBe('custom-progress-id')
  })

  it('should apply container class for small size', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        size: 'sm'
      }
    })

    const container = wrapper.find('.w-full')
    expect(container.classes()).toContain('text-sm')
  })

  it('should handle zero value correctly', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 0,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('0%')
    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('value')).toBe('0')
  })

  it('should handle max value correctly', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 100,
        max: 100,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('100%')
    const progressBar = wrapper.find('progress')
    expect(progressBar.attributes('value')).toBe('100')
  })

  it('should handle zero range (min equals max)', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 50,
        min: 100,
        max: 100,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('0%')
  })

  it('should round percentage correctly', () => {
    wrapper = mount(BaseProgressIndicator, {
      props: {
        value: 33.333,
        max: 100,
        showValue: true
      }
    })

    expect(wrapper.text()).toContain('33%')
  })
})

