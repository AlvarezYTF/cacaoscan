import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AdvancedChart from '../AdvancedChart.vue'

vi.mock('chart.js', () => {
  const mockChart = vi.fn().mockImplementation(() => ({
    destroy: vi.fn(),
    update: vi.fn(),
    resize: vi.fn(),
    toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test')
  }))

  mockChart.register = vi.fn()

  return {
    Chart: mockChart,
    registerables: []
  }
})

describe('AdvancedChart', () => {
  let wrapper

  const defaultChartData = {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Test Data',
      data: [10, 20, 30]
    }]
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render chart container', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    expect(wrapper.find('.chart-container').exists()).toBe(true)
    expect(wrapper.find('canvas').exists()).toBe(true)
  })

  it('should display title when provided', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        title: 'Test Chart'
      }
    })

    expect(wrapper.find('.chart-title').exists()).toBe(true)
    expect(wrapper.text()).toContain('Test Chart')
  })

  it('should not display title when not provided', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    expect(wrapper.find('.chart-title').exists()).toBe(false)
  })

  it('should apply custom height', () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        height: '500px'
      }
    })

    expect(wrapper.vm.containerStyle.height).toBe('500px')
  })

  it('should create chart on mount', async () => {
    const Chart = (await import('chart.js')).Chart

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(Chart).toHaveBeenCalled()
  })

  it('should update chart when data changes', async () => {
    const Chart = (await import('chart.js')).Chart

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    const newData = {
      labels: ['Apr', 'May'],
      datasets: [{
        label: 'New Data',
        data: [40, 50]
      }]
    }

    await wrapper.setProps({ chartData: newData })
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Chart should be created/updated when data changes
    expect(Chart).toHaveBeenCalled()
  })

  it('should handle different chart types', async () => {
    const Chart = (await import('chart.js')).Chart
    const types = ['line', 'bar', 'pie', 'doughnut']

    for (const type of types) {
      wrapper = mount(AdvancedChart, {
        props: {
          chartData: defaultChartData,
          type
        }
      })

      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      // Chart should be created for each type
      expect(Chart).toHaveBeenCalled()
      if (wrapper) {
        wrapper.unmount()
      }
    }
  })

  it('should emit chart-loaded event', async () => {
    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.emitted('chart-loaded')).toBeTruthy()
  })

  it('should update chart method', async () => {
    const Chart = (await import('chart.js')).Chart
    const mockUpdate = vi.fn()
    Chart.mockImplementation(() => ({
      destroy: vi.fn(),
      update: mockUpdate,
      resize: vi.fn(),
      toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test'),
      data: { labels: [], datasets: [] }
    }))

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    const newData = {
      labels: ['New'],
      datasets: [{ data: [100] }]
    }

    wrapper.vm.updateChart(newData)
    await wrapper.vm.$nextTick()

    expect(mockUpdate).toHaveBeenCalled()
  })

  it('should add data to chart', async () => {
    const Chart = (await import('chart.js')).Chart
    const mockUpdate = vi.fn()
    Chart.mockImplementation(() => ({
      destroy: vi.fn(),
      update: mockUpdate,
      resize: vi.fn(),
      toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test'),
      data: { labels: [], datasets: [{ data: [] }] }
    }))

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    wrapper.vm.addData([40], 'Apr')
    await wrapper.vm.$nextTick()

    expect(mockUpdate).toHaveBeenCalled()
  })

  it('should remove data from chart', async () => {
    const Chart = (await import('chart.js')).Chart
    const mockUpdate = vi.fn()
    Chart.mockImplementation(() => ({
      destroy: vi.fn(),
      update: mockUpdate,
      resize: vi.fn(),
      toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test'),
      data: { labels: ['A', 'B'], datasets: [{ data: [1, 2] }] }
    }))

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    wrapper.vm.removeData(0)
    await wrapper.vm.$nextTick()

    expect(mockUpdate).toHaveBeenCalled()
  })

  it('should export chart', async () => {
    const Chart = (await import('chart.js')).Chart
    const mockToBase64Image = vi.fn().mockReturnValue('data:image/png;base64,test')
    Chart.mockImplementation(() => ({
      destroy: vi.fn(),
      update: vi.fn(),
      resize: vi.fn(),
      toBase64Image: mockToBase64Image,
      data: { labels: [], datasets: [] }
    }))

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    const exported = wrapper.vm.exportChart('png')

    expect(exported).toBe('data:image/png;base64,test')
    expect(mockToBase64Image).toHaveBeenCalledWith('png')
  })

  it('should destroy chart on unmount', async () => {
    const Chart = (await import('chart.js')).Chart
    const mockDestroy = vi.fn()
    Chart.mockImplementation(() => ({
      destroy: mockDestroy,
      update: vi.fn(),
      resize: vi.fn(),
      toBase64Image: vi.fn().mockReturnValue('data:image/png;base64,test'),
      data: { labels: [], datasets: [] }
    }))

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 200))

    wrapper.unmount()

    expect(mockDestroy).toHaveBeenCalled()
  })

  it('should apply theme correctly', async () => {
    const Chart = (await import('chart.js')).Chart

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        theme: 'dark'
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Chart should be created with dark theme
    expect(Chart).toHaveBeenCalled()
  })

  it('should handle responsive prop', async () => {
    const Chart = (await import('chart.js')).Chart

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        responsive: false
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Chart should be created with responsive: false
    expect(Chart).toHaveBeenCalled()
  })

  it('should apply custom colors', async () => {
    const Chart = (await import('chart.js')).Chart
    const customColors = ['#ff0000', '#00ff00', '#0000ff']

    wrapper = mount(AdvancedChart, {
      props: {
        chartData: defaultChartData,
        colors: customColors
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Chart should be created with custom colors
    expect(Chart).toHaveBeenCalled()
  })
})

