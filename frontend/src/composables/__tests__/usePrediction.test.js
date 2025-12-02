/**
 * Unit tests for usePrediction composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePrediction } from '../usePrediction.js'
import { usePredictionStore } from '@/stores/prediction'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

// Mock dependencies
const mockStore = {
  hasPrediction: false,
  currentPrediction: null,
  currentImage: null,
  error: null,
  isLoading: false,
  setCurrentImage: vi.fn(),
  clearError: vi.fn()
}

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockStore
}))

vi.mock('@/services/predictionApi', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn()
}))

vi.mock('../useFileUpload', () => ({
  useFileUpload: () => ({
    selectedFile: { value: null },
    imagePreview: { value: null },
    hasFile: { value: false },
    selectFile: vi.fn().mockResolvedValue(true),
    removeSelectedFile: vi.fn()
  })
}))

describe('usePrediction', () => {
  let prediction

  beforeEach(() => {
    vi.clearAllMocks()
    prediction = usePrediction()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(prediction.isLoading.value).toBe(false)
      expect(prediction.error.value).toBe(null)
      expect(prediction.result.value).toBe(null)
    })

    it('should use default method', () => {
      expect(prediction.selectedMethod.value).toBe('traditional')
    })

    it('should accept custom method', () => {
      const customPrediction = usePrediction({ method: 'yolo' })
      expect(customPrediction.selectedMethod.value).toBe('yolo')
    })
  })

  describe('selectMethod', () => {
    it('should select valid method', () => {
      prediction.selectMethod('yolo')
      expect(prediction.selectedMethod.value).toBe('yolo')
    })

    it('should throw error for invalid method', () => {
      expect(() => prediction.selectMethod('invalid')).toThrow()
    })
  })

  describe('hasResult computed', () => {
    it('should return false when no result', () => {
      expect(prediction.hasResult.value).toBe(false)
    })

    it('should return true when result exists', () => {
      prediction.resultRef.value = { id: 1 }
      expect(prediction.hasResult.value).toBe(true)
    })
  })

  describe('mapApiResponseToPredictionData', () => {
    it('should map API response correctly', () => {
      const apiData = {
        id: 1,
        ancho_mm: 10.5,
        alto_mm: 12.3,
        grosor_mm: 5.2,
        peso_g: 25.5,
        nivel_confianza: 0.85
      }

      const mapped = prediction.mapApiResponseToPredictionData(apiData, 'traditional')

      expect(mapped.width).toBe(10.5)
      expect(mapped.height).toBe(12.3)
      expect(mapped.thickness).toBe(5.2)
      expect(mapped.confidence_level).toBe('high')
    })
  })
})

