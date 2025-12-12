/**
 * Unit tests for usePrediction composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { usePrediction } from '../usePrediction.js'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

// Mock dependencies
const mockStore = {
  hasPrediction: false,
  currentPrediction: null,
  currentImage: null,
  error: null,
  isLoading: false,
  setCurrentImage: vi.fn(),
  setCurrentPrediction: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  clearCurrentPrediction: vi.fn()
}

const mockFileUpload = {
  selectedFile: { value: null },
  imagePreview: { value: null },
  hasFile: { value: false },
  error: { value: '' },
  isDragging: { value: false },
  selectFile: vi.fn().mockResolvedValue(true),
  removeSelectedFile: vi.fn(),
  formatFileSize: vi.fn((bytes) => `${bytes} bytes`),
  openFileSelector: vi.fn(),
  handleDragOver: vi.fn(),
  handleDragLeave: vi.fn(),
  handleDrop: vi.fn()
}

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockStore
}))

vi.mock('@/services/predictionApi', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn()
}))

vi.mock('@/services/apiErrorHandler', () => ({
  handleApiError: vi.fn((err) => ({
    message: err.message || 'Error desconocido',
    type: 'unknown'
  }))
}))

vi.mock('../useFileUpload', () => ({
  useFileUpload: () => mockFileUpload
}))

describe('usePrediction', () => {
  let prediction

  beforeEach(() => {
    vi.clearAllMocks()
    mockStore.hasPrediction = false
    mockStore.currentPrediction = null
    mockStore.currentImage = null
    mockStore.error = null
    mockStore.isLoading = false
    mockFileUpload.selectedFile.value = null
    mockFileUpload.imagePreview.value = null
    mockFileUpload.hasFile.value = false
    mockFileUpload.error.value = ''
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

    it('should accept useStore option', () => {
      const noStorePrediction = usePrediction({ useStore: false })
      expect(noStorePrediction.store).toBe(null)
    })

    it('should accept custom fileUpload', () => {
      const customFileUpload = { ...mockFileUpload }
      const customPrediction = usePrediction({ fileUpload: customFileUpload })
      expect(customPrediction.fileUpload).toBe(customFileUpload)
    })
  })

  describe('selectMethod', () => {
    it('should select valid method', () => {
      prediction.selectMethod('yolo')
      expect(prediction.selectedMethod.value).toBe('yolo')
    })

    it('should select smart method', () => {
      prediction.selectMethod('smart')
      expect(prediction.selectedMethod.value).toBe('smart')
    })

    it('should select cacaoscan method', () => {
      prediction.selectMethod('cacaoscan')
      expect(prediction.selectedMethod.value).toBe('cacaoscan')
    })

    it('should clear error when selecting method', () => {
      prediction.error.value = 'Some error'
      prediction.selectMethod('yolo')
      expect(prediction.error.value).toBe(null)
      expect(mockStore.clearError).toHaveBeenCalled()
    })

    it('should throw error for invalid method', () => {
      expect(() => prediction.selectMethod('invalid')).toThrow('Invalid prediction method')
    })
  })

  describe('computed properties', () => {
    describe('hasResult', () => {
      it('should return false when no result', () => {
        expect(prediction.hasResult.value).toBe(false)
      })

      it('should return true when result exists', () => {
        prediction.resultRef.value = { id: 1 }
        expect(prediction.hasResult.value).toBe(true)
      })

      it('should return true when store has prediction', () => {
        mockStore.hasPrediction = true
        expect(prediction.hasResult.value).toBe(true)
      })

      it('should return false when useStore is false and no result', () => {
        const noStorePrediction = usePrediction({ useStore: false })
        expect(noStorePrediction.hasResult.value).toBe(false)
      })
    })

    describe('hasError', () => {
      it('should return false when no error', () => {
        expect(prediction.hasError.value).toBe(false)
      })

      it('should return true when error exists', () => {
        prediction.error.value = 'Error message'
        expect(prediction.hasError.value).toBe(true)
      })

      it('should return true when store has error', () => {
        mockStore.error = 'Store error'
        expect(prediction.hasError.value).toBe(true)
      })
    })

    describe('hasImage', () => {
      it('should return false when no image', () => {
        expect(prediction.hasImage.value).toBe(false)
      })

      it('should return true when file exists', () => {
        mockFileUpload.hasFile.value = true
        const newPrediction = usePrediction()
        expect(newPrediction.hasImage.value).toBe(true)
      })

      it('should return true when store has image', () => {
        mockStore.currentImage = 'image-url'
        const newPrediction = usePrediction()
        expect(newPrediction.hasImage.value).toBe(true)
      })
    })

    describe('loading', () => {
      it('should return false when not loading', () => {
        expect(prediction.loading.value).toBe(false)
      })

      it('should return true when loading', () => {
        prediction.isLoadingRef.value = true
        expect(prediction.loading.value).toBe(true)
      })

      it('should return true when store is loading', () => {
        mockStore.isLoading = true
        const newPrediction = usePrediction()
        expect(newPrediction.loading.value).toBe(true)
      })
    })

    describe('predictionResult', () => {
      it('should return null when no result', () => {
        expect(prediction.result.value).toBe(null)
      })

      it('should return result from ref', () => {
        prediction.resultRef.value = { id: 1 }
        expect(prediction.result.value).toEqual({ id: 1 })
      })

      it('should return result from store', () => {
        mockStore.currentPrediction = { id: 2 }
        const newPrediction = usePrediction()
        expect(newPrediction.result.value).toEqual({ id: 2 })
      })
    })
  })

  describe('setImage', () => {
    it('should set image file successfully', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.imagePreview.value = 'preview-url'
      
      await prediction.setImage(file)

      expect(mockFileUpload.selectFile).toHaveBeenCalledWith(file)
      expect(mockStore.setCurrentImage).toHaveBeenCalledWith('preview-url')
      expect(prediction.error.value).toBe(null)
    })

    it('should clear image when null is passed', async () => {
      await prediction.setImage(null)

      expect(mockFileUpload.removeSelectedFile).toHaveBeenCalled()
      expect(mockStore.setCurrentImage).toHaveBeenCalledWith(null)
    })

    it('should handle error when setting image', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const error = new Error('Invalid file')
      mockFileUpload.selectFile.mockRejectedValueOnce(error)

      await expect(prediction.setImage(file)).rejects.toThrow()
      expect(prediction.error.value).toBe('Invalid file')
      expect(mockFileUpload.error.value).toBe('Invalid file')
    })
  })

  describe('validateBeforeExecution', () => {
    it('should return invalid when no method selected', () => {
      prediction.selectedMethod.value = ''
      const result = prediction.validateBeforeExecution()
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('método de análisis')
    })

    it('should return invalid when no image', () => {
      mockFileUpload.hasFile.value = false
      mockStore.currentImage = null
      const result = prediction.validateBeforeExecution()
      expect(result.isValid).toBe(false)
      expect(result.error).toContain('subir una imagen')
    })

    it('should return valid when all conditions met', () => {
      mockFileUpload.hasFile.value = true
      const result = prediction.validateBeforeExecution()
      expect(result.isValid).toBe(true)
      expect(result.error).toBe(null)
    })

    it('should return valid when store has image', () => {
      mockStore.currentImage = 'image-url'
      const result = prediction.validateBeforeExecution()
      expect(result.isValid).toBe(true)
    })
  })

  describe('prepareFormData', () => {
    it('should return FormData when FormData is passed', () => {
      const formData = new FormData()
      const result = prediction.prepareFormData(formData)
      expect(result).toBe(formData)
    })

    it('should create FormData from File', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const result = prediction.prepareFormData(file)
      expect(result).toBeInstanceOf(FormData)
      expect(result.has('image')).toBe(true)
    })

    it('should use file from fileUpload when null passed', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      const result = prediction.prepareFormData(null)
      expect(result).toBeInstanceOf(FormData)
    })

    it('should use image from store when null passed', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockStore.currentImage = file
      const result = prediction.prepareFormData(null)
      expect(result).toBeInstanceOf(FormData)
    })

    it('should throw error when no image available', () => {
      expect(() => prediction.prepareFormData(null)).toThrow('No hay imagen disponible')
    })

    it('should throw error for unsupported image format', () => {
      mockStore.currentImage = 'string-url'
      expect(() => prediction.prepareFormData(null)).toThrow('Formato de imagen no soportado')
    })
  })

  describe('executePredictionApi', () => {
    it('should call predictImage for traditional method', async () => {
      prediction.selectedMethod.value = 'traditional'
      predictImage.mockResolvedValueOnce({ success: true, data: { id: 1 } })

      const result = await prediction.executePredictionApi(new FormData(), {})

      expect(predictImage).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('should call predictImageYolo for yolo method', async () => {
      prediction.selectedMethod.value = 'yolo'
      predictImageYolo.mockResolvedValueOnce({ success: true, data: { id: 1 } })

      const result = await prediction.executePredictionApi(new FormData(), {})

      expect(predictImageYolo).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('should call predictImageSmart for smart method', async () => {
      prediction.selectedMethod.value = 'smart'
      predictImageSmart.mockResolvedValueOnce({ success: true, data: { id: 1 } })

      const result = await prediction.executePredictionApi(new FormData(), {})

      expect(predictImageSmart).toHaveBeenCalled()
      expect(result.success).toBe(true)
    })

    it('should call cacaoscan method', async () => {
      prediction.selectedMethod.value = 'cacaoscan'
      const mockPredictImage = vi.fn().mockResolvedValue({ id: 1 })
      vi.doMock('@/services/api', () => ({
        predictImage: mockPredictImage
      }))

      const formData = new FormData()
      const result = await prediction.executePredictionApi(formData, {})

      expect(result).toBeDefined()
      expect(result.success).toBe(true)
    })
  })

  describe('executePrediction', () => {
    it('should execute prediction successfully', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      mockFileUpload.hasFile.value = true
      predictImage.mockResolvedValueOnce({
        success: true,
        data: {
          id: 1,
          ancho_mm: 10,
          alto_mm: 12,
          grosor_mm: 5,
          peso_g: 20
        }
      })

      await prediction.executePrediction()

      expect(prediction.isLoading.value).toBe(false)
      expect(prediction.resultRef.value).toBeTruthy()
      expect(mockStore.setCurrentPrediction).toHaveBeenCalled()
    })

    it('should handle validation error', async () => {
      prediction.selectedMethod.value = ''
      
      await expect(prediction.executePrediction()).rejects.toThrow()
      expect(prediction.error.value).toBeTruthy()
    })

    it('should handle API error', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      mockFileUpload.hasFile.value = true
      const error = new Error('API Error')
      predictImage.mockRejectedValueOnce(error)

      await expect(prediction.executePrediction()).rejects.toThrow()
      expect(prediction.error.value).toBeTruthy()
      expect(mockStore.setError).toHaveBeenCalled()
    })

    it('should call onSuccess callback', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      mockFileUpload.hasFile.value = true
      const onSuccess = vi.fn()
      const customPrediction = usePrediction({ onSuccess })
      customPrediction.selectedMethod.value = 'traditional'
      
      predictImage.mockResolvedValueOnce({
        success: true,
        data: { id: 1, ancho_mm: 10, alto_mm: 12, grosor_mm: 5, peso_g: 20 }
      })

      await customPrediction.executePrediction()
      expect(onSuccess).toHaveBeenCalled()
    })

    it('should call onError callback', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      mockFileUpload.hasFile.value = true
      const onError = vi.fn()
      const customPrediction = usePrediction({ onError, useStore: false })
      customPrediction.selectedMethod.value = 'traditional'
      
      // Clear any previous mock implementations
      predictImage.mockClear()
      const error = new Error('API Error')
      predictImage.mockRejectedValueOnce(error)

      try {
        await customPrediction.executePrediction()
        // If we reach here, the promise resolved instead of rejecting
        expect.fail('Expected executePrediction to reject')
      } catch (err) {
        // Promise rejected as expected
        expect(err).toBeDefined()
      }
      expect(onError).toHaveBeenCalled()
    })

    it('should handle API result without success flag', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      mockFileUpload.selectedFile.value = file
      mockFileUpload.hasFile.value = true
      predictImage.mockResolvedValueOnce({
        success: false,
        error: 'Prediction failed'
      })

      // The error will be processed by handleApiError, which returns err.message
      // So we expect the error message to be 'Prediction failed'
      await expect(prediction.executePrediction()).rejects.toThrow('Prediction failed')
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
      expect(mapped.predicted_weight).toBe(25.5)
      expect(mapped.confidence_level).toBe('high')
      expect(mapped.confidence_score).toBe(0.85)
    })

    it('should map with alternative field names', () => {
      const apiData = {
        id: 1,
        width: 10,
        height: 12,
        thickness: 5,
        predicted_weight: 20,
        confidence_score: 0.7
      }

      const mapped = prediction.mapApiResponseToPredictionData(apiData, 'yolo')

      expect(mapped.width).toBe(10)
      expect(mapped.height).toBe(12)
      expect(mapped.thickness).toBe(5)
      expect(mapped.predicted_weight).toBe(20)
    })

    it('should map confidence level correctly', () => {
      expect(prediction.mapApiResponseToPredictionData({ nivel_confianza: 0.9 }, 'traditional').confidence_level).toBe('high')
      expect(prediction.mapApiResponseToPredictionData({ nivel_confianza: 0.7 }, 'traditional').confidence_level).toBe('medium')
      expect(prediction.mapApiResponseToPredictionData({ nivel_confianza: 0.5 }, 'traditional').confidence_level).toBe('low')
      expect(prediction.mapApiResponseToPredictionData({ nivel_confianza: 0.6 }, 'traditional').confidence_level).toBe('medium')
    })

    it('should handle missing fields', () => {
      const mapped = prediction.mapApiResponseToPredictionData({ id: 1 }, 'traditional')
      expect(mapped.id).toBe(1)
      expect(mapped.confidence_level).toBe('unknown')
    })
  })

  describe('getMethodInfo', () => {
    it('should return info for traditional method', () => {
      const info = prediction.getMethodInfo('traditional')
      expect(info.title).toBe('Análisis Tradicional')
      expect(info.color).toBe('blue')
    })

    it('should return info for yolo method', () => {
      const info = prediction.getMethodInfo('yolo')
      expect(info.title).toBe('YOLOv8')
      expect(info.color).toBe('purple')
    })

    it('should return info for smart method', () => {
      const info = prediction.getMethodInfo('smart')
      expect(info.title).toBe('YOLOv8 + Recorte Inteligente')
      expect(info.color).toBe('green')
    })

    it('should return info for cacaoscan method', () => {
      const info = prediction.getMethodInfo('cacaoscan')
      expect(info.title).toBe('CacaoScan')
    })

    it('should use selectedMethod when no parameter', () => {
      prediction.selectedMethod.value = 'yolo'
      const info = prediction.getMethodInfo()
      expect(info.title).toBe('YOLOv8')
    })

    it('should return default for unknown method', () => {
      const info = prediction.getMethodInfo('unknown')
      expect(info.title).toBe('Análisis Tradicional')
    })
  })

  describe('isMethodAvailable', () => {
    it('should return true for valid methods', () => {
      expect(prediction.isMethodAvailable('traditional')).toBe(true)
      expect(prediction.isMethodAvailable('yolo')).toBe(true)
      expect(prediction.isMethodAvailable('smart')).toBe(true)
      expect(prediction.isMethodAvailable('cacaoscan')).toBe(true)
    })

    it('should return false for invalid methods', () => {
      expect(prediction.isMethodAvailable('invalid')).toBe(false)
    })

    it('should use selectedMethod when no parameter', () => {
      prediction.selectedMethod.value = 'yolo'
      expect(prediction.isMethodAvailable()).toBe(true)
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      prediction.selectedMethod.value = 'yolo'
      prediction.isLoading.value = true
      prediction.error.value = 'Error'
      prediction.resultRef.value = { id: 1 }
      prediction.processingTime.value = 1000

      prediction.reset()

      expect(prediction.selectedMethod.value).toBe('traditional')
      expect(prediction.isLoading.value).toBe(false)
      expect(prediction.error.value).toBe(null)
      expect(prediction.resultRef.value).toBe(null)
      expect(prediction.processingTime.value).toBe(0)
      expect(mockFileUpload.removeSelectedFile).toHaveBeenCalled()
      expect(mockStore.clearCurrentPrediction).toHaveBeenCalled()
    })

    it('should reset without store when useStore is false', () => {
      const noStorePrediction = usePrediction({ useStore: false })
      noStorePrediction.reset()
      expect(mockStore.clearCurrentPrediction).not.toHaveBeenCalled()
    })
  })

  describe('clearError', () => {
    it('should clear error', () => {
      prediction.error.value = 'Some error'
      prediction.clearError()
      expect(prediction.error.value).toBe(null)
      expect(mockStore.clearError).toHaveBeenCalled()
    })

    it('should not call store clearError when useStore is false', () => {
      const noStorePrediction = usePrediction({ useStore: false })
      noStorePrediction.clearError()
      expect(mockStore.clearError).not.toHaveBeenCalled()
    })
  })
})

