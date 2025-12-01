import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePredictionStore } from '../prediction.js'
import * as predictionApi from '@/services/predictionApi.js'

// Mock predictionApi
vi.mock('@/services/predictionApi.js', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn(),
  getImageHistory: vi.fn(),
  getPredictionStats: vi.fn()
}))

describe('Prediction Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = usePredictionStore()
    vi.clearAllMocks()
  })

  describe('State and Getters', () => {
    it('should have initial state', () => {
      expect(store.currentPrediction).toBe(null)
      expect(store.currentImage).toBe(null)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.predictions).toEqual([])
      expect(store.stats.totalPredictions).toBe(0)
    })

    it('should compute hasPrediction', () => {
      expect(store.hasPrediction).toBe(false)
      store.currentPrediction = { id: 1 }
      expect(store.hasPrediction).toBe(true)
    })

    it('should compute hasImage', () => {
      expect(store.hasImage).toBe(false)
      store.currentImage = new File(['test'], 'test.jpg')
      expect(store.hasImage).toBe(true)
    })

    it('should compute currentConfidenceLevel', () => {
      store.currentPrediction = { confidence_level: 'high' }
      expect(store.currentConfidenceLevel).toBe('high')
    })

    it('should compute currentConfidenceScore', () => {
      store.currentPrediction = { confidence_score: 0.85 }
      expect(store.currentConfidenceScore).toBe(85)
    })

    it('should compute isHighConfidence', () => {
      store.currentPrediction = { confidence_level: 'high' }
      expect(store.isHighConfidence).toBe(true)
      
      store.currentPrediction = { confidence_level: 'low' }
      expect(store.isHighConfidence).toBe(false)
    })

    it('should compute recentPredictions', () => {
      store.predictions = [
        { id: 1 },
        { id: 2 },
        { id: 3 },
        { id: 4 },
        { id: 5 },
        { id: 6 }
      ]

      const recent = store.recentPredictions
      expect(recent).toHaveLength(5)
    })

    it('should compute currentDimensions', () => {
      store.currentPrediction = {
        width: 10.5,
        height: 12.3,
        thickness: 5.2
      }

      const dimensions = store.currentDimensions
      expect(dimensions.width).toBe('10.50')
      expect(dimensions.height).toBe('12.30')
      expect(dimensions.thickness).toBe('5.20')
      expect(dimensions.formatted).toContain('10.50')
    })

    it('should compute currentWeight', () => {
      store.currentPrediction = {
        predicted_weight: 1.234
      }

      const weight = store.currentWeight
      expect(weight.value).toBe('1.234')
      expect(weight.formatted).toBe('1.234 g')
    })

    it('should compute hasActiveFilters', () => {
      expect(store.hasActiveFilters).toBe(false)
      store.filters.quality = 'excellent'
      expect(store.hasActiveFilters).toBe(true)
    })

    it('should compute quickStats', () => {
      store.predictions = [
        { predicted_weight: 1, confidence_score: 0.8 },
        { predicted_weight: 1.5, confidence_score: 0.9 }
      ]

      const stats = store.quickStats
      expect(stats.total).toBe(2)
      expect(stats.avgWeight).toBeDefined()
      expect(stats.avgConfidence).toBeDefined()
    })
  })

  describe('makePrediction', () => {
    it('should make prediction successfully', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockResult = {
        id: 1,
        predicted_weight: 1.234,
        width: 10.5,
        height: 12.3,
        thickness: 5.2
      }

      vi.mocked(predictionApi.predictImage).mockResolvedValue(mockResult)

      await store.makePrediction(formData)

      expect(predictionApi.predictImage).toHaveBeenCalledWith(formData, {})
      expect(store.currentPrediction).toEqual(mockResult)
      expect(store.predictions).toContainEqual(mockResult)
      expect(store.lastUpload.fileName).toBe('test.jpg')
      expect(store.isLoading).toBe(false)
    })

    it('should handle prediction errors', async () => {
      const formData = new FormData()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', file)

      const mockError = new Error('Prediction failed')
      vi.mocked(predictionApi.predictImage).mockRejectedValue(mockError)

      await expect(store.makePrediction(formData)).rejects.toThrow()
      expect(store.error).toBe('Prediction failed')
      expect(store.uploadError).toBe('Prediction failed')
      expect(store.isLoading).toBe(false)
    })

    it('should limit predictions history to 50', async () => {
      const formData = new FormData()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', file)

      // Fill predictions to 50
      store.predictions = Array.from({ length: 50 }, (_, i) => ({ id: i }))

      const mockResult = { id: 51 }
      vi.mocked(predictionApi.predictImage).mockResolvedValue(mockResult)

      await store.makePrediction(formData)

      expect(store.predictions).toHaveLength(50)
      expect(store.predictions[0].id).toBe(51)
    })
  })

  describe('makePredictionYolo', () => {
    it('should make YOLOv8 prediction successfully', async () => {
      const formData = new FormData()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', file)

      const mockResult = {
        success: true,
        data: {
          id: 1,
          predicted_weight: 1.234,
          detection_count: 1
        }
      }

      vi.mocked(predictionApi.predictImageYolo).mockResolvedValue(mockResult)

      await store.makePredictionYolo(formData)

      expect(predictionApi.predictImageYolo).toHaveBeenCalledWith(formData, {})
      expect(store.currentPrediction).toEqual(mockResult.data)
      expect(store.isLoading).toBe(false)
    })

    it('should handle YOLOv8 errors', async () => {
      const formData = new FormData()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', file)

      const mockResult = {
        success: false,
        error: 'YOLOv8 error'
      }

      vi.mocked(predictionApi.predictImageYolo).mockResolvedValue(mockResult)

      const result = await store.makePredictionYolo(formData)
      expect(result).toEqual(mockResult)
      expect(store.currentPrediction).toEqual(mockResult)
      expect(store.isLoading).toBe(false)
    })
  })

  describe('makePredictionSmart', () => {
    it('should make smart prediction successfully', async () => {
      const formData = new FormData()
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      formData.append('image', file)

      const options = {
        returnCroppedImage: true
      }

      const mockResult = {
        success: true,
        data: {
          id: 1,
          predicted_weight: 1.234,
          cropped_image: 'base64...'
        }
      }

      vi.mocked(predictionApi.predictImageSmart).mockResolvedValue(mockResult)

      await store.makePredictionSmart(formData, options)

      expect(predictionApi.predictImageSmart).toHaveBeenCalledWith(formData, options)
      expect(store.currentPrediction).toEqual(mockResult.data)
    })
  })

  describe('loadHistory', () => {
    it('should load prediction history successfully', async () => {
      const mockResponse = {
        results: [
          { id: 1, created_at: '2024-01-01' },
          { id: 2, created_at: '2024-01-02' }
        ],
        count: 2
      }

      vi.mocked(predictionApi.getImageHistory).mockResolvedValue(mockResponse)

      await store.loadHistory(1, {})

      expect(predictionApi.getImageHistory).toHaveBeenCalled()
      expect(store.predictions).toEqual(mockResponse.results)
      expect(store.pagination.totalItems).toBe(2)
    })

    it('should handle errors when loading history', async () => {
      const mockError = new Error('Failed to load history')
      vi.mocked(predictionApi.getImageHistory).mockRejectedValue(mockError)

      const result = await store.loadHistory(1)

      expect(result.results).toEqual([])
      expect(result.count).toBe(0)
    })
  })

  describe('loadStats', () => {
    it('should load prediction stats successfully', async () => {
      const mockStats = {
        total_predictions: 100,
        avg_quality: 85.5
      }

      vi.mocked(predictionApi.getPredictionStats).mockResolvedValue(mockStats)

      await store.loadStats()

      expect(predictionApi.getPredictionStats).toHaveBeenCalled()
      expect(store.stats).toMatchObject(mockStats)
    })
  })

  describe('updateResults', () => {
    it('should update current prediction results', () => {
      const predictionData = {
        id: 1,
        predicted_weight: 1.234
      }

      store.updateResults(predictionData)

      expect(store.currentPrediction).toEqual(predictionData)
      expect(store.error).toBe(null)
    })

    it('should add new prediction to history if not exists', () => {
      const predictionData = {
        id: 1,
        predicted_weight: 1.234
      }

      store.updateResults(predictionData)

      expect(store.predictions).toContainEqual(predictionData)
    })

    it('should update existing prediction in history', () => {
      store.predictions = [
        { id: 1, predicted_weight: 1 }
      ]

      const updatedData = {
        id: 1,
        predicted_weight: 1.234
      }

      store.updateResults(updatedData)

      expect(store.predictions[0].predicted_weight).toBe(1.234)
    })
  })

  describe('clearCurrentPrediction', () => {
    it('should clear current prediction and image', () => {
      store.currentPrediction = { id: 1 }
      store.currentImage = new File(['test'], 'test.jpg')
      store.error = 'Some error'
      store.uploadError = 'Upload error'

      store.clearCurrentPrediction()

      expect(store.currentPrediction).toBe(null)
      expect(store.currentImage).toBe(null)
      expect(store.error).toBe(null)
      expect(store.uploadError).toBe(null)
    })
  })

  describe('selectPrediction', () => {
    it('should select prediction from history', () => {
      store.predictions = [
        { id: 1, predicted_weight: 1 },
        { id: 2, predicted_weight: 1.5 }
      ]

      store.selectPrediction(1)

      expect(store.currentPrediction).toEqual({ id: 1, predicted_weight: 1 })
      expect(store.error).toBe(null)
    })

    it('should not select if prediction not found', () => {
      store.predictions = [
        { id: 1, predicted_weight: 1 }
      ]

      store.selectPrediction(999)

      expect(store.currentPrediction).toBe(null)
    })
  })

  describe('updateFilters', () => {
    it('should update filters', () => {
      const newFilters = {
        quality: 'excellent',
        dateFrom: '2024-01-01'
      }

      store.updateFilters(newFilters)

      expect(store.filters.quality).toBe('excellent')
      expect(store.filters.dateFrom).toBe('2024-01-01')
    })
  })

  describe('clearFilters', () => {
    it('should clear all filters', () => {
      store.filters = {
        processed: true,
        quality: 'excellent',
        batch: 'batch1',
        origin: 'origin1',
        dateFrom: '2024-01-01',
        dateTo: '2024-12-31'
      }

      store.clearFilters()

      expect(store.filters.processed).toBe(null)
      expect(store.filters.quality).toBe('')
      expect(store.filters.batch).toBe('')
      expect(store.filters.origin).toBe('')
      expect(store.filters.dateFrom).toBe('')
      expect(store.filters.dateTo).toBe('')
    })
  })

  describe('resetState', () => {
    it('should reset all state to initial values', () => {
      store.currentPrediction = { id: 1 }
      store.currentImage = new File(['test'], 'test.jpg')
      store.isLoading = true
      store.error = 'Error'
      store.predictions = [{ id: 1 }]
      store.stats.totalPredictions = 1

      store.resetState()

      expect(store.currentPrediction).toBe(null)
      expect(store.currentImage).toBe(null)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.predictions).toEqual([])
      expect(store.stats.totalPredictions).toBe(0)
    })
  })

  describe('removePrediction', () => {
    it('should remove prediction from history', () => {
      store.predictions = [
        { id: 1 },
        { id: 2 },
        { id: 3 }
      ]
      store.currentPrediction = { id: 2 }
      store.stats.totalPredictions = 3

      store.removePrediction(2)

      expect(store.predictions).toHaveLength(2)
      expect(store.currentPrediction).toBe(null)
      expect(store.stats.totalPredictions).toBe(2)
    })
  })

  describe('exportPrediction', () => {
    it('should export current prediction', () => {
      store.currentPrediction = {
        id: 1,
        created_at: '2024-01-01',
        width: 10.5,
        height: 12.3,
        thickness: 5.2,
        predicted_weight: 1.234,
        confidence_level: 'high',
        confidence_score: 0.85,
        prediction_method: 'yolo',
        processing_time: 2.3
      }

      const exportData = store.exportPrediction()

      expect(exportData.id).toBe(1)
      expect(exportData.peso_predicho).toContain('1.234')
      expect(exportData.confianza.nivel).toBe('high')
    })

    it('should export specific prediction by id', () => {
      store.predictions = [
        {
          id: 1,
          predicted_weight: 1
        },
        {
          id: 2,
          predicted_weight: 1.5
        }
      ]

      const exportData = store.exportPrediction(2)

      expect(exportData.id).toBe(2)
    })

    it('should return null if no prediction', () => {
      const exportData = store.exportPrediction()
      expect(exportData).toBe(null)
    })
  })

  describe('updateTodayStats', () => {
    it('should update today statistics', () => {
      const today = new Date()
      const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)

      store.predictions = [
        { created_at: today.toISOString(), processing_time: 2 },
        { created_at: today.toISOString(), processing_time: 3 },
        { created_at: yesterday.toISOString(), processing_time: 1 }
      ]

      store.updateTodayStats()

      expect(store.stats.predictionsToday).toBe(2)
      // avgProcessingTime is calculated from all predictions, not just today's
      expect(store.stats.avgProcessingTime).toBe(2) // (2 + 3 + 1) / 3 = 2
    })
  })

  describe('initialize', () => {
    it('should initialize store with data', async () => {
      const mockHistory = {
        results: [{ id: 1 }],
        count: 1
      }
      const mockStats = {
        total_predictions: 100
      }

      vi.mocked(predictionApi.getImageHistory).mockResolvedValue(mockHistory)
      vi.mocked(predictionApi.getPredictionStats).mockResolvedValue(mockStats)

      await store.initialize()

      expect(predictionApi.getImageHistory).toHaveBeenCalled()
      expect(predictionApi.getPredictionStats).toHaveBeenCalled()
      expect(store.predictions).toEqual(mockHistory.results)
    })
  })
})

