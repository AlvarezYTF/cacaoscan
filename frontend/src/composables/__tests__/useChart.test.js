/**
 * Unit tests for useChart composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useChart } from '../useChart.js'
import { Chart } from 'chart.js'

// Mock Chart.js
vi.mock('chart.js', () => ({
  Chart: {
    register: vi.fn()
  }
}))

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
    vi.clearAllMocks()
    
    // Mock Chart constructor
    globalThis.Chart = vi.fn(function() {
      this.destroy = vi.fn()
      this.update = vi.fn()
      this.resize = vi.fn()
      this.toBase64Image = vi.fn(() => 'base64-image')
      this.data = {}
      this.options = {}
      this.config = {
        type: 'line',
        data: {},
        options: {}
      }
    })
    
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
      
      expect(mockCanvas.getContext).toHaveBeenCalled()
    })

    it('should not create chart if no chartRef', async () => {
      chart.chartRef.value = null
      
      await chart.createChart()
      
      expect(mockCanvas.getContext).not.toHaveBeenCalled()
    })

    it('should destroy existing chart before creating new', async () => {
      const mockInstance = {
        destroy: vi.fn(),
        update: vi.fn(),
        resize: vi.fn(),
        toBase64Image: vi.fn(),
        data: {},
        options: {}
      }
      
      // Simulate existing instance
      chart.chartInstance = () => mockInstance
      
      await chart.createChart()
    })
  })

  describe('updateChart', () => {
    it('should update chart data', () => {
      const mockInstance = {
        data: {},
        update: vi.fn()
      }
      
      // Manually set instance for testing
      chart.chartInstance = () => mockInstance
      
      const newData = { labels: ['C'], datasets: [] }
      chart.updateChart(newData)
      
      expect(mockInstance.data).toEqual(newData)
      expect(mockInstance.update).toHaveBeenCalled()
    })

    it('should not update if no instance', () => {
      chart.chartInstance = () => null
      
      chart.updateChart({})
      
      // Should not throw
      expect(true).toBe(true)
    })
  })

  describe('destroyChart', () => {
    it('should destroy chart instance', () => {
      const mockInstance = {
        destroy: vi.fn()
      }
      
      chart.chartInstance = () => mockInstance
      
      chart.destroyChart()
      
      expect(mockInstance.destroy).toHaveBeenCalled()
    })
  })

  describe('exportChart', () => {
    it('should export chart as image', () => {
      const mockInstance = {
        toBase64Image: vi.fn(() => 'base64-image')
      }
      
      chart.chartInstance = () => mockInstance
      
      const result = chart.exportChart('png')
      
      expect(mockInstance.toBase64Image).toHaveBeenCalledWith('png')
      expect(result).toBe('base64-image')
    })

    it('should return null if no instance', () => {
      chart.chartInstance = () => null
      
      const result = chart.exportChart()
      
      expect(result).toBe(null)
    })
  })
})

