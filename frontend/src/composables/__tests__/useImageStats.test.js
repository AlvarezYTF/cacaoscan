/**
 * Unit tests for useImageStats composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from '@/services/api'

// Mock dependencies
const mockAuthStore = {
  isAuthenticated: true
}

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

import { useImageStats } from '../useImageStats.js'

describe('useImageStats', () => {
  let imageStats

  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.isAuthenticated = true
    imageStats = useImageStats()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(imageStats.stats.value).toBe(null)
      expect(imageStats.loading.value).toBe(false)
      expect(imageStats.error.value).toBe(null)
    })
  })

  describe('fetchStats', () => {
    it('should fetch stats successfully', async () => {
      const mockStats = {
        total_images: 100,
        processed_images: 80,
        processing_rate: 0.8
      }
      axios.get.mockResolvedValue({ data: mockStats })

      await imageStats.fetchStats()

      expect(axios.get).toHaveBeenCalledWith('/api/v1/images/stats/')
      expect(imageStats.stats.value).toEqual(mockStats)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should handle 500 error gracefully', async () => {
      const error = {
        response: { status: 500 }
      }
      axios.get.mockRejectedValue(error)

      await imageStats.fetchStats()

      expect(imageStats.stats.value).toEqual({
        total_images: 0,
        processed_images: 0,
        processing_rate: 0,
        average_confidence: 0,
        average_dimensions: {},
        region_stats: [],
        top_fincas: []
      })
      expect(imageStats.error.value).toBe(null)
    })

    it('should require authentication', async () => {
      mockAuthStore.isAuthenticated = false

      await imageStats.fetchStats()

      expect(imageStats.error.value).toBe('Usuario no autenticado')
      expect(axios.get).not.toHaveBeenCalled()
    })
  })

  describe('fetchImages', () => {
    it('should fetch images successfully', async () => {
      const mockResponse = {
        data: {
          results: [{ id: 1 }],
          count: 1
        }
      }
      axios.get.mockResolvedValue(mockResponse)

      const result = await imageStats.fetchImages(1)

      expect(axios.get).toHaveBeenCalled()
      expect(result.count).toBe(1)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should return empty result if not authenticated', async () => {
      mockAuthStore.isAuthenticated = false

      const result = await imageStats.fetchImages()

      expect(result).toEqual({ results: [], count: 0, totalPages: 0 })
    })

    it('should handle 500 error gracefully', async () => {
      const error = {
        response: { status: 500 }
      }
      axios.get.mockRejectedValue(error)

      const result = await imageStats.fetchImages()

      expect(result).toEqual({ results: [], count: 0, totalPages: 0 })
      expect(imageStats.error.value).toBe(null)
    })

    it('should handle other errors', async () => {
      const error = {
        response: { status: 404, data: { error: 'Not found' } }
      }
      axios.get.mockRejectedValue(error)

      const result = await imageStats.fetchImages()

      expect(result).toEqual({ results: [], count: 0, totalPages: 0 })
      expect(imageStats.error.value).toBe('Not found')
    })

    it('should include filters in params', async () => {
      const mockResponse = {
        data: {
          results: [],
          count: 0
        }
      }
      axios.get.mockResolvedValue(mockResponse)

      await imageStats.fetchImages(1, { finca: 1, date_from: '2024-01-01' })

      expect(axios.get).toHaveBeenCalled()
      const callArgs = axios.get.mock.calls[0][0]
      expect(callArgs).toContain('finca=1')
      expect(callArgs).toContain('date_from=2024-01-01')
    })
  })

  describe('fetchReportStats', () => {
    it('should fetch report stats successfully', async () => {
      const mockStats = {
        total_reports: 10,
        generated_today: 5
      }
      axios.get.mockResolvedValue({ data: mockStats })

      const result = await imageStats.fetchReportStats({ period: '7d' })

      expect(axios.get).toHaveBeenCalled()
      expect(result).toEqual(mockStats)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should require authentication', async () => {
      mockAuthStore.isAuthenticated = false

      const result = await imageStats.fetchReportStats()

      expect(result).toBe(null)
      expect(axios.get).not.toHaveBeenCalled()
    })

    it('should handle 500 error gracefully', async () => {
      const error = {
        response: { status: 500 }
      }
      axios.get.mockRejectedValue(error)

      const result = await imageStats.fetchReportStats()

      expect(result).toBe(null)
      expect(imageStats.error.value).toBe(null)
    })

    it('should handle other errors', async () => {
      const error = {
        response: { status: 404, data: { error: 'Not found' } }
      }
      axios.get.mockRejectedValue(error)

      const result = await imageStats.fetchReportStats()

      expect(result).toBe(null)
      expect(imageStats.error.value).toBe('Not found')
    })
  })

  describe('generateReport', () => {
    beforeEach(() => {
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:url')
      globalThis.URL.revokeObjectURL = vi.fn()
      document.createElement = vi.fn(() => ({
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      }))
      document.body.appendChild = vi.fn()
    })

    it('should generate report successfully', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' })
      axios.post.mockResolvedValue({ data: mockBlob })

      const result = await imageStats.generateReport('images', { period: '7d' })

      expect(axios.post).toHaveBeenCalled()
      expect(result).toBe(true)
      expect(imageStats.loading.value).toBe(false)
    })

    it('should require authentication', async () => {
      mockAuthStore.isAuthenticated = false

      const result = await imageStats.generateReport('images')

      expect(result).toBe(false)
      expect(axios.post).not.toHaveBeenCalled()
    })

    it('should handle errors', async () => {
      const error = {
        response: { status: 500, data: { error: 'Server error' } }
      }
      axios.post.mockRejectedValue(error)

      const result = await imageStats.generateReport('images')

      expect(result).toBe(false)
      expect(imageStats.error.value).toBe('Server error')
    })
  })

  describe('computed properties', () => {
    it('should compute hasStats', () => {
      expect(imageStats.hasStats.value).toBe(false)
      
      imageStats.stats.value = { total_images: 10 }
      expect(imageStats.hasStats.value).toBe(true)
    })

    it('should compute totalImages', () => {
      imageStats.stats.value = { total_images: 100 }
      expect(imageStats.totalImages.value).toBe(100)
      
      imageStats.stats.value = null
      expect(imageStats.totalImages.value).toBe(0)
    })

    it('should compute processedImages', () => {
      imageStats.stats.value = { processed_images: 80 }
      expect(imageStats.processedImages.value).toBe(80)
      
      imageStats.stats.value = null
      expect(imageStats.processedImages.value).toBe(0)
    })

    it('should compute processingRate', () => {
      imageStats.stats.value = { processing_rate: 0.8 }
      expect(imageStats.processingRate.value).toBe(0.8)
      
      imageStats.stats.value = null
      expect(imageStats.processingRate.value).toBe(0)
    })

    it('should compute averageConfidence', () => {
      imageStats.stats.value = { average_confidence: 0.95 }
      expect(imageStats.averageConfidence.value).toBe(0.95)
      
      imageStats.stats.value = null
      expect(imageStats.averageConfidence.value).toBe(0)
    })

    it('should compute averageDimensions', () => {
      imageStats.stats.value = { average_dimensions: { width: 10, height: 20 } }
      expect(imageStats.averageDimensions.value).toEqual({ width: 10, height: 20 })
      
      imageStats.stats.value = null
      expect(imageStats.averageDimensions.value).toEqual({})
    })

    it('should compute regionStats', () => {
      imageStats.stats.value = { region_stats: [{ region: 'North', count: 10 }] }
      expect(imageStats.regionStats.value).toHaveLength(1)
      
      imageStats.stats.value = null
      expect(imageStats.regionStats.value).toEqual([])
    })

    it('should compute topFincas', () => {
      imageStats.stats.value = { top_fincas: [{ id: 1, name: 'Finca 1' }] }
      expect(imageStats.topFincas.value).toHaveLength(1)
      
      imageStats.stats.value = null
      expect(imageStats.topFincas.value).toEqual([])
    })
  })
})

