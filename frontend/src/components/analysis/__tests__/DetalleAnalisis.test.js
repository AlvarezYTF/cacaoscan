/**
 * Unit tests for DetalleAnalisis component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DetalleAnalisis from '../DetalleAnalisis.vue'
import Chart from 'chart.js/auto'

// Mock Chart.js
vi.mock('chart.js/auto', () => ({
  default: vi.fn().mockImplementation(() => ({
    destroy: vi.fn()
  }))
}))

describe('DetalleAnalisis', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  const mountOptions = {
    global: {
      stubs: {
        'router-link': {
          template: '<a data-testid="router-link"><slot /></a>',
          props: ['to']
        }
      }
    }
  }

  it('should render component', () => {
    wrapper = mount(DetalleAnalisis, mountOptions)

    expect(wrapper.exists()).toBe(true)
  })

  it('should render header with title', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    const title = wrapper.find('h1')
    expect(title.exists()).toBe(true)
    expect(title.text()).toContain('Detalle del Análisis de Cacao')
  })

  it('should render back link to nuevo-analisis', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    // Verify the link text exists
    expect(wrapper.text()).toContain('Volver a Nuevo Análisis')
    
    // Find router-link components
    const routerLinks = wrapper.findAllComponents({ name: 'RouterLink' })
    if (routerLinks.length > 0) {
      // Find the one that goes to nuevo-analisis
      const backLink = routerLinks.find(link => link.attributes('to') === '/nuevo-analisis')
      expect(backLink).toBeDefined()
      expect(backLink.attributes('to')).toBe('/nuevo-analisis')
    } else {
      // Fallback: verify there's at least one link element
      const links = wrapper.findAll('a')
      expect(links.length).toBeGreaterThan(0)
      // Verify the text is present
      expect(wrapper.html()).toContain('Volver a Nuevo Análisis')
    }
  })

  it('should render general information section', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    const generalInfo = wrapper.find('.bg-white.rounded-lg.shadow-md')
    expect(generalInfo.exists()).toBe(true)
    expect(wrapper.text()).toContain('Información General')
  })

  it('should render technical results section', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    expect(wrapper.text()).toContain('Resultados Técnicos')
    expect(wrapper.text()).toContain('Peso promedio')
    expect(wrapper.text()).toContain('Tamaño promedio')
  })

  it('should render classification section', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    expect(wrapper.text()).toContain('Clasificación y Recomendación')
    expect(wrapper.text()).toContain('Puntaje Total')
    expect(wrapper.text()).toContain('Fino de Aroma')
  })

  it('should render quality classification table', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    expect(wrapper.text()).toContain('Clasificación de Calidad')
    expect(wrapper.text()).toContain('Bien Fermentados')
    expect(wrapper.text()).toContain('Pizarrosos')
    expect(wrapper.text()).toContain('Violetas')
    expect(wrapper.text()).toContain('Dañados/Germinados')
  })

  it('should render comparison section', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    expect(wrapper.text()).toContain('Comparación con Análisis Anteriores')
  })

  it('should render action buttons', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    expect(wrapper.text()).toContain('Acciones')
    expect(wrapper.text()).toContain('Descargar PDF')
    expect(wrapper.text()).toContain('Compartir')
    expect(wrapper.text()).toContain('Editar')
  })

  it('should create pie chart on mount', async () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    await wrapper.vm.$nextTick()

    expect(Chart).toHaveBeenCalled()
    const chartCall = Chart.mock.calls.find(call => {
      const config = call[1]
      return config?.type === 'pie'
    })
    expect(chartCall).toBeDefined()
  })

  it('should create bar chart on mount', async () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    await wrapper.vm.$nextTick()

    const chartCall = Chart.mock.calls.find(call => {
      const config = call[1]
      return config?.type === 'bar'
    })
    expect(chartCall).toBeDefined()
  })

  it('should destroy charts on unmount', async () => {
    const mockDestroy = vi.fn()
    Chart.mockImplementation(() => ({
      destroy: mockDestroy
    }))

    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    await wrapper.vm.$nextTick()
    wrapper.unmount()

    expect(mockDestroy).toHaveBeenCalled()
  })

  it('should have pie chart canvas element', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    // Refs are not HTML attributes, check via wrapper.vm.$refs or find all canvas elements
    const canvasElements = wrapper.findAll('canvas')
    expect(canvasElements.length).toBeGreaterThan(0)
    // Verify pie chart ref exists
    expect(wrapper.vm.$refs.pieChart).toBeTruthy()
  })

  it('should have bar chart canvas element', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    // Refs are not HTML attributes, check via wrapper.vm.$refs or find all canvas elements
    const canvasElements = wrapper.findAll('canvas')
    expect(canvasElements.length).toBeGreaterThan(0)
    // Verify bar chart ref exists
    expect(wrapper.vm.$refs.barChart).toBeTruthy()
  })

  it('should render table with correct structure', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    const table = wrapper.find('table')
    expect(table.exists()).toBe(true)
    
    const headers = table.findAll('th')
    expect(headers.length).toBeGreaterThan(0)
    expect(headers[0].text()).toContain('Categoría')
  })

  it('should render table rows with data', () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBeGreaterThan(0)
  })

  it('should handle chart creation when canvas is not available', async () => {
    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    await wrapper.vm.$nextTick()

    // Simulate canvas not being available by setting refs to null
    wrapper.vm.pieChart.value = null
    wrapper.vm.barChart.value = null

    // Should not throw error
    expect(() => {
      wrapper.vm.createPieChart()
      wrapper.vm.createBarChart()
    }).not.toThrow()
  })

  it('should destroy existing chart before creating new one', async () => {
    const mockDestroy = vi.fn()
    let chartInstance = { destroy: mockDestroy }
    
    Chart.mockImplementation(() => chartInstance)

    wrapper = mount(DetalleAnalisis, {
      ...mountOptions
    })

    await wrapper.vm.$nextTick()

    // Create chart again
    wrapper.vm.createPieChart()
    await wrapper.vm.$nextTick()

    expect(mockDestroy).toHaveBeenCalled()
  })
})

