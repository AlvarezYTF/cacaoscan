/**
 * Unit tests for BaseFincaFilters component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseFincaFilters from '../BaseFincaFilters.vue'

vi.mock('@/utils/idGenerator', () => ({
  generateSecureId: vi.fn(() => 'test-id-123')
}))

describe('BaseFincaFilters', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('Props validation', () => {
    it('should accept searchQuery prop', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          searchQuery: 'test'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept filters prop', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          filters: { type: 'test' }
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render header when showHeader is true', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showHeader: true
        }
      })

      expect(wrapper.find('.bg-gray-50').exists()).toBe(true)
    })

    it('should render search input when showSearch is true', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showSearch: true
        }
      })

      expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    })

    it('should render clear button when showClearButton is true', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showClearButton: true
        }
      })

      expect(wrapper.text()).toContain('Limpiar Filtros')
    })

    it('should use custom title when provided', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          title: 'Custom Title'
        }
      })

      expect(wrapper.text()).toContain('Custom Title')
    })
  })

  describe('Events', () => {
    it('should emit update:searchQuery when search input changes', async () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showSearch: true
        }
      })

      const input = wrapper.find('input')
      await input.setValue('test query')
      vi.advanceTimersByTime(500)

      expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
    })

    it('should emit apply-filters when search input changes', async () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showSearch: true
        }
      })

      const input = wrapper.find('input')
      await input.setValue('test query')
      vi.advanceTimersByTime(500)

      expect(wrapper.emitted('apply-filters')).toBeTruthy()
    })

    it('should emit clear-filters when clear button is clicked', async () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          showClearButton: true
        }
      })

      const clearButton = wrapper.find('button')
      await clearButton.trigger('click')

      expect(wrapper.emitted('clear-filters')).toBeTruthy()
    })

    it('should emit update:filters when filter is updated', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          filters: {}
        }
      })

      wrapper.vm.updateFilter('type', 'test')

      expect(wrapper.emitted('update:filters')).toBeTruthy()
    })
  })

  describe('Methods', () => {
    it('should update filter correctly', () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          filters: {}
        }
      })

      wrapper.vm.updateFilter('type', 'test')

      expect(wrapper.emitted('update:filters')[0][0]).toEqual({ type: 'test' })
    })

    it('should clear filters correctly', async () => {
      wrapper = mount(BaseFincaFilters, {
        props: {
          searchQuery: 'test',
          filters: { type: 'test' }
        }
      })

      wrapper.vm.handleClearFilters()

      expect(wrapper.emitted('update:searchQuery')[0][0]).toBe('')
      expect(wrapper.emitted('update:filters')[0][0]).toEqual({})
    })
  })

  describe('Slots', () => {
    it('should render filters slot when provided', () => {
      wrapper = mount(BaseFincaFilters, {
        slots: {
          filters: '<input type="text" />'
        }
      })

      expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    })

    it('should render header slot when provided', () => {
      wrapper = mount(BaseFincaFilters, {
        slots: {
          header: '<div>Custom Header</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Header')
    })
  })
})

