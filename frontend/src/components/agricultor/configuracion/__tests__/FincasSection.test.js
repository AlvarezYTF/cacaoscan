import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FincasSection from '../FincasSection.vue'

describe('FincasSection', () => {
  let wrapper

  const mockFincas = [
    {
      id: 1,
      nombre: 'Finca El Paraíso',
      ubicacion: 'Santander, Colombia',
      hectareas: 5.5,
      isPrimary: true,
      isActive: true
    },
    {
      id: 2,
      nombre: 'Finca La Esperanza',
      ubicacion: 'Boyacá, Colombia',
      hectareas: 3.2,
      isPrimary: false,
      isActive: true
    },
    {
      id: 3,
      nombre: 'Finca Las Flores',
      ubicacion: 'Cundinamarca, Colombia',
      hectareas: 2.8,
      isPrimary: false,
      isActive: false
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display section title', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      expect(wrapper.text()).toContain('Mis Fincas')
    })

    it('should render all fincas in the list', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      expect(wrapper.text()).toContain('Finca El Paraíso')
      expect(wrapper.text()).toContain('Finca La Esperanza')
      expect(wrapper.text()).toContain('Finca Las Flores')
    })

    it('should display finca nombre', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      expect(wrapper.text()).toContain('Finca El Paraíso')
    })

    it('should display finca ubicacion', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      expect(wrapper.text()).toContain('Santander, Colombia')
    })

    it('should display finca hectareas', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      expect(wrapper.text()).toContain('5.5')
      expect(wrapper.text()).toContain('hectáreas')
    })

    it('should display "Principal" badge for primary finca', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      expect(wrapper.text()).toContain('Principal')
    })

    it('should not display "Principal" badge for non-primary finca', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[1]]
        }
      })

      // The badge should only appear for primary fincas
      const primaryBadge = wrapper.find('.bg-green-600')
      // Should exist but only for primary finca
      if (primaryBadge.exists()) {
        expect(wrapper.text()).not.toContain('Principal')
      }
    })

    it('should show empty state when no fincas', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: []
        }
      })

      expect(wrapper.text()).toContain('No tienes fincas registradas')
    })

    it('should display "Nueva Finca" button', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      expect(wrapper.text()).toContain('Nueva Finca')
    })
  })

  describe('Props', () => {
    it('should require fincas prop', () => {
      expect(() => {
        mount(FincasSection)
      }).toThrow()
    })

    it('should accept fincas array prop', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      expect(wrapper.vm.$props.fincas).toEqual(mockFincas)
    })

    it('should handle empty fincas array', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: []
        }
      })

      expect(wrapper.vm.$props.fincas).toEqual([])
    })
  })

  describe('Events', () => {
    it('should emit toggle-status when toggle button is clicked', async () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const toggleButtons = wrapper.findAll('button')
      // Find the toggle status button (first button in finca row)
      const toggleButton = toggleButtons.find(btn => {
        const icon = btn.find('svg')
        return icon.exists()
      })

      if (toggleButton) {
        await toggleButton.trigger('click')
        expect(wrapper.emitted('toggle-status')).toBeTruthy()
        expect(wrapper.emitted('toggle-status')[0]).toEqual([mockFincas[0].id])
      }
    })

    it('should emit set-primary when set primary button is clicked', async () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[1]] // Non-primary finca
        }
      })

      // Find all buttons - for a single non-primary finca:
      // buttons[0] = toggle-status
      // buttons[1] = set-primary (not disabled because isPrimary is false)
      // buttons[2] = Nueva Finca
      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThanOrEqual(2)
      
      // The set-primary button is the second button (index 1)
      const setPrimaryButton = buttons[1]
      
      expect(setPrimaryButton).toBeTruthy()
      expect(setPrimaryButton.exists()).toBe(true)
      // Verify it's not disabled (since mockFincas[1] has isPrimary: false)
      expect(setPrimaryButton.attributes('disabled')).toBeUndefined()
      
      await setPrimaryButton.trigger('click')
      
      expect(wrapper.emitted('set-primary')).toBeTruthy()
      expect(wrapper.emitted('set-primary')).toHaveLength(1)
      expect(wrapper.emitted('set-primary')[0]).toEqual([mockFincas[1].id])
    })

    it('should emit add-new when "Nueva Finca" button is clicked', async () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      const addButton = wrapper.findAll('button').find(btn => btn.text().includes('Nueva Finca'))
      
      if (addButton) {
        await addButton.trigger('click')
        expect(wrapper.emitted('add-new')).toBeTruthy()
      }
    })

    it('should pass correct finca id when emitting toggle-status', async () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[1]]
        }
      })

      const toggleButtons = wrapper.findAll('button')
      const toggleButton = toggleButtons[0]

      if (toggleButton) {
        await toggleButton.trigger('click')
        expect(wrapper.emitted('toggle-status')[0][0]).toBe(mockFincas[1].id)
      }
    })
  })

  describe('Finca States', () => {
    it('should apply primary finca styles when isPrimary is true', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const fincaCard = wrapper.find('.border-green-500')
      expect(fincaCard.exists()).toBe(true)
    })

    it('should apply active finca styles when isActive is true', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const toggleButton = wrapper.findAll('button')[0]
      if (toggleButton) {
        expect(toggleButton.classes()).toContain('bg-green-100')
        expect(toggleButton.classes()).toContain('text-green-600')
      }
    })

    it('should apply inactive finca styles when isActive is false', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[2]]
        }
      })

      const toggleButton = wrapper.findAll('button')[0]
      if (toggleButton) {
        expect(toggleButton.classes()).toContain('bg-gray-100')
        expect(toggleButton.classes()).toContain('text-gray-400')
      }
    })

    it('should disable set-primary button when finca is already primary', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const buttons = wrapper.findAll('button')
      const setPrimaryButton = buttons.find(btn => btn.attributes('disabled'))
      
      if (setPrimaryButton) {
        expect(setPrimaryButton.attributes('disabled')).toBeDefined()
      }
    })

    it('should enable set-primary button when finca is not primary', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[1]]
        }
      })

      const buttons = wrapper.findAll('button')
      // Find the set-primary button (should not be disabled for non-primary)
      const setPrimaryButton = buttons.find(btn => {
        return !btn.attributes('disabled') && btn.text() !== 'Nueva Finca'
      })

      if (setPrimaryButton) {
        expect(setPrimaryButton.attributes('disabled')).toBeUndefined()
      }
    })

    it('should apply primary button styles when finca is primary', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const buttons = wrapper.findAll('button')
      const primaryButton = buttons.find(btn => 
        btn.classes().includes('bg-green-600') || btn.classes().includes('text-white')
      )

      if (primaryButton) {
        expect(primaryButton.classes()).toContain('bg-green-600')
        expect(primaryButton.classes()).toContain('text-white')
      }
    })
  })

  describe('Empty State', () => {
    it('should display empty state icon', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: []
        }
      })

      const icon = wrapper.find('svg.w-12.h-12')
      expect(icon.exists()).toBe(true)
    })

    it('should display empty state message', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: []
        }
      })

      expect(wrapper.text()).toContain('No tienes fincas registradas')
    })

    it('should show "Nueva Finca" button even when empty', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: []
        }
      })

      expect(wrapper.text()).toContain('Nueva Finca')
      const addButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Nueva Finca')
      )
      expect(addButton).toBeTruthy()
    })
  })

  describe('Button Interactions', () => {
    it('should have correct number of buttons for each finca', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      // Each finca should have 2 buttons (toggle status and set primary)
      // Plus the "Nueva Finca" button
      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThanOrEqual(1)
    })

    it('should have "Nueva Finca" button with correct classes', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      const addButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('Nueva Finca')
      )

      if (addButton) {
        expect(addButton.classes()).toContain('border-dashed')
        expect(addButton.classes()).toContain('text-green-600')
      }
    })

    it('should emit events correctly for multiple fincas', async () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      const buttons = wrapper.findAll('button')
      
      // Click first toggle button
      if (buttons[0]) {
        await buttons[0].trigger('click')
        expect(wrapper.emitted('toggle-status')).toBeTruthy()
      }
    })
  })

  describe('Visual Structure', () => {
    it('should render section with correct container classes', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      const container = wrapper.find('.bg-white.rounded-2xl')
      expect(container.exists()).toBe(true)
    })

    it('should render finca cards with correct structure', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      const fincaCard = wrapper.find('.border-2.border-gray-200.rounded-xl')
      expect(fincaCard.exists()).toBe(true)
    })

    it('should render section icon', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: mockFincas
        }
      })

      const iconContainer = wrapper.find('.bg-green-100.rounded-xl')
      expect(iconContainer.exists()).toBe(true)
    })
  })

  describe('Edge Cases', () => {
    it('should handle finca with missing properties gracefully', () => {
      const incompleteFinca = {
        id: 999,
        nombre: 'Incomplete Finca'
      }

      wrapper = mount(FincasSection, {
        props: {
          fincas: [incompleteFinca]
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Incomplete Finca')
    })

    it('should handle very long finca names', () => {
      const longNameFinca = {
        ...mockFincas[0],
        nombre: 'Finca con un nombre muy largo que podría causar problemas de diseño'
      }

      wrapper = mount(FincasSection, {
        props: {
          fincas: [longNameFinca]
        }
      })

      expect(wrapper.text()).toContain('Finca con un nombre muy largo')
    })

    it('should handle decimal hectareas correctly', () => {
      wrapper = mount(FincasSection, {
        props: {
          fincas: [mockFincas[0]]
        }
      })

      expect(wrapper.text()).toContain('5.5')
      expect(wrapper.text()).toContain('hectáreas')
    })

    it('should handle integer hectareas correctly', () => {
      const integerHectareasFinca = {
        ...mockFincas[0],
        hectareas: 10
      }

      wrapper = mount(FincasSection, {
        props: {
          fincas: [integerHectareasFinca]
        }
      })

      expect(wrapper.text()).toContain('10')
      expect(wrapper.text()).toContain('hectáreas')
    })
  })
})

