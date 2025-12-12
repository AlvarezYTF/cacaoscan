/**
 * Unit tests for BaseFincaList component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseFincaList from '../BaseFincaList.vue'

vi.mock('../BaseFincaCard.vue', () => ({
  default: {
    name: 'BaseFincaCard',
    template: '<div class="finca-card">{{ finca.nombre }}</div>',
    props: {
      finca: Object,
      selected: Boolean,
      showDescription: Boolean,
      showActions: Boolean,
      actions: Array
    },
    emits: ['click', 'action-click']
  }
}))

vi.mock('../BaseLoadingSkeleton.vue', () => ({
  default: {
    name: 'BaseLoadingSkeleton',
    template: '<div class="skeleton">Loading...</div>',
    props: {
      type: String,
      variant: String
    }
  }
}))

describe('BaseFincaList', () => {
  let wrapper

  const createFincas = () => [
    { id: 1, nombre: 'Finca 1' },
    { id: 2, nombre: 'Finca 2' },
    { id: 3, nombre: 'Finca 3' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should accept fincas prop', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas()
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should default fincas to empty array', () => {
      wrapper = mount(BaseFincaList)
      expect(wrapper.props('fincas')).toEqual([])
    })
  })

  describe('Rendering', () => {
    it('should render fincas', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas()
        }
      })

      expect(wrapper.text()).toContain('Finca 1')
      expect(wrapper.text()).toContain('Finca 2')
    })

    it('should show loading state when loading is true', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          loading: true
        }
      })

      expect(wrapper.findComponent({ name: 'BaseLoadingSkeleton' }).exists()).toBe(true)
    })

    it('should show empty state when no fincas', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: []
        }
      })

      expect(wrapper.text()).toContain('No hay fincas disponibles')
    })

    it('should render title when provided', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas(),
          title: 'Test Title'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should apply correct grid class for columns', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas(),
          columns: 2
        }
      })

      const grid = wrapper.find('.grid')
      expect(grid.classes()).toContain('grid-cols-1')
    })
  })

  describe('Events', () => {
    it('should emit finca-click event', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas()
        }
      })

      wrapper.vm.handleFincaClick({ id: 1 })

      expect(wrapper.emitted('finca-click')).toBeTruthy()
    })

    it('should emit action-click event', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: createFincas()
        }
      })

      wrapper.vm.handleActionClick({ action: 'edit', finca: { id: 1 } })

      expect(wrapper.emitted('action-click')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render header slot when provided', () => {
      wrapper = mount(BaseFincaList, {
        slots: {
          header: '<div>Custom Header</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Header')
    })

    it('should render empty slot when provided', () => {
      wrapper = mount(BaseFincaList, {
        props: {
          fincas: []
        },
        slots: {
          empty: '<div>Custom Empty</div>'
        }
      })

      expect(wrapper.text()).toContain('Custom Empty')
    })
  })
})

