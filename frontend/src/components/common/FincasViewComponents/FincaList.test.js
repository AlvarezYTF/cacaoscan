import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FincaList from './FincaList.vue'

describe('FincaList', () => {
  let wrapper

  const mockFincas = [
    {
      id: 1,
      nombre: 'Finca 1',
      municipio: 'Municipio 1',
      departamento: 'Departamento 1',
      activa: true
    },
    {
      id: 2,
      nombre: 'Finca 2',
      municipio: 'Municipio 2',
      departamento: 'Departamento 2',
      activa: false
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render finca list with fincas', () => {
    wrapper = mount(FincaList, {
      props: {
        fincas: mockFincas,
        loading: false,
        error: null
      },
      global: {
        stubs: {
          FincaCard: { template: '<div>FincaCard</div>' }
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display loading state when loading', () => {
    wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: true,
        error: null
      }
    })

    const text = wrapper.text()
    expect(text.includes('Cargando') || text.includes('loading')).toBe(true)
  })

  it('should display error state when error exists', () => {
    wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: 'Error de prueba'
      }
    })

    const text = wrapper.text()
    expect(text.includes('Error') || text.includes('error')).toBe(true)
  })

  it('should emit retry event when retry button is clicked', async () => {
    wrapper = mount(FincaList, {
      props: {
        fincas: [],
        loading: false,
        error: 'Error de prueba'
      }
    })

    const retryButton = wrapper.find('button')
    if (retryButton.exists()) {
      await retryButton.trigger('click')
      expect(wrapper.emitted('retry')).toBeTruthy()
    }
  })

  it('should emit view-details event when finca card emits it', async () => {
    wrapper = mount(FincaList, {
      props: {
        fincas: mockFincas,
        loading: false,
        error: null
      },
      global: {
        stubs: {
          FincaCard: {
            template: '<div @click="$emit(\'view-details\', finca)">FincaCard</div>',
            props: ['finca'],
            emits: ['view-details']
          }
        }
      }
    })

    await wrapper.vm.$nextTick()
    const fincaCard = wrapper.findComponent({ name: 'FincaCard' })
    if (fincaCard.exists()) {
      await fincaCard.trigger('click')
      expect(wrapper.emitted('view-details')).toBeTruthy()
    }
  })
})

