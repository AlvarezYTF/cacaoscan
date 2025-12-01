import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import * as predictionApi from '../predictionApi.js'
import api from '../api.js'

// Mock api service
vi.mock('../api.js', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn()
  }
}))

// Mock imageValidationUtils
vi.mock('@/utils/imageValidationUtils', () => ({
  validateImageFile: vi.fn(() => []),
  getImageValidationError: vi.fn(() => null)
}))

// Mock globalThis events
globalThis.dispatchEvent = vi.fn()

describe('Prediction API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('predictImage', () => {
    it('should successfully predict image', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockResponse = {
        data: {
          predicted_weight: 1.234,
          width: 10.5,
          height: 12.3,
          thickness: 5.2
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await predictionApi.predictImage(formData)

      expect(api.post).toHaveBeenCalledWith(
        '/scan/measure/',
        formData,
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000
        })
      )
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
      expect(globalThis.dispatchEvent).toHaveBeenCalled()
    })

    it('should throw error when FormData has no image', async () => {
      const formData = new FormData()

      const result = await predictionApi.predictImage(formData)
      expect(result.success).toBe(false)
      expect(result.error).toContain('No se ha proporcionado ninguna imagen para procesar')
    })

    it('should throw error when image file is empty', async () => {
      const file = new File([], 'empty.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const result = await predictionApi.predictImage(formData)
      expect(result.success).toBe(false)
      expect(result.error).toContain('El archivo de imagen está vacío o corrupto')
    })

    it('should handle API errors correctly', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockError = {
        response: {
          status: 500,
          data: { detail: 'Server error' }
        }
      }

      vi.mocked(api.post).mockRejectedValue(mockError)

      const result = await predictionApi.predictImage(formData)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error del servidor. Por favor intenta más tarde.')
    })

    it('should emit loading events', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      vi.mocked(api.post).mockResolvedValue({ data: {} })

      await predictionApi.predictImage(formData)

      expect(globalThis.dispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'api-loading-start',
          detail: expect.objectContaining({
            type: 'prediction',
            message: 'Analizando imagen de cacao...'
          })
        })
      )
    })
  })

  describe('predictImageYolo', () => {
    it('should successfully predict image with YOLOv8', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockResponse = {
        data: {
          predicted_weight: 1.234,
          width: 10.5,
          height: 12.3,
          thickness: 5.2,
          detection_count: 1
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const result = await predictionApi.predictImageYolo(formData)

      expect(api.post).toHaveBeenCalledWith(
        '/scan/measure/',
        formData,
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 120000
        })
      )
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })

    it('should handle YOLOv8 errors correctly', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockError = {
        response: {
          status: 500,
          data: { detail: 'YOLOv8 processing error' }
        }
      }

      vi.mocked(api.post).mockRejectedValue(mockError)

      const result = await predictionApi.predictImageYolo(formData)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error del servidor. Por favor intenta más tarde.')
    })
  })

  describe('predictImageSmart', () => {
    it('should successfully predict image with smart cropping', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      const mockResponse = {
        data: {
          predicted_weight: 1.234,
          width: 10.5,
          height: 12.3,
          thickness: 5.2,
          cropped_image: 'base64...'
        }
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      const options = {
        returnCroppedImage: true,
        returnTransparentImage: false
      }

      const result = await predictionApi.predictImageSmart(formData, options)

      expect(api.post).toHaveBeenCalledWith(
        '/scan/measure/',
        formData,
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 150000
        })
      )
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })

    it('should append options to FormData', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const formData = new FormData()
      formData.append('image', file)

      vi.mocked(api.post).mockResolvedValue({ data: {} })

      const options = {
        returnCroppedImage: true,
        returnTransparentImage: true
      }

      await predictionApi.predictImageSmart(formData, options)

      expect(formData.get('return_cropped_image')).toBe('true')
      expect(formData.get('return_transparent_image')).toBe('true')
    })
  })

  describe('getImages', () => {
    it('should fetch images list successfully', async () => {
      const mockResponse = {
        data: {
          results: [
            { id: 1, filename: 'test1.jpg', created_at: '2024-01-01' },
            { id: 2, filename: 'test2.jpg', created_at: '2024-01-02' }
          ],
          count: 2
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await predictionApi.getImages({ page: 1, page_size: 10 })

      expect(api.get).toHaveBeenCalledWith('/images/', {
        params: { page: 1, page_size: 10 }
      })
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })

    it('should handle errors when fetching images', async () => {
      const mockError = {
        response: {
          status: 500,
          data: { detail: 'Error fetching images' }
        }
      }

      vi.mocked(api.get).mockRejectedValue(mockError)

      const result = await predictionApi.getImages()

      expect(result.success).toBe(false)
      expect(result.error).toBe('Error del servidor. Por favor intenta más tarde.')
    })
  })

  describe('getImageDetails', () => {
    it('should fetch image details successfully', async () => {
      const imageId = 1
      const mockResponse = {
        data: {
          id: 1,
          filename: 'test.jpg',
          predicted_weight: 1.234,
          created_at: '2024-01-01'
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await predictionApi.getImageDetails(imageId)

      expect(api.get).toHaveBeenCalledWith(`/images/${imageId}/`, { params: {} })
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })

    it('should throw error when imageId is missing', async () => {
      const result = await predictionApi.getImageDetails(null)
      expect(result.success).toBe(false)
      expect(result.error).toContain('ID de imagen requerido')
    })
  })

  describe('deleteImage', () => {
    it('should delete image successfully', async () => {
      const imageId = 1

      vi.mocked(api.delete).mockResolvedValue({})

      const result = await predictionApi.deleteImage(imageId)

      expect(api.delete).toHaveBeenCalledWith(`/images/${imageId}/`, {})
      expect(result.success).toBe(true)
      expect(result.message).toBe('Imagen eliminada exitosamente')
    })

    it('should throw error when imageId is missing', async () => {
      const result = await predictionApi.deleteImage(null)
      expect(result.success).toBe(false)
      expect(result.error).toContain('ID de imagen requerido')
    })
  })

  describe('getStats', () => {
    it('should fetch prediction stats successfully', async () => {
      const mockResponse = {
        data: {
          total_predictions: 100,
          avg_quality: 85.5,
          avg_processing_time: 2.3
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      const result = await predictionApi.getStats({ date_from: '2024-01-01' })

      expect(api.get).toHaveBeenCalledWith('/images/stats/', {
        params: { date_from: '2024-01-01' }
      })
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })
  })

  describe('updateImageMetadata', () => {
    it('should update image metadata successfully', async () => {
      const imageId = 1
      const metadata = {
        lote_id: 5,
        notas: 'Test notes'
      }

      const mockResponse = {
        data: {
          id: 1,
          ...metadata
        }
      }

      vi.mocked(api.patch).mockResolvedValue(mockResponse)

      const result = await predictionApi.updateImageMetadata(imageId, metadata)

      expect(api.patch).toHaveBeenCalledWith(`/images/${imageId}/`, metadata, {})
      expect(result.success).toBe(true)
      expect(result.data).toEqual(mockResponse.data)
    })
  })

  describe('downloadImage', () => {
    it('should download image successfully', async () => {
      const imageId = 1
      const type = 'original'

      const blob = new Blob(['test'], { type: 'image/jpeg' })
      const mockResponse = {
        data: blob,
        headers: {
          'content-disposition': 'attachment; filename="test.jpg"'
        }
      }

      vi.mocked(api.get).mockResolvedValue(mockResponse)

      // Mock DOM methods
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue({
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      })
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockReturnValue(null)
      const removeSpy = vi.spyOn(document.body, 'removeChild').mockReturnValue(null)
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:url')
      globalThis.URL.revokeObjectURL = vi.fn()

      const result = await predictionApi.downloadImage(imageId, type)

      expect(api.get).toHaveBeenCalledWith(`/images/${imageId}/download/`, {
        params: { type },
        responseType: 'blob'
      })
      expect(result.success).toBe(true)

      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeSpy.mockRestore()
    })
  })

  describe('exportResults', () => {
    it('should export results successfully', async () => {
      const options = {
        format: 'csv',
        date_from: '2024-01-01'
      }

      const blob = new Blob(['csv,data'], { type: 'text/csv' })
      const mockResponse = {
        data: blob
      }

      vi.mocked(api.post).mockResolvedValue(mockResponse)

      // Mock DOM methods
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue({
        href: '',
        download: '',
        click: vi.fn(),
        remove: vi.fn()
      })
      const appendChildSpy = vi.spyOn(document.body, 'appendChild').mockReturnValue(null)
      const removeSpy = vi.spyOn(document.body, 'removeChild').mockReturnValue(null)
      globalThis.URL.createObjectURL = vi.fn(() => 'blob:url')
      globalThis.URL.revokeObjectURL = vi.fn()

      const result = await predictionApi.exportResults(options)

      expect(api.post).toHaveBeenCalledWith('/images/export/', options, {
        responseType: 'blob'
      })
      expect(result.success).toBe(true)

      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeSpy.mockRestore()
    })
  })

  describe('createImageFormData', () => {
    it('should create FormData with image and metadata', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const metadata = {
        lote_id: 5,
        finca: 1,
        region: 'Test Region',
        variedad: 'CCN-51',
        fecha_cosecha: '2024-01-01',
        notas: 'Test notes'
      }

      const formData = predictionApi.createImageFormData(file, metadata)

      expect(formData.get('image')).toBe(file)
      expect(formData.get('lote_id')).toBe('5')
      expect(formData.get('finca')).toBe('1')
      expect(formData.get('region')).toBe('Test Region')
      expect(formData.get('variedad')).toBe('CCN-51')
      expect(formData.get('fecha_cosecha')).toBe('2024-01-01')
      expect(formData.get('notas')).toBe('Test notes')
    })

    it('should create FormData with only image when no metadata', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      const formData = predictionApi.createImageFormData(file)

      expect(formData.get('image')).toBe(file)
      expect(formData.get('lote_id')).toBeNull()
    })
  })
})

