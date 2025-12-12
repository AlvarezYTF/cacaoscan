/**
 * Unit tests for useAnalysis composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAnalysis } from '../useAnalysis.js'
import { predictImage, predictImageYolo } from '@/services/predictionApi'

// Mock dependencies
const mockStore = {
  currentPrediction: null,
  predictions: [],
  stats: {},
  isLoading: false,
  error: null,
  setCurrentPrediction: vi.fn(),
  setError: vi.fn()
}

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockStore
}))

vi.mock('@/services/predictionApi', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn()
}))

describe('useAnalysis', () => {
  let analysis

  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.currentPrediction = null
    mockStore.predictions = []
    analysis = useAnalysis()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(analysis.isAnalyzing.value).toBe(false)
      expect(analysis.analysisError.value).toBe(null)
      expect(analysis.currentBatch.value).toBe(null)
    })
  })

  describe('analyzeImage', () => {
    it('should analyze image with traditional method', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImage.mockResolvedValue(mockResult)
      
      const imageFile = new File([''], 'test.jpg')
      await analysis.analyzeImage(imageFile, 'traditional')

      expect(predictImage).toHaveBeenCalledWith(imageFile)
      expect(mockStore.setCurrentPrediction).toHaveBeenCalled()
      expect(analysis.isAnalyzing.value).toBe(false)
    })

    it('should analyze image with yolo method', async () => {
      const mockResult = { data: { peso_estimado: 30 } }
      predictImageYolo.mockResolvedValue(mockResult)
      
      const imageFile = new File([''], 'test.jpg')
      await analysis.analyzeImage(imageFile, 'yolo')

      expect(predictImageYolo).toHaveBeenCalledWith(imageFile)
    })

    it('should handle analysis error', async () => {
      const error = new Error('Analysis failed')
      predictImage.mockRejectedValue(error)
      
      const imageFile = new File([''], 'test.jpg')
      
      await expect(analysis.analyzeImage(imageFile)).rejects.toThrow()
      expect(analysis.analysisError.value).toBeTruthy()
      expect(analysis.isAnalyzing.value).toBe(false)
    })
  })

  describe('analyzeBatch', () => {
    it('should analyze batch of images', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImage.mockResolvedValue(mockResult)
      
      const images = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      const onProgress = vi.fn()
      
      const results = await analysis.analyzeBatch(images, 'traditional', onProgress)

      expect(results).toHaveLength(2)
      expect(onProgress).toHaveBeenCalledTimes(2)
      expect(analysis.isAnalyzing.value).toBe(false)
    })

    it('should handle errors in batch analysis', async () => {
      predictImage.mockRejectedValueOnce(new Error('Error 1'))
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImage.mockResolvedValueOnce(mockResult)
      
      const images = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      
      const results = await analysis.analyzeBatch(images)

      expect(results).toHaveLength(2)
      expect(results[0].error).toBeTruthy()
    })
  })

  describe('getAnalysisSummary', () => {
    it('should calculate summary from results', () => {
      const results = [
        { peso_estimado: 25.5, ancho_mm: 10, altura_mm: 12, grosor_mm: 5 },
        { peso_estimado: 30, ancho_mm: 12, altura_mm: 14, grosor_mm: 6 }
      ]
      
      const summary = analysis.getAnalysisSummary(results)

      expect(summary.total).toBe(2)
      expect(summary.avgWeight).toBeGreaterThan(0)
      expect(summary.avgDimensions.width).toBeGreaterThan(0)
    })

    it('should return empty summary for no results', () => {
      const summary = analysis.getAnalysisSummary([])

      expect(summary.total).toBe(0)
      expect(summary.avgWeight).toBe(0)
    })
  })
})

