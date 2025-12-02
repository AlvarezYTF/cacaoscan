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
})

