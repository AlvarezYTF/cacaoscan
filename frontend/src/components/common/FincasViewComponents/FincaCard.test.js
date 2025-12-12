import { describe, it, expect, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaCard from './FincaCard.vue'

describe('FincaCard', () => {
  let wrapper

  const mockFinca = {
    id: 1,
    nombre: 'Test Finca',
    municipio: 'Test Municipio',
    departamento: 'Test Departamento',
    ubicacion: 'Test Ubicación',
    hectareas: 10,
    activa: true
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render finca card with finca data', () => {
    wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Finca')
    expect(wrapper.text()).toContain('Test Municipio')
    expect(wrapper.text()).toContain('Test Departamento')
  })

  it('should display active status correctly', () => {
    wrapper = mount(FincaCard, {
      props: {
        finca: { ...mockFinca, activa: true }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Activa')).toBe(true)
  })

  it('should display inactive status correctly', () => {
    wrapper = mount(FincaCard, {
      props: {
        finca: { ...mockFinca, activa: false }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Inactiva')).toBe(true)
  })

  it('should emit view-details event when clicked', async () => {
    wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca
      }
    })

    await wrapper.trigger('click')

    expect(wrapper.emitted('view-details')).toBeTruthy()
    expect(wrapper.emitted('view-details')[0]).toEqual([mockFinca])
  })
})

