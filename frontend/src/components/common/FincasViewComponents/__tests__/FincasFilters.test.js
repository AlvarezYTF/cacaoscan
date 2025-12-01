import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FincasFilters from '../FincasFilters.vue'

vi.mock('@/services/fincasApi', () => ({
  default: {
    getDepartamentosColombia: () => ['Antioquia', 'Cundinamarca', 'Valle']
  }
}))

describe('FincasFilters', () => {
  it('should render filters', () => {
    const wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: { departamento: '', activa: '' }
      }
    })

    expect(wrapper.text()).toContain('Filtros de Búsqueda')
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('should emit update:searchQuery when search input changes', async () => {
    const wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: { departamento: '', activa: '' }
      }
    })

    const input = wrapper.find('input')
    await input.setValue('test search')
    
    // Wait for debounce (500ms)
    await new Promise(resolve => setTimeout(resolve, 600))
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
  })

  it('should emit update:filters when filter changes', async () => {
    const wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: { departamento: '', activa: '' }
      }
    })

    const select = wrapper.findAll('select')[0]
    await select.setValue('Antioquia')

    expect(wrapper.emitted('update:filters')).toBeTruthy()
  })

  it('should emit clear-filters when clear button is clicked', async () => {
    const wrapper = mount(FincasFilters, {
      props: {
        searchQuery: 'test',
        filters: { departamento: 'Antioquia', activa: 'true' }
      }
    })

    const clearButton = wrapper.find('button')
    await clearButton.trigger('click')

    expect(wrapper.emitted('clear-filters')).toBeTruthy()
  })
})

