/**
 * Unit tests for useChart composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'

// Use vi.hoisted() to define mocks before vi.mock() hoisting
const { MockChart } = vi.hoisted(() => {
  const MockChart = vi.fn(function(ctx, config) {
    this.destroy = vi.fn()
    this.update = vi.fn()
    this.resize = vi.fn()
    this.toBase64Image = vi.fn(() => 'base64-image')
    // Initialize data as mutable property that can be reassigned
    // Use Object.assign to ensure the property is writable
    if (config?.data) {
      this.data = { ...config.data }
    } else {
      this.data = {}
    }
    this.options = config?.options || {}
    this.config = config
    return this
  })
  MockChart.register = vi.fn()
  return { MockChart }
})

// Mock Chart.js
vi.mock('chart.js', () => ({
  Chart: MockChart,
  registerables: []
}))

// Import useChart after mocking chart.js
import { useChart } from '../useChart.js'

// Mock canvas context
const mockContext = {
  fillRect: vi.fn(),
  clearRect: vi.fn()
}

const mockCanvas = {
  getContext: vi.fn(() => mockContext)
}

describe('useChart', () => {
  let chart

  beforeEach(() => {
    // Clear mocks but preserve MockChart constructor
    mockCanvas.getContext.mockClear()
    mockContext.fillRect.mockClear()
    mockContext.clearRect.mockClear()
    MockChart.mockClear()
    
    chart = useChart({
      chartData: {
        labels: ['A', 'B'],
        datasets: [{
          data: [1, 2]
        }]
      },
      type: 'line'
    })
    
    // Set mock canvas
    chart.chartRef.value = mockCanvas
  })

  describe('initial state', () => {
    it('should have chartRef', () => {
      expect(chart.chartRef).toBeDefined()
    })
  })

  describe('createChart', () => {
    it('should create chart instance', async () => {
      await chart.createChart()
      
      expect(mockCanvas.getContext).toHaveBeenCalledWith('2d')
      expect(MockChart).toHaveBeenCalled()
      const chartInstance = chart.chartInstance()
      expect(chartInstance).toBeDefined()
      expect(chartInstance.destroy).toBeDefined()
    })

    it('should not create chart if no chartRef', async () => {
      chart.chartRef.value = null
      
      await chart.createChart()
      
      expect(mockCanvas.getContext).not.toHaveBeenCalled()
    })

    it('should destroy existing chart before creating new', async () => {
      await chart.createChart()
      
      const firstInstance = chart.chartInstance()
      await chart.createChart()
      
      expect(firstInstance.destroy).toHaveBeenCalled()
    })
  })

  describe('updateChart', () => {
    it('should update chart data', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      const initialData = instance.data
      const newData = { labels: ['C'], datasets: [] }
      
      chart.updateChart(newData)
      
      // Verify that data was reassigned (should be a new reference)
      expect(instance.data).not.toBe(initialData)
      expect(instance.data).toEqual(newData)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should not update if no instance', () => {
      chart.updateChart({})
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('destroyChart', () => {
    it('should destroy chart instance', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      chart.destroyChart()
      
      expect(instance.destroy).toHaveBeenCalled()
    })
  })

  describe('exportChart', () => {
    it('should export chart as image', async () => {
      await chart.createChart()
      
      const result = chart.exportChart('png')
      
      const instance = chart.chartInstance()
      expect(instance.toBase64Image).toHaveBeenCalledWith('png')
      expect(result).toBe('base64-image')
    })

    it('should return null if no instance', () => {
      const result = chart.exportChart()
      
      expect(result).toBe(null)
    })
  })

  describe('updateOptions', () => {
    it('should update chart options', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      const newOptions = { responsive: true }
      
      chart.updateOptions(newOptions)
      
      expect(instance.options).toMatchObject(newOptions)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should not update if no instance', () => {
      chart.updateOptions({})
      
      // Should not throw
      expect(true).toBe(true)
    })

    it('should not update if no options provided', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      const updateSpy = vi.spyOn(instance, 'update')
      
      chart.updateOptions(null)
      
      expect(updateSpy).not.toHaveBeenCalled()
    })
  })

  describe('addData', () => {
    it('should add data point with label', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      instance.data.labels = ['A', 'B']
      instance.data.datasets = [{ data: [1, 2] }]
      
      chart.addData(3, 'C')
      
      expect(instance.data.labels).toContain('C')
      expect(instance.data.datasets[0].data).toContain(3)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should add array data to multiple datasets', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      instance.data.datasets = [
        { data: [1, 2] },
        { data: [3, 4] }
      ]
      
      chart.addData([5, 6])
      
      expect(instance.data.datasets[0].data).toContain(5)
      expect(instance.data.datasets[1].data).toContain(6)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should add single value to all datasets', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      instance.data.datasets = [
        { data: [1, 2] },
        { data: [3, 4] }
      ]
      
      chart.addData(5)
      
      expect(instance.data.datasets[0].data).toContain(5)
      expect(instance.data.datasets[1].data).toContain(5)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should not add data if no instance', () => {
      chart.addData(1, 'Label')
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('removeData', () => {
    it('should remove data point by index', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      instance.data.labels = ['A', 'B', 'C']
      instance.data.datasets = [
        { data: [1, 2, 3] },
        { data: [4, 5, 6] }
      ]
      
      chart.removeData(1)
      
      expect(instance.data.labels).not.toContain('B')
      expect(instance.data.datasets[0].data).not.toContain(2)
      expect(instance.data.datasets[1].data).not.toContain(5)
      expect(instance.update).toHaveBeenCalled()
    })

    it('should not remove if index out of bounds', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      instance.data.labels = ['A']
      instance.data.datasets = [{ data: [1] }]
      
      const initialLength = instance.data.labels.length
      chart.removeData(5)
      
      expect(instance.data.labels.length).toBe(initialLength)
    })

    it('should not remove data if no instance', () => {
      chart.removeData(0)
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('resizeChart', () => {
    it('should resize chart', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      chart.resizeChart()
      
      expect(instance.resize).toHaveBeenCalled()
    })

    it('should not resize if no instance', () => {
      chart.resizeChart()
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('createChart edge cases', () => {
    it('should not create chart if no data', async () => {
      const chartWithoutData = useChart({
        chartData: null,
        type: 'line'
      })
      chartWithoutData.chartRef.value = mockCanvas
      
      await chartWithoutData.createChart()
      
      expect(MockChart).not.toHaveBeenCalled()
    })

    it('should handle onClick handler', async () => {
      const onClick = vi.fn()
      const chartWithClick = useChart({
        chartData: { labels: ['A'], datasets: [{ data: [1] }] },
        type: 'line',
        onClick
      })
      chartWithClick.chartRef.value = mockCanvas
      
      await chartWithClick.createChart()
      
      const instance = chartWithClick.chartInstance()
      const mockEvent = {}
      const mockElements = [{ datasetIndex: 0, index: 0, element: { $context: { parsed: 1 } } }]
      
      instance.config.options.onClick(mockEvent, mockElements)
      
      expect(onClick).toHaveBeenCalled()
    })

    it('should not call onClick if no elements', async () => {
      const onClick = vi.fn()
      const chartWithClick = useChart({
        chartData: { labels: ['A'], datasets: [{ data: [1] }] },
        type: 'line',
        onClick
      })
      chartWithClick.chartRef.value = mockCanvas
      
      await chartWithClick.createChart()
      
      const instance = chartWithClick.chartInstance()
      const mockEvent = {}
      const mockElements = []
      
      instance.config.options.onClick(mockEvent, mockElements)
      
      expect(onClick).not.toHaveBeenCalled()
    })

    it('should handle onHover handler', async () => {
      const onHover = vi.fn()
      const chartWithHover = useChart({
        chartData: { labels: ['A'], datasets: [{ data: [1] }] },
        type: 'line',
        onHover
      })
      chartWithHover.chartRef.value = mockCanvas
      
      await chartWithHover.createChart()
      
      const instance = chartWithHover.chartInstance()
      const mockEvent = {}
      const mockElements = [{ datasetIndex: 0, index: 0 }]
      
      instance.config.options.onHover(mockEvent, mockElements)
      
      expect(onHover).toHaveBeenCalled()
    })

    it('should handle onLoaded callback', async () => {
      const onLoaded = vi.fn()
      const chartWithLoaded = useChart({
        chartData: { labels: ['A'], datasets: [{ data: [1] }] },
        type: 'line',
        onLoaded
      })
      chartWithLoaded.chartRef.value = mockCanvas
      
      await chartWithLoaded.createChart()
      
      expect(onLoaded).toHaveBeenCalled()
    })

    it('should handle reactive type', async () => {
      const typeRef = { value: 'bar' }
      const chartWithReactiveType = useChart({
        chartData: { labels: ['A'], datasets: [{ data: [1] }] },
        type: typeRef
      })
      chartWithReactiveType.chartRef.value = mockCanvas
      
      await chartWithReactiveType.createChart()
      
      const instance = chartWithReactiveType.chartInstance()
      expect(instance.config.type).toBe('bar')
    })

    it('should handle getContext returning null', async () => {
      const canvasWithoutContext = {
        getContext: vi.fn(() => null)
      }
      chart.chartRef.value = canvasWithoutContext
      
      await chart.createChart()
      
      expect(MockChart).not.toHaveBeenCalled()
    })
  })

  describe('updateChart edge cases', () => {
    it('should not update if no newData', async () => {
      await chart.createChart()
      
      const instance = chart.chartInstance()
      const updateSpy = vi.spyOn(instance, 'update')
      
      chart.updateChart(null)
      
      expect(updateSpy).not.toHaveBeenCalled()
    })
  })
})

