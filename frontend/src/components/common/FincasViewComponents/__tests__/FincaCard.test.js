import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaCard from '../FincaCard.vue'

describe('FincaCard', () => {
  const mockFinca = {
    id: 1,
    nombre: 'Finca Test',
    municipio: 'Medellín',
    departamento: 'Antioquia',
    ubicacion: 'Calle 123',
    hectareas: 10,
    activa: true,
    total_lotes: 5,
    total_analisis: 10
  }

  it('should render finca information', () => {
    const wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca,
        userRole: 'agricultor'
      }
    })

    expect(wrapper.text()).toContain('Finca Test')
    expect(wrapper.text()).toContain('Medellín')
    expect(wrapper.text()).toContain('Antioquia')
  })

  it('should emit view-details when card is clicked', async () => {
    const wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca,
        userRole: 'agricultor'
      }
    })

    const card = wrapper.find('.cursor-pointer')
    await card.trigger('click')

    expect(wrapper.emitted('view-details')).toBeTruthy()
    expect(wrapper.emitted('view-details')[0]).toEqual([mockFinca])
  })

  it('should emit edit when edit button is clicked', async () => {
    const wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca,
        userRole: 'admin'
      }
    })

    const editButton = wrapper.findAll('button').find(btn => btn.text().includes('Editar'))
    await editButton.trigger('click.stop')

    expect(wrapper.emitted('edit')).toBeTruthy()
  })

  it('should show activate button for inactive finca when user is admin', () => {
    const wrapper = mount(FincaCard, {
      props: {
        finca: { ...mockFinca, activa: false },
        userRole: 'admin'
      }
    })

    expect(wrapper.text()).toContain('Activar')
  })

  it('should display finca stats', () => {
    const wrapper = mount(FincaCard, {
      props: {
        finca: mockFinca,
        userRole: 'agricultor'
      }
    })

    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('10')
  })
})

