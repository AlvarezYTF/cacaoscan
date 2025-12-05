import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseSpinner from './BaseSpinner.vue'

describe('BaseSpinner', () => {
  it('should render spinner', () => {
    const wrapper = mount(BaseSpinner)

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('should apply correct size class', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        size: 'lg'
      }
    })

    expect(wrapper.vm.spinnerClasses).toContain('h-6 w-6')
  })

  it('should apply correct color class', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        color: 'blue'
      }
    })

    expect(wrapper.vm.spinnerClasses).toContain('text-blue-600')
  })

  it('should display text when provided', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        text: 'Loading...'
      }
    })

    expect(wrapper.text().includes('Loading...')).toBe(true)
  })

  it('should not display text when not provided', () => {
    const wrapper = mount(BaseSpinner)

    const textElement = wrapper.find('p')
    expect(textElement.exists()).toBe(false)
  })

  it('should render fullscreen when fullScreen is true', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        fullScreen: true
      }
    })

    expect(wrapper.find('.base-spinner-fullscreen').exists()).toBe(true)
  })

  it('should not render fullscreen when fullScreen is false', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        fullScreen: false
      }
    })

    expect(wrapper.find('.base-spinner-fullscreen').exists()).toBe(false)
  })

  it('should apply custom container class', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        containerClass: 'custom-class'
      }
    })

    expect(wrapper.classes()).toContain('custom-class')
  })

  it('should use correct stroke width', () => {
    const wrapper = mount(BaseSpinner, {
      props: {
        strokeWidth: '2'
      }
    })

    const circle = wrapper.find('circle')
    expect(circle.attributes('stroke-width')).toBe('2')
  })

  it('should use default stroke width when not provided', () => {
    const wrapper = mount(BaseSpinner)

    const circle = wrapper.find('circle')
    expect(circle.attributes('stroke-width')).toBe('4')
  })

  it('should apply all size classes correctly', () => {
    const sizes = ['xs', 'sm', 'md', 'lg', 'xl']
    
    for (const size of sizes) {
      const wrapper = mount(BaseSpinner, {
        props: { size }
      })
      
      const sizeClasses = {
        xs: 'h-3 w-3',
        sm: 'h-4 w-4',
        md: 'h-5 w-5',
        lg: 'h-6 w-6',
        xl: 'h-8 w-8'
      }
      
      expect(wrapper.vm.spinnerClasses).toContain(sizeClasses[size])
    }
  })

  it('should apply all color classes correctly', () => {
    const colors = ['white', 'gray', 'blue', 'green', 'red', 'yellow', 'purple']
    
    for (const color of colors) {
      const wrapper = mount(BaseSpinner, {
        props: { color }
      })
      
      const colorClasses = {
        white: 'text-white',
        gray: 'text-gray-600',
        blue: 'text-blue-600',
        green: 'text-green-600',
        red: 'text-red-600',
        yellow: 'text-yellow-600',
        purple: 'text-purple-600'
      }
      
      expect(wrapper.vm.spinnerClasses).toContain(colorClasses[color])
    })
  })
})

