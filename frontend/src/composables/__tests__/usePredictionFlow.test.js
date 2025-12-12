/**
 * Unit tests for usePredictionFlow composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { nextTick, reactive } from 'vue'
import { usePredictionFlow } from '../usePredictionFlow.js'
import { predictImage, predictImageYolo, predictImageSmart } from '@/services/predictionApi'

// Mock dependencies - using reactive to ensure computed properties update correctly
const mockStore = reactive({
  currentPrediction: null,
  currentImage: null,
  isLoading: false,
  error: null,
  uploadError: null,
  setCurrentImage: vi.fn(),
  setCurrentPrediction: vi.fn(),
  setError: vi.fn(),
  clearCurrentPrediction: vi.fn(),
  clearError: vi.fn()
})

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockStore
}))

vi.mock('@/services/predictionApi', () => ({
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn()
}))

// Mock FileReader
function createMockFileReader() {
  const instance = {
    readAsDataURL: vi.fn(function() {
      // Simulate async read completion
      setTimeout(() => {
        if (this.onload) {
          this.onload({ target: { result: 'data:image/jpeg;base64,test' } })
        }
      }, 0)
    }),
    onload: null,
    result: 'data:image/jpeg;base64,test'
  }
  return instance
}

globalThis.FileReader = vi.fn(createMockFileReader)

describe('usePredictionFlow', () => {
  let flow

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset FileReader mock
    globalThis.FileReader = vi.fn(createMockFileReader)
    flow = usePredictionFlow()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(flow.selectedMethod.value).toBe('traditional')
      expect(flow.imageFile.value).toBe(null)
      expect(flow.isExecuting.value).toBe(false)
    })
  })

  describe('selectMethod', () => {
    it('should select valid method', () => {
      flow.selectMethod('yolo')
      
      expect(flow.selectedMethod.value).toBe('yolo')
    })

    it('should throw error for invalid method', () => {
      expect(() => flow.selectMethod('invalid')).toThrow()
    })
  })

  describe('setImage', () => {
    it('should set valid image file', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      
      await flow.setImage(file)

      expect(flow.imageFile.value).toEqual(file)
      expect(globalThis.FileReader).toHaveBeenCalled()
      expect(globalThis.FileReader.mock.results.length).toBeGreaterThan(0)
      const readerInstance = globalThis.FileReader.mock.results[0]?.value
      expect(readerInstance).toBeDefined()
      expect(readerInstance.readAsDataURL).toHaveBeenCalledWith(file)
    })

    it('should reject invalid file type', async () => {
      const file = new File([''], 'test.pdf', { type: 'application/pdf' })
      
      await expect(flow.setImage(file)).rejects.toThrow()
    })
  })

  describe('validateBeforeExecution', () => {
    it('should validate correctly when ready', () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(true)
    })

    it('should fail validation without method', () => {
      flow.selectedMethod.value = null
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(false)
    })

    it('should fail validation without image', () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = null
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(false)
    })
  })

  describe('executePrediction', () => {
    it('should execute prediction successfully with traditional method', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImage.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await flow.executePrediction()
      
      expect(predictImage).toHaveBeenCalled()
      expect(mockStore.setCurrentPrediction).toHaveBeenCalledWith(mockResult.data)
      expect(flow.isExecuting.value).toBe(false)
    })

    it('should execute prediction with yolo method', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImageYolo.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'yolo'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await flow.executePrediction()
      
      expect(predictImageYolo).toHaveBeenCalled()
      expect(mockStore.setCurrentPrediction).toHaveBeenCalledWith(mockResult.data)
    })

    it('should execute prediction with smart method', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      predictImageSmart.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'smart'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await flow.executePrediction()
      
      expect(predictImageSmart).toHaveBeenCalled()
      expect(mockStore.setCurrentPrediction).toHaveBeenCalledWith(mockResult.data)
    })

    it('should execute prediction with store currentImage when imageFile is null', async () => {
      const mockResult = { data: { peso_estimado: 25.5 } }
      mockStore.currentImage = 'data:image/jpeg;base64,test'
      predictImage.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = null
      
      await flow.executePrediction()
      
      expect(predictImage).toHaveBeenCalledWith('data:image/jpeg;base64,test')
      expect(mockStore.setCurrentPrediction).toHaveBeenCalled()
    })

    it('should throw error when validation fails', async () => {
      flow.selectedMethod.value = null
      flow.imageFile.value = null
      
      await expect(flow.executePrediction()).rejects.toThrow('Debes seleccionar un método de análisis')
      expect(flow.executionError.value).toBe('Debes seleccionar un método de análisis')
    })

    it('should throw error when no image available', async () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = null
      mockStore.currentImage = null
      
      await expect(flow.executePrediction()).rejects.toThrow('No hay imagen disponible para analizar')
    })

    it('should handle prediction error with response data', async () => {
      const error = {
        response: {
          data: {
            detail: 'Prediction failed'
          }
        },
        message: 'Network error'
      }
      predictImage.mockRejectedValue(error)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await expect(flow.executePrediction()).rejects.toEqual(error)
      expect(flow.executionError.value).toBe('Prediction failed')
      expect(mockStore.setError).toHaveBeenCalledWith('Prediction failed')
    })

    it('should handle prediction error with message only', async () => {
      const error = {
        message: 'Network error'
      }
      predictImage.mockRejectedValue(error)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await expect(flow.executePrediction()).rejects.toEqual(error)
      expect(flow.executionError.value).toBe('Network error')
    })

    it('should handle prediction error with generic message', async () => {
      const error = {}
      predictImage.mockRejectedValue(error)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await expect(flow.executePrediction()).rejects.toEqual(error)
      expect(flow.executionError.value).toBe('Error al ejecutar la predicción')
    })

    it('should throw error for unsupported method', async () => {
      flow.selectedMethod.value = 'unsupported'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await expect(flow.executePrediction()).rejects.toThrow('Método de predicción no soportado: unsupported')
    })

    it('should handle result without data property', async () => {
      const mockResult = { peso_estimado: 25.5 }
      predictImage.mockResolvedValue(mockResult)
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = new File([''], 'test.jpg')
      
      await flow.executePrediction()
      
      expect(mockStore.setCurrentPrediction).toHaveBeenCalledWith(mockResult)
    })
  })

  describe('setImage', () => {
    it('should clear image when file is null', async () => {
      flow.imageFile.value = new File([''], 'test.jpg')
      flow.imagePreview.value = 'preview'
      
      await flow.setImage(null)
      
      expect(flow.imageFile.value).toBe(null)
      expect(flow.imagePreview.value).toBe(null)
      expect(mockStore.setCurrentImage).toHaveBeenCalledWith(null)
    })

    it('should reject file that is too large', async () => {
      const largeFile = new File(['x'.repeat(21 * 1024 * 1024)], 'test.jpg', { type: 'image/jpeg' })
      
      await expect(flow.setImage(largeFile)).rejects.toThrow('El archivo es demasiado grande')
    })

    it('should accept valid image types', async () => {
      const jpegFile = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const pngFile = new File([''], 'test.png', { type: 'image/png' })
      const webpFile = new File([''], 'test.webp', { type: 'image/webp' })
      
      await flow.setImage(jpegFile)
      expect(flow.imageFile.value).toEqual(jpegFile)
      
      await flow.setImage(pngFile)
      expect(flow.imageFile.value).toEqual(pngFile)
      
      await flow.setImage(webpFile)
      expect(flow.imageFile.value).toEqual(webpFile)
    })

    it('should clear execution error when setting image', async () => {
      flow.executionError.value = 'Previous error'
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      
      await flow.setImage(file)
      
      expect(flow.executionError.value).toBe(null)
    })
  })

  describe('validateBeforeExecution', () => {
    it('should validate with store currentImage', () => {
      flow.selectedMethod.value = 'traditional'
      flow.imageFile.value = null
      mockStore.currentImage = 'data:image/jpeg;base64,test'
      
      const validation = flow.validateBeforeExecution()
      
      expect(validation.isValid).toBe(true)
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      flow.selectedMethod.value = 'yolo'
      flow.imageFile.value = new File([''], 'test.jpg')
      flow.imagePreview.value = 'preview'
      flow.isExecuting.value = true
      flow.executionError.value = 'error'
      
      flow.reset()
      
      expect(flow.selectedMethod.value).toBe('traditional')
      expect(flow.imageFile.value).toBe(null)
      expect(flow.imagePreview.value).toBe(null)
      expect(flow.isExecuting.value).toBe(false)
      expect(flow.executionError.value).toBe(null)
      expect(mockStore.clearCurrentPrediction).toHaveBeenCalled()
      expect(mockStore.setCurrentImage).toHaveBeenCalledWith(null)
    })
  })

  describe('clearError', () => {
    it('should clear execution error and store error', () => {
      flow.executionError.value = 'execution error'
      mockStore.error = 'store error'
      
      flow.clearError()
      
      expect(flow.executionError.value).toBe(null)
      expect(mockStore.clearError).toHaveBeenCalled()
    })
  })

  describe('computed properties', () => {
    it('should compute predictionResult from store', () => {
      const prediction = { peso_estimado: 25.5 }
      mockStore.currentPrediction = prediction
      
      expect(flow.predictionResult.value).toEqual(prediction)
    })

    it('should compute loading from store and isExecuting', async () => {
      mockStore.isLoading = true
      flow.isExecuting.value = false
      await nextTick()
      expect(flow.loading.value).toBe(true)
      
      mockStore.isLoading = false
      flow.isExecuting.value = true
      await nextTick()
      expect(flow.loading.value).toBe(true)
      
      mockStore.isLoading = false
      flow.isExecuting.value = false
      await nextTick()
      expect(flow.loading.value).toBe(false)
    })

    it('should compute error from executionError, store error, and uploadError', async () => {
      flow.executionError.value = null
      mockStore.error = null
      mockStore.uploadError = null
      await nextTick()
      expect(flow.error.value).toBe(null)
      
      flow.executionError.value = 'execution error'
      await nextTick()
      expect(flow.error.value).toBe('execution error')
      
      flow.executionError.value = null
      mockStore.error = 'store error'
      await nextTick()
      expect(flow.error.value).toBe('store error')
      
      mockStore.error = null
      mockStore.uploadError = 'upload error'
      await nextTick()
      expect(flow.error.value).toBe('upload error')
    })

    it('should compute hasImage from imageFile or store currentImage', () => {
      flow.imageFile.value = null
      mockStore.currentImage = null
      expect(flow.hasImage.value).toBe(false)
      
      flow.imageFile.value = new File([''], 'test.jpg')
      expect(flow.hasImage.value).toBe(true)
      
      flow.imageFile.value = null
      mockStore.currentImage = 'data:image/jpeg;base64,test'
      expect(flow.hasImage.value).toBe(true)
    })

    it('should compute hasResult from predictionResult', async () => {
      // Reset to null first
      mockStore.currentPrediction = null
      await nextTick()
      expect(flow.hasResult.value).toBe(false)
      
      // Set prediction - now reactive, so computed should update
      mockStore.currentPrediction = { peso_estimado: 25.5 }
      await nextTick()
      expect(flow.hasResult.value).toBe(true)
    })
  })

  describe('getMethodInfo', () => {
    it('should return info for traditional method', () => {
      const info = flow.getMethodInfo('traditional')
      expect(info.title).toBe('Análisis Tradicional')
      expect(info.color).toBe('blue')
    })

    it('should return info for yolo method', () => {
      const info = flow.getMethodInfo('yolo')
      expect(info.title).toBe('YOLOv8')
      expect(info.color).toBe('purple')
    })

    it('should return info for smart method', () => {
      const info = flow.getMethodInfo('smart')
      expect(info.title).toBe('YOLOv8 + Recorte Inteligente')
      expect(info.color).toBe('green')
    })

    it('should return default info for unknown method', () => {
      const info = flow.getMethodInfo('unknown')
      expect(info.title).toBe('Análisis Tradicional')
    })
  })

  describe('isMethodAvailable', () => {
    it('should return true for valid methods', () => {
      expect(flow.isMethodAvailable('traditional')).toBe(true)
      expect(flow.isMethodAvailable('yolo')).toBe(true)
      expect(flow.isMethodAvailable('smart')).toBe(true)
    })

    it('should return false for invalid methods', () => {
      expect(flow.isMethodAvailable('invalid')).toBe(false)
      expect(flow.isMethodAvailable('')).toBe(false)
    })
  })

  describe('selectMethod', () => {
    it('should select all valid methods', () => {
      flow.selectMethod('traditional')
      expect(flow.selectedMethod.value).toBe('traditional')
      
      flow.selectMethod('yolo')
      expect(flow.selectedMethod.value).toBe('yolo')
      
      flow.selectMethod('smart')
      expect(flow.selectedMethod.value).toBe('smart')
    })

    it('should clear execution error when selecting method', () => {
      flow.executionError.value = 'Previous error'
      flow.selectMethod('yolo')
      expect(flow.executionError.value).toBe(null)
    })
  })
})

