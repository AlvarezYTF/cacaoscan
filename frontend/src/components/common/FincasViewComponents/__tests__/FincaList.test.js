import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaList from '../FincaList.vue'

describe('FincaList', () => {
  const mockFincas = [
    {
      id: 1,
      nombre: 'Finca 1',
      activa: true
    },
    {
      id: 2,
      nombre: 'Finca 2',
      activa: false
    }
  ]

  it('should show loading state', () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: true,
        error: null
      }
    })

    expect(wrapper.text()).toContain('Cargando fincas')
  })

  it('should show error state', () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: 'Error message'
      }
    })

    expect(wrapper.text()).toContain('Error al cargar')
    expect(wrapper.text()).toContain('Error message')
  })

  it('should emit retry when retry button is clicked', async () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: 'Error message'
      }
    })

    const retryButton = wrapper.find('button')
    await retryButton.trigger('click')

    expect(wrapper.emitted('retry')).toBeTruthy()
  })

  it('should render fincas list', () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: mockFincas,
        loading: false,
        error: null
      }
    })

    expect(wrapper.text()).toContain('Finca 1')
    expect(wrapper.text()).toContain('Finca 2')
  })

  it('should show empty state when no fincas', () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: null
      }
    })

    expect(wrapper.text()).toContain('No hay fincas registradas')
  })

  it('should emit create when create button is clicked in empty state', async () => {
    const wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: null
      }
    })

    const createButton = wrapper.find('button')
    await createButton.trigger('click')

    expect(wrapper.emitted('create')).toBeTruthy()
  })
})

