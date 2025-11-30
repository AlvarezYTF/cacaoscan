import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAnalysisStore } from '../analysis'
import api from '@/services/api'

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('useAnalysisStore', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAnalysisStore()
    vi.clearAllMocks()
  })

  describe('State', () => {
    it('should have initial state', () => {
      expect(store.batch.name).toBe('')
      expect(store.batch.collectionDate).toBe('')
      expect(store.images).toEqual([])
      expect(store.uploadProgress).toBe(0)
      expect(store.isUploading).toBe(false)
      expect(store.uploadError).toBe(null)
    })
  })

  describe('Getters', () => {
    it('should return false for hasImages when no images', () => {
      expect(store.hasImages).toBe(false)
    })

    it('should return true for hasImages when images exist', () => {
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      expect(store.hasImages).toBe(true)
    })

    it('should return false for isValid when batch is incomplete', () => {
      expect(store.isValid).toBe(false)
    })

    it('should return true for isValid when batch is complete', () => {
      store.batch = {
        name: 'Batch 1',
        collectionDate: '2024-01-01',
        farm: '1',
        genetics: 'Criollo',
        origin: '',
        notes: '',
        originPlace: '',
        farmer: ''
      }
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      expect(store.isValid).toBe(true)
    })
  })

  describe('Actions', () => {
    it('should set batch data', () => {
      const data = { name: 'Batch 1', collectionDate: '2024-01-01' }
      store.setBatchData(data)

      expect(store.batch.name).toBe('Batch 1')
      expect(store.batch.collectionDate).toBe('2024-01-01')
    })

    it('should merge batch data', () => {
      store.batch.name = 'Original'
      store.setBatchData({ collectionDate: '2024-01-01' })

      expect(store.batch.name).toBe('Original')
      expect(store.batch.collectionDate).toBe('2024-01-01')
    })

    it('should add valid images', () => {
      const image1 = new File([''], 'test1.jpg', { type: 'image/jpeg' })
      const image2 = new File([''], 'test2.png', { type: 'image/png' })
      const invalidFile = new File([''], 'test.txt', { type: 'text/plain' })

      const count = store.addImages([image1, image2, invalidFile])

      expect(store.images).toHaveLength(2)
      expect(count).toBe(2)
      expect(store.images).toContain(image1)
      expect(store.images).toContain(image2)
      expect(store.images).not.toContain(invalidFile)
    })

    it('should remove image by index', () => {
      const image1 = new File([''], 'test1.jpg', { type: 'image/jpeg' })
      const image2 = new File([''], 'test2.jpg', { type: 'image/jpeg' })
      store.images = [image1, image2]

      store.removeImage(0)

      expect(store.images).toHaveLength(1)
      expect(store.images[0]).toBe(image2)
    })

    it('should clear batch', () => {
      store.batch.name = 'Batch 1'
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      store.uploadProgress = 50
      store.uploadError = 'Error'

      store.clearBatch()

      expect(store.batch.name).toBe('')
      expect(store.images).toEqual([])
      expect(store.uploadProgress).toBe(0)
      expect(store.uploadError).toBe(null)
    })

    it('should submit batch successfully', async () => {
      store.batch = {
        name: 'Batch 1',
        collectionDate: '2024-01-01',
        farm: '1',
        genetics: 'Criollo',
        origin: '',
        notes: '',
        originPlace: '',
        farmer: ''
      }
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      
      const mockResponse = {
        data: { id: 1, success: true }
      }
      api.post.mockResolvedValue(mockResponse)

      const result = await store.submitBatch()

      expect(api.post).toHaveBeenCalledWith('/analysis/batch/', expect.any(FormData), {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 120000,
        onUploadProgress: expect.any(Function)
      })
      expect(result).toEqual(mockResponse.data)
      expect(store.isUploading).toBe(false)
    })

    it('should not submit if batch is invalid', async () => {
      store.batch.name = ''
      store.images = []

      const result = await store.submitBatch()

      expect(api.post).not.toHaveBeenCalled()
      expect(result).toBe(false)
    })

    it('should not submit if already uploading', async () => {
      store.batch = {
        name: 'Batch 1',
        collectionDate: '2024-01-01',
        farm: '1',
        genetics: 'Criollo',
        origin: '',
        notes: '',
        originPlace: '',
        farmer: ''
      }
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      store.isUploading = true

      const result = await store.submitBatch()

      expect(api.post).not.toHaveBeenCalled()
      expect(result).toBe(false)
    })

    it('should handle upload error', async () => {
      store.batch = {
        name: 'Batch 1',
        collectionDate: '2024-01-01',
        farm: '1',
        genetics: 'Criollo',
        origin: '',
        notes: '',
        originPlace: '',
        farmer: ''
      }
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      
      const error = {
        response: {
          data: {
            error: 'Upload failed'
          }
        }
      }
      api.post.mockRejectedValue(error)

      await expect(store.submitBatch()).rejects.toThrow('Upload failed')
      expect(store.uploadError).toBe('Upload failed')
      expect(store.isUploading).toBe(false)
    })

    it('should update upload progress', async () => {
      store.batch = {
        name: 'Batch 1',
        collectionDate: '2024-01-01',
        farm: '1',
        genetics: 'Criollo',
        origin: '',
        notes: '',
        originPlace: '',
        farmer: ''
      }
      store.images = [new File([''], 'test.jpg', { type: 'image/jpeg' })]
      
      const mockResponse = {
        data: { id: 1, success: true }
      }
      api.post.mockImplementation((url, data, config) => {
        // Simulate progress
        if (config.onUploadProgress) {
          config.onUploadProgress({ loaded: 50, total: 100 })
        }
        return Promise.resolve(mockResponse)
      })

      await store.submitBatch()

      expect(store.uploadProgress).toBe(50)
    })
  })
})

