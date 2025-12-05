/**
 * Unit tests for useDataset composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDataset } from '../useDataset.js'
import { getDatasetImages, getDatasetImage, updateDatasetImage, deleteDatasetImage } from '@/services/datasetApi'

// Mock dependencies
vi.mock('@/services/datasetApi', () => ({
  getDatasetImages: vi.fn(),
  getDatasetImage: vi.fn(),
  updateDatasetImage: vi.fn(),
  deleteDatasetImage: vi.fn()
}))

vi.mock('@/services/apiErrorHandler', () => ({
  handleApiError: vi.fn((error) => ({
    message: error.message || 'Error'
  }))
}))

describe('useDataset', () => {
  let dataset

  beforeEach(() => {
    vi.clearAllMocks()
    dataset = useDataset()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(dataset.images.value).toEqual([])
      expect(dataset.currentImage.value).toBe(null)
      expect(dataset.isLoading.value).toBe(false)
      expect(dataset.error.value).toBe(null)
    })
  })

  describe('loadImages', () => {
    it('should load images successfully', async () => {
      const mockResponse = {
        results: [{ id: 1, url: 'image1.jpg' }],
        count: 1
      }
      getDatasetImages.mockResolvedValue(mockResponse)

      await dataset.loadImages()

      expect(getDatasetImages).toHaveBeenCalled()
      expect(dataset.images.value).toEqual([{ id: 1, url: 'image1.jpg' }])
      expect(dataset.isLoading.value).toBe(false)
    })

    it('should handle error', async () => {
      const error = new Error('Network error')
      getDatasetImages.mockRejectedValue(error)

      await expect(dataset.loadImages()).rejects.toThrow()

      expect(dataset.error.value).toBeTruthy()
    })
  })

  describe('loadImage', () => {
    it('should load single image', async () => {
      const mockImage = { id: 1, url: 'image1.jpg' }
      getDatasetImage.mockResolvedValue(mockImage)

      await dataset.loadImage(1)

      expect(getDatasetImage).toHaveBeenCalledWith(1)
      expect(dataset.currentImage.value).toEqual(mockImage)
    })
  })

  describe('updateImage', () => {
    it('should update image successfully', async () => {
      const imageData = { id: 1, quality: 0.95 }
      updateDatasetImage.mockResolvedValue(imageData)
      const onImageUpdate = vi.fn()

      const datasetWithCallback = useDataset({ onImageUpdate })
      await datasetWithCallback.updateImage(1, imageData)

      expect(updateDatasetImage).toHaveBeenCalledWith(1, imageData)
      expect(onImageUpdate).toHaveBeenCalled()
    })
  })

  describe('deleteImage', () => {
    it('should delete image successfully', async () => {
      deleteDatasetImage.mockResolvedValue()
      const onImageDelete = vi.fn()

      const datasetWithCallback = useDataset({ onImageDelete })
      await datasetWithCallback.deleteImage(1)

      expect(deleteDatasetImage).toHaveBeenCalledWith(1)
      expect(onImageDelete).toHaveBeenCalled()
    })
  })
})

