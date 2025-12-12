/**
 * Unit tests for BaseFincaCard component
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseFincaCard from '../BaseFincaCard.vue'

describe('BaseFincaCard', () => {
  let wrapper

  const createFinca = () => ({
    id: 1,
    nombre: 'Finca Test',
    ubicacion: 'Test Location',
    area_total: 10.5,
    lotes: [
      { id: 1, nombre: 'Lote 1' },
      { id: 2, nombre: 'Lote 2' }
    ],
    descripcion: 'Test description'
  })

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Props validation', () => {
    it('should require finca prop', () => {
      expect(() => {
        wrapper = mount(BaseFincaCard)
      }).toThrow()
    })

    it('should accept finca prop', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render finca nombre', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      expect(wrapper.text()).toContain('Finca Test')
    })

    it('should render ubicacion when provided', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      expect(wrapper.text()).toContain('Test Location')
    })

    it('should render area total', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      expect(wrapper.text()).toContain('10.50 ha')
    })

    it('should render number of lotes', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      expect(wrapper.text()).toContain('2')
    })

    it('should render description when showDescription is true', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca,
          showDescription: true
        }
      })

      expect(wrapper.text()).toContain('Test description')
    })

    it('should not render description when showDescription is false', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca,
          showDescription: false
        }
      })

      expect(wrapper.text()).not.toContain('Test description')
    })

    it('should apply selected class when selected is true', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca,
          selected: true
        }
      })

      const card = wrapper.find('div')
      expect(card.classes()).toContain('border-green-500')
    })
  })

  describe('Events', () => {
    it('should emit click event when card is clicked', async () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      const card = wrapper.find('div')
      await card.trigger('click')

      expect(wrapper.emitted('click')).toBeTruthy()
      expect(wrapper.emitted('click')[0][0]).toEqual(finca)
    })

    it('should emit action-click event when action is clicked', async () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca,
          showActions: true,
          actions: [
            { key: 'edit', label: 'Edit' }
          ]
        }
      })

      const actionButton = wrapper.find('button')
      await actionButton.trigger('click')

      expect(wrapper.emitted('action-click')).toBeTruthy()
    })
  })

  describe('Methods', () => {
    it('should format area correctly', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      const formatted = wrapper.vm.formatArea(10.5)
      expect(formatted).toBe('10.50 ha')
    })

    it('should return 0 ha for null area', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        }
      })

      const formatted = wrapper.vm.formatArea(null)
      expect(formatted).toBe('0 ha')
    })
  })

  describe('Slots', () => {
    it('should render image slot when provided', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        },
        slots: {
          image: '<img src="test.jpg" />'
        }
      })

      expect(wrapper.find('img').exists()).toBe(true)
    })

    it('should render header-actions slot when provided', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        },
        slots: {
          'header-actions': '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Action')
    })

    it('should render footer slot when provided', () => {
      const finca = createFinca()
      wrapper = mount(BaseFincaCard, {
        props: {
          finca
        },
        slots: {
          footer: '<div>Footer</div>'
        }
      })

      expect(wrapper.text()).toContain('Footer')
    })
  })
})

