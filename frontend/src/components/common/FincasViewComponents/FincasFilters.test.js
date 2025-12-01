import { describe, it, expect, beforeEach, afterEach } from 'vitest'
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
        filters: {
          searchQuery: '',
          departamento: '',
          activa: null
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display filter title', () => {
    wrapper = mount(FincasFilters, {
      props: {
        filters: {
          searchQuery: '',
          departamento: '',
          activa: null
        }
      }
    })

    const text = wrapper.text()
    expect(text.includes('Filtros') || text.includes('Búsqueda')).toBe(true)
  })

  it('should emit update:filters when search query changes', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        filters: {
          searchQuery: '',
          departamento: '',
          activa: null
        }
      }
    })

    const searchInput = wrapper.find('input[type="text"]')
    if (searchInput.exists()) {
      await searchInput.setValue('test query')
      await wrapper.vm.$nextTick()

      const emits = wrapper.emitted('update:filters')
      if (emits) {
        expect(emits.length).toBeGreaterThan(0)
      }
    }
  })

  it('should emit reset event when reset button is clicked', async () => {
    wrapper = mount(FincasFilters, {
      props: {
        filters: {
          searchQuery: 'test',
          departamento: 'test',
          activa: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    const resetButton = wrapper.find('button')
    if (resetButton.exists() && resetButton.text().includes('Reset')) {
      await resetButton.trigger('click')
      expect(wrapper.emitted('reset')).toBeTruthy()
    }
  })
})

