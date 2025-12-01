import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import * as datasetApi from '../datasetApi.js'

// Mock fetch
globalThis.fetch = vi.fn()

// Mock apiConfig
vi.mock('@/utils/apiConfig', () => ({
  getApiBaseUrlWithoutPath: vi.fn(() => 'https://test-api.example.com')
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(() => 'test-token'),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
globalThis.localStorage = localStorageMock

describe('Dataset API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue('test-token')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('getDatasetImages', () => {
    it('should fetch dataset images successfully', async () => {
      const mockResponse = {
        results: [
          { id: 1, filename: 'test1.jpg', quality_score: 85.5 },
          { id: 2, filename: 'test2.jpg', quality_score: 92 }
        ],
        count: 2
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.getDatasetImages({ quality: 'excellent' }, 1, 20)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/images/admin/images/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle errors when fetching images', async () => {
      globalThis.fetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: { get: () => 'application/json' },
        json: async () => ({ error: 'Server error' })
      })

      await expect(datasetApi.getDatasetImages()).rejects.toThrow()
    })
  })

  describe('getDatasetImage', () => {
    it('should fetch single image successfully', async () => {
      const imageId = 1
      const mockResponse = {
        id: 1,
        filename: 'test.jpg',
        quality_score: 85.5
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.getDatasetImage(imageId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/images/admin/images/${imageId}/`),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateDatasetImage', () => {
    it('should update image successfully', async () => {
      const imageId = 1
      const updateData = {
        quality_score: 90,
        notes: 'Updated notes'
      }

      const mockResponse = {
        id: 1,
        ...updateData
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.updateDatasetImage(imageId, updateData)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/images/admin/images/${imageId}/`),
        expect.objectContaining({
          method: 'PATCH',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token'
          }),
          body: JSON.stringify(updateData)
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteDatasetImage', () => {
    it('should delete image successfully', async () => {
      const imageId = 1

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' }
      })

      await datasetApi.deleteDatasetImage(imageId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/images/admin/images/${imageId}/`),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token'
          })
        })
      )
    })

    it('should throw error when deletion fails', async () => {
      const imageId = 1

      globalThis.fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      })

      await expect(datasetApi.deleteDatasetImage(imageId)).rejects.toThrow()
    })
  })

  describe('bulkUpdateDatasetImages', () => {
    it('should bulk update images successfully', async () => {
      const imageIds = [1, 2, 3]
      const updateData = {
        quality_score: 90
      }

      const mockResponse = {
        updated: 3,
        failed: 0
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.bulkUpdateDatasetImages(imageIds, updateData)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/images/admin/images/bulk-update/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            image_ids: imageIds,
            ...updateData
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('uploadDatasetImages', () => {
    it('should upload single image successfully', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const files = [file]
      const metadata = {
        lote_id: 5,
        region: 'Test Region'
      }

      const mockResponse = {
        id: 1,
        filename: 'test.jpg',
        upload_status: 'completed'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const onProgress = vi.fn()

      const results = await datasetApi.uploadDatasetImages(files, metadata, onProgress)

      expect(results).toHaveLength(1)
      expect(results[0].success).toBe(true)
      expect(results[0].file).toBe('test.jpg')
      expect(onProgress).toHaveBeenCalled()
    })

    it('should handle validation errors', async () => {
      const invalidFile = new File(['test'], 'test.txt', { type: 'text/plain' })
      const files = [invalidFile]

      const results = await datasetApi.uploadDatasetImages(files)

      expect(results).toHaveLength(1)
      expect(results[0].success).toBe(false)
      expect(results[0].error).toBeDefined()
    })

    it('should upload multiple images', async () => {
      const file1 = new File(['test1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
      const files = [file1, file2]

      const mockResponse = {
        id: 1,
        filename: 'test.jpg',
        upload_status: 'completed'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const results = await datasetApi.uploadDatasetImages(files)

      expect(results).toHaveLength(2)
      expect(globalThis.fetch).toHaveBeenCalledTimes(2)
    })
  })

  describe('validateImageFile', () => {
    it('should validate valid image file', () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

      const result = datasetApi.validateImageFile(file)

      expect(result.isValid).toBe(true)
    })

    it('should reject invalid file type', () => {
      const file = new File(['test'], 'test.txt', { type: 'text/plain' })

      const result = datasetApi.validateImageFile(file)

      expect(result.isValid).toBe(false)
      expect(result.error).toContain('Formato no soportado')
    })

    it('should reject file that is too large', () => {
      const largeFile = new File(['x'.repeat(25 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' })

      const result = datasetApi.validateImageFile(largeFile)

      expect(result.isValid).toBe(false)
      expect(result.error).toContain('demasiado grande')
    })
  })

  describe('getDatasetStats', () => {
    it('should fetch dataset stats successfully', async () => {
      const mockResponse = {
        total_images: 1000,
        total_size: 500000000,
        avg_quality: 85.5
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.getDatasetStats()

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/images/admin/images/admin-stats/'),
        expect.objectContaining({
          method: 'GET'
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('exportDatasetCSV', () => {
    it('should export CSV successfully', async () => {
      const filters = { quality: 'excellent' }
      const blob = new Blob(['csv,data'], { type: 'text/csv' })

      globalThis.fetch.mockResolvedValue({
        ok: true,
        blob: async () => blob
      })

      const result = await datasetApi.exportDatasetCSV(filters)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/images/admin/images/export-csv/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Accept': 'text/csv'
          })
        })
      )
      expect(result).toBeInstanceOf(Blob)
    })
  })

  describe('trainRegressionModel', () => {
    it('should start regression training successfully', async () => {
      const trainingParams = {
        epochs: 100,
        batch_size: 32
      }

      const mockResponse = {
        job_id: 'job-123',
        status: 'queued'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.trainRegressionModel(trainingParams)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/train/jobs/create/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            job_type: 'regression',
            ...trainingParams
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('trainVisionModel', () => {
    it('should start vision model training successfully', async () => {
      const trainingParams = {
        epochs: 50,
        batch_size: 16
      }

      const mockResponse = {
        job_id: 'job-456',
        status: 'queued'
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.trainVisionModel(trainingParams)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/train/jobs/create/'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            job_type: 'vision',
            ...trainingParams
          })
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getTrainingJobStatus', () => {
    it('should get training job status successfully', async () => {
      const jobId = 'job-123'
      const mockResponse = {
        status: 'running',
        progress: 50,
        epoch: 25
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.getTrainingJobStatus(jobId)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/train/jobs/${jobId}/status/`),
        expect.objectContaining({
          method: 'GET'
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getTrainingJobs', () => {
    it('should get list of training jobs successfully', async () => {
      const mockResponse = {
        results: [
          { id: 'job-1', status: 'completed' },
          { id: 'job-2', status: 'running' }
        ]
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.getTrainingJobs()

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/train/jobs/'),
        expect.objectContaining({
          method: 'GET'
        })
      )
      expect(result).toEqual(mockResponse.results)
    })
  })

  describe('validateDataIntegrity', () => {
    it('should validate data integrity successfully', async () => {
      const mockResponse = {
        valid: true,
        issues: [],
        total_checked: 1000
      }

      globalThis.fetch.mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => mockResponse
      })

      const result = await datasetApi.validateDataIntegrity()

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/images/admin/data/validate-integrity/'),
        expect.objectContaining({
          method: 'POST'
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Utility Functions', () => {
    describe('formatFileSize', () => {
      it('should format bytes correctly', () => {
        expect(datasetApi.formatFileSize(0)).toBe('0 Bytes')
        expect(datasetApi.formatFileSize(1024)).toContain('KB')
        expect(datasetApi.formatFileSize(1024 * 1024)).toContain('MB')
        expect(datasetApi.formatFileSize(1024 * 1024 * 1024)).toContain('GB')
      })
    })

    describe('formatNumber', () => {
      it('should format numbers correctly', () => {
        expect(datasetApi.formatNumber(123.456)).toBe('123.46')
        expect(datasetApi.formatNumber(123.456, 1)).toBe('123.5')
        expect(datasetApi.formatNumber(null)).toBe('N/A')
        expect(datasetApi.formatNumber(undefined)).toBe('N/A')
        expect(datasetApi.formatNumber(Number.NaN)).toBe('N/A')
      })
    })

    describe('getCommonFilters', () => {
      it('should return common filter options', () => {
        const filters = datasetApi.getCommonFilters()

        expect(filters.DATA_QUALITY).toBeDefined()
        expect(filters.PREDICTED_QUALITY).toBeDefined()
        expect(filters.DEFECT_TYPE).toBeDefined()
        expect(filters.PROCESSING_STATUS).toBeDefined()
      })
    })
  })

  describe('DATASET_CONFIG', () => {
    it('should export configuration constants', () => {
      expect(datasetApi.DATASET_CONFIG).toBeDefined()
      expect(datasetApi.DATASET_CONFIG.MAX_FILE_SIZE).toBe(20 * 1024 * 1024)
      expect(datasetApi.DATASET_CONFIG.MAX_BULK_OPERATIONS).toBe(100)
      expect(datasetApi.DATASET_CONFIG.SUPPORTED_FORMATS).toBeInstanceOf(Array)
      expect(datasetApi.DATASET_CONFIG.DEFAULT_PAGE_SIZE).toBe(20)
    })
  })
})

