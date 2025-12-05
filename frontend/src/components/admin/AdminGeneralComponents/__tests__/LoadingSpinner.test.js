import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoadingSpinner from '../LoadingSpinner.vue'

// Mock BaseSpinner component
vi.mock('@/components/common/BaseSpinner.vue', () => ({
  default: {
    name: 'BaseSpinner',
    template: '<div class="base-spinner" :class="containerClass"></div>',
    props: ['size', 'color', 'strokeWidth', 'containerClass']
  }
}))

describe('LoadingSpinner', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(LoadingSpinner)

      expect(wrapper.exists()).toBe(true)
    })

    it('should render BaseSpinner component', () => {
      wrapper = mount(LoadingSpinner)

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.exists()).toBe(true)
    })
  })

  describe('Props', () => {
    it('should pass default props to BaseSpinner', () => {
      wrapper = mount(LoadingSpinner)

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.props('size')).toBe('md')
      expect(baseSpinner.props('color')).toBe('white')
      expect(baseSpinner.props('strokeWidth')).toBe('4')
      expect(baseSpinner.props('containerClass')).toBe('')
    })

    it('should pass size prop to BaseSpinner', () => {
      wrapper = mount(LoadingSpinner, {
        props: {
          size: 'lg'
        }
      })

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.props('size')).toBe('lg')
    })

    it('should pass color prop to BaseSpinner', () => {
      wrapper = mount(LoadingSpinner, {
        props: {
          color: 'blue'
        }
      })

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.props('color')).toBe('blue')
    })

    it('should pass strokeWidth prop to BaseSpinner', () => {
      wrapper = mount(LoadingSpinner, {
        props: {
          strokeWidth: '2'
        }
      })

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.props('strokeWidth')).toBe('2')
    })

    it('should pass className prop as containerClass to BaseSpinner', () => {
      wrapper = mount(LoadingSpinner, {
        props: {
          className: 'custom-class'
        }
      })

      const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
      expect(baseSpinner.props('containerClass')).toBe('custom-class')
    })
  })

  describe('Props Validation', () => {
    it('should accept valid size values', () => {
      const validSizes = ['xs', 'sm', 'md', 'lg', 'xl']
      
      for (const size of validSizes) {
        wrapper = mount(LoadingSpinner, {
          props: { size }
        })

        expect(wrapper.exists()).toBe(true)
        const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
        expect(baseSpinner.props('size')).toBe(size)
        wrapper.unmount()
      }
    })

    it('should accept valid color values', () => {
      const validColors = ['white', 'gray', 'blue', 'green', 'red', 'yellow', 'purple']
      
      for (const color of validColors) {
        wrapper = mount(LoadingSpinner, {
          props: { color }
        })

        expect(wrapper.exists()).toBe(true)
        const baseSpinner = wrapper.findComponent({ name: 'BaseSpinner' })
        expect(baseSpinner.props('color')).toBe(color)
        wrapper.unmount()
      }
    })
  })
})

