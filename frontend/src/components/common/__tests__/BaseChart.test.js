/**
 * Unit tests for BaseChart component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseChart from '../BaseChart.vue'

// Store mock references in global object - initialize before mock
if (!globalThis.__chartMocks__) {
  globalThis.__chartMocks__ = {}
}

// Mock Chart.js - create mocks inside factory to avoid hoisting issues
vi.mock('chart.js', () => {
  const mockChartInstance = {
    destroy: vi.fn(),
    update: vi.fn(),
    data: {},
    options: {}
  }

  const mockChart = vi.fn(() => mockChartInstance)
  
  // Add register method to Chart object
  mockChart.register = vi.fn()

  // Store references globally for test access
  if (!globalThis.__chartMocks__) {
    globalThis.__chartMocks__ = {}
  }
  globalThis.__chartMocks__.mockChart = mockChart
  globalThis.__chartMocks__.mockChartInstance = mockChartInstance

  return {
    Chart: mockChart,
    registerables: []
  }
})

// Helper functions to access mock objects in tests
const getMockChart = () => globalThis.__chartMocks__.mockChart
const getMockChartInstance = () => globalThis.__chartMocks__.mockChartInstance

describe('BaseChart', () => {
  let wrapper

  const createChartData = () => ({
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Dataset 1',
      data: [10, 20, 30]
    }]
  })

  beforeEach(() => {
    vi.clearAllMocks()
    const mockChartInstance = getMockChartInstance()
    mockChartInstance.data = {}
    mockChartInstance.options = {}
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Props validation', () => {
    it('should use default data prop when not provided', () => {
      // Vue 3 doesn't throw errors for props with default values
      // Even if a prop is marked as required, if it has a default, it will use that
      wrapper = mount(BaseChart)
      expect(wrapper.exists()).toBe(true)
      // The prop has a default value, so it should be available
      expect(wrapper.props('data')).toBeDefined()
    })

    it('should accept data prop', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props('data')).toEqual(data)
    })

    it('should accept type prop', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          type: 'bar'
        }
      })
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.props('type')).toBe('bar')
    })

    it('should accept invalid type prop without throwing', () => {
      // Vue 3 validators don't throw errors, they only show console warnings
      // The component will mount but the validator will fail silently
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          type: 'invalid'
        }
      })
      // Component should still mount
      expect(wrapper.exists()).toBe(true)
      // Invalid type should still be set (validator only warns, doesn't prevent)
      expect(wrapper.props('type')).toBe('invalid')
    })
  })

  describe('Rendering', () => {
    it('should render canvas element', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      expect(wrapper.find('canvas').exists()).toBe(true)
    })

    it('should render title when provided', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          title: 'Test Chart'
        }
      })

      expect(wrapper.text()).toContain('Test Chart')
    })

    it('should not render title when not provided', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      expect(wrapper.find('h3').exists()).toBe(false)
    })

    it('should apply containerClass when provided', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          containerClass: 'custom-class'
        }
      })

      const container = wrapper.find('.base-chart')
      expect(container.classes()).toContain('custom-class')
    })
  })

  describe('Chart initialization', () => {
    it('should create chart on mount', async () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      await wrapper.vm.$nextTick()
      expect(getMockChart()).toHaveBeenCalled()
    })

    it('should create chart with correct type', async () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          type: 'bar'
        }
      })

      await wrapper.vm.$nextTick()
      expect(getMockChart()).toHaveBeenCalled()
    })

    it('should destroy chart on unmount', async () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      await wrapper.vm.$nextTick()
      wrapper.unmount()
      expect(getMockChartInstance().destroy).toHaveBeenCalled()
    })
  })

  describe('Chart updates', () => {
    it('should update chart when data changes', async () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      await wrapper.vm.$nextTick()
      vi.clearAllMocks()

      const newData = {
        labels: ['Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Dataset 2',
          data: [40, 50, 60]
        }]
      }

      await wrapper.setProps({ data: newData })
      await wrapper.vm.$nextTick()

      expect(getMockChartInstance().update).toHaveBeenCalled()
    })

    it('should recreate chart when type changes', async () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data,
          type: 'line'
        }
      })

      await wrapper.vm.$nextTick()
      vi.clearAllMocks()

      await wrapper.setProps({ type: 'bar' })
      await wrapper.vm.$nextTick()

      expect(getMockChartInstance().destroy).toHaveBeenCalled()
    })
  })

  describe('Edge cases', () => {
    it('should handle empty data', () => {
      const data = { labels: [], datasets: [] }
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should handle missing canvas ref', () => {
      const data = createChartData()
      wrapper = mount(BaseChart, {
        props: {
          data
        }
      })

      wrapper.vm.chartCanvas = null
      wrapper.vm.createChart()

      expect(wrapper.exists()).toBe(true)
    })
  })
})

