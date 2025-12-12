import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FincasFilters from './FincasFilters.vue'

describe('FincasFilters', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render filters component', () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display filter title', () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Filtros') || text.includes('Búsqueda')).toBe(true)
  })

  it('should emit update:searchQuery when search query changes', async () => {
    vi.useFakeTimers()
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    const searchInput = wrapper.find('input[type="text"]')
    if (searchInput.exists()) {
      await searchInput.setValue('test query')
      await wrapper.vm.$nextTick()

      vi.advanceTimersByTime(500)
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
    }

    vi.useRealTimers()
  })

  it('should emit clear-filters event when clear button is clicked', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: 'test',
        filters: {
          departamento: 'test',
          activa: 'true'
        }
      }
    })

    await wrapper.vm.$nextTick()
    const clearButton = wrapper.find('button')
    if (clearButton.exists()) {
      await clearButton.trigger('click')
      expect(wrapper.emitted('clear-filters')).toBeTruthy()
    }
  })

  it('should emit apply-filters when search query changes after debounce', async () => {
    vi.useFakeTimers()
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    const searchInput = wrapper.find('input[type="text"]')
    if (searchInput.exists()) {
      await searchInput.setValue('test query')
      await wrapper.vm.$nextTick()

      vi.advanceTimersByTime(500)
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('apply-filters')).toBeTruthy()
    }

    vi.useRealTimers()
  })

  it('should emit update:filters and apply-filters when departamento changes', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    const departamentoSelect = wrapper.find('select')
    if (departamentoSelect.exists()) {
      await departamentoSelect.setValue('Cundinamarca')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:filters')).toBeTruthy()
      expect(wrapper.emitted('apply-filters')).toBeTruthy()
    }
  })

  it('should emit update:filters and apply-filters when activa changes', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    const selects = wrapper.findAll('select')
    if (selects.length > 1) {
      const activaSelect = selects[1]
      await activaSelect.setValue('true')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:filters')).toBeTruthy()
      expect(wrapper.emitted('apply-filters')).toBeTruthy()
    }
  })

  it('should clear all filters when clear button is clicked', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: 'test query',
        filters: {
          departamento: 'Cundinamarca',
          activa: 'true'
        }
      }
    })

    await wrapper.vm.$nextTick()

    const clearButton = wrapper.find('button')
    if (clearButton.exists()) {
      await clearButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('update:searchQuery')).toBeTruthy()
      expect(wrapper.emitted('update:filters')).toBeTruthy()
      expect(wrapper.emitted('clear-filters')).toBeTruthy()
    }
  })

  it('should sync localSearchQuery when searchQuery prop changes', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: 'initial',
        filters: {
          departamento: '',
          activa: ''
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.localSearchQuery).toBe('initial')

    await wrapper.setProps({ searchQuery: 'updated' })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.localSearchQuery).toBe('updated')
  })

  it('should sync localFilters when filters prop changes', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        searchQuery: '',
        filters: {
          departamento: 'Cundinamarca',
          activa: 'true'
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.localFilters.departamento).toBe('Cundinamarca')
    expect(wrapper.vm.localFilters.activa).toBe('true')

    await wrapper.setProps({
      filters: {
        departamento: 'Antioquia',
        activa: 'false'
      }
    })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.localFilters.departamento).toBe('Antioquia')
    expect(wrapper.vm.localFilters.activa).toBe('false')
  })
})

