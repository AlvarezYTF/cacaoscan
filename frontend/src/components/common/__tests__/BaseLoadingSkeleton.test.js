import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLoadingSkeleton from '../BaseLoadingSkeleton.vue'

describe('BaseLoadingSkeleton', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  describe('Text Type', () => {
    it('should render text skeleton with default lines', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'text'
        }
      })

      const lines = wrapper.findAll('.space-y-2 .h-4.bg-gray-200.rounded')
      expect(lines.length).toBe(3)
    })

    it('should render text skeleton with custom number of lines', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'text',
          lines: 5
        }
      })

      const lines = wrapper.findAll('.space-y-2 .h-4.bg-gray-200.rounded')
      expect(lines.length).toBe(5)
    })
  })

  describe('Card Type', () => {
    it('should render card skeleton', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'card'
        }
      })

      const card = wrapper.find('.bg-white.rounded-lg')
      expect(card.exists()).toBe(true)
      expect(card.find('.w-12.h-12.bg-gray-200.rounded-full').exists()).toBe(true)
    })
  })

  describe('Table Type', () => {
    it('should render table skeleton with default columns and rows', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'table'
        }
      })

      const table = wrapper.find('.bg-white.rounded-lg')
      expect(table.exists()).toBe(true)
    })

    it('should render table skeleton with custom columns and rows', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'table',
          columns: 3,
          rows: 4
        }
      })

      const table = wrapper.find('.bg-white.rounded-lg')
      expect(table.exists()).toBe(true)
    })
  })

  describe('Image Type', () => {
    it('should render image skeleton', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'image'
        }
      })

      const image = wrapper.find('.bg-gray-200.rounded')
      expect(image.exists()).toBe(true)
    })
  })

  describe('Custom Type', () => {
    it('should render custom slot content', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'custom'
        },
        slots: {
          default: '<div class="custom-skeleton">Custom content</div>'
        }
      })

      expect(wrapper.find('.custom-skeleton').exists()).toBe(true)
      expect(wrapper.text()).toContain('Custom content')
    })
  })

  describe('Variants', () => {
    it('should apply compact variant classes', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'text',
          variant: 'compact'
        }
      })

      const container = wrapper.find('.animate-pulse')
      expect(container.classes()).toContain('p-2')
    })

    it('should apply spacious variant classes', () => {
      wrapper = mount(BaseLoadingSkeleton, {
        props: {
          type: 'text',
          variant: 'spacious'
        }
      })

      const container = wrapper.find('.animate-pulse')
      expect(container.classes()).toContain('p-6')
    })
  })
})

