/**
 * Unit tests for useImageHandling composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useImageHandling } from '../useImageHandling.js'
import { isValidImageFile, validateImageSize, validateImageType } from '@/utils/imageValidationUtils'

// Mock dependencies
vi.mock('@/utils/imageValidationUtils', () => ({
  isValidImageFile: vi.fn(() => ({ isValid: true, error: null })),
  validateImageSize: vi.fn(() => ({ isValid: true, error: null })),
  validateImageType: vi.fn(() => ({ isValid: true, error: null }))
}))

// Mock FileReader
globalThis.FileReader = vi.fn(() => ({
  readAsDataURL: vi.fn(),
  onload: null,
  result: 'data:image/jpeg;base64,test'
}))

describe('useImageHandling', () => {
  let imageHandling

  beforeEach(() => {
    vi.clearAllMocks()
    imageHandling = useImageHandling()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(imageHandling.selectedImages.value).toEqual([])
      expect(imageHandling.imagePreviews.value).toEqual([])
      expect(imageHandling.uploadProgress.value).toBe(0)
      expect(imageHandling.isUploading.value).toBe(false)
    })

    it('should compute hasImages correctly', () => {
      expect(imageHandling.hasImages.value).toBe(false)
      
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      expect(imageHandling.hasImages.value).toBe(true)
    })
  })

  describe('validateImage', () => {
    it('should validate valid image', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const result = imageHandling.validateImage(file)
      
      expect(result.isValid).toBe(true)
    })

    it('should reject null file', () => {
      const result = imageHandling.validateImage(null)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBeTruthy()
    })
  })

  describe('addImages', () => {
    it('should add valid image', () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const result = imageHandling.addImages(file)
      
      expect(result.added).toHaveLength(1)
      expect(result.errors).toHaveLength(0)
    })

    it('should handle multiple files', () => {
      const files = [
        new File([''], 'test1.jpg', { type: 'image/jpeg' }),
        new File([''], 'test2.jpg', { type: 'image/jpeg' })
      ]
      const result = imageHandling.addImages(files)
      
      expect(result.added).toHaveLength(2)
    })
  })

  describe('navigation', () => {
    it('should navigate to next image', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      
      imageHandling.navigateNext()
      
      expect(imageHandling.currentImageIndex.value).toBe(1)
    })

    it('should navigate to previous image', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      imageHandling.currentImageIndex.value = 1
      
      imageHandling.navigatePrevious()
      
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })
  })

  describe('removeImage', () => {
    it('should remove image', () => {
      const file = new File([''], 'test.jpg')
      imageHandling.selectedImages.value = [file]
      
      imageHandling.removeImage(0)
      
      expect(imageHandling.selectedImages.value).toHaveLength(0)
    })
  })

  describe('clearImages', () => {
    it('should clear all images', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      
      imageHandling.clearImages()
      
      expect(imageHandling.selectedImages.value).toHaveLength(0)
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })

    it('should revoke blob URLs', () => {
      globalThis.URL.revokeObjectURL = vi.fn()
      imageHandling.imagePreviews.value = ['blob:url1', 'blob:url2']
      
      imageHandling.clearImages()
      
      expect(globalThis.URL.revokeObjectURL).toHaveBeenCalledTimes(2)
    })

    it('should not revoke non-blob URLs', () => {
      globalThis.URL.revokeObjectURL = vi.fn()
      imageHandling.imagePreviews.value = ['data:image/jpeg;base64,test']
      
      imageHandling.clearImages()
      
      expect(globalThis.URL.revokeObjectURL).not.toHaveBeenCalled()
    })
  })

  describe('validateImage', () => {
    it('should reject invalid type', () => {
      validateImageType.mockReturnValueOnce({ isValid: false, error: 'Invalid type' })
      const file = new File([''], 'test.txt', { type: 'text/plain' })
      
      const result = imageHandling.validateImage(file)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Invalid type')
    })

    it('should reject invalid size', () => {
      validateImageSize.mockReturnValueOnce({ isValid: false, error: 'File too large' })
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      
      const result = imageHandling.validateImage(file)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('File too large')
    })

    it('should reject invalid file', () => {
      isValidImageFile.mockReturnValueOnce({ isValid: false, error: 'Invalid file' })
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      
      const result = imageHandling.validateImage(file)
      
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Invalid file')
    })
  })

  describe('addImages', () => {
    it('should handle validation errors', () => {
      validateImageType.mockReturnValueOnce({ isValid: false, error: 'Invalid type' })
      const file = new File([''], 'test.txt', { type: 'text/plain' })
      
      const result = imageHandling.addImages(file)
      
      expect(result.added).toHaveLength(0)
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0].error).toBe('Invalid type')
    })

    it('should create preview for valid images', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockFileReader = {
        readAsDataURL: vi.fn(function() {
          this.onload({ target: { result: 'data:image/jpeg;base64,test' } })
        }),
        onload: null,
        result: 'data:image/jpeg;base64,test'
      }
      globalThis.FileReader = vi.fn(() => mockFileReader)
      
      const result = imageHandling.addImages(file)
      
      expect(result.added).toHaveLength(1)
    })
  })

  describe('createPreview', () => {
    it('should return null for null file', () => {
      const result = imageHandling.createPreview(null)
      
      expect(result).toBe(null)
    })

    it('should create preview URL', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockFileReader = {
        readAsDataURL: vi.fn(function() {
          setTimeout(() => {
            this.onload({ target: { result: 'data:image/jpeg;base64,test' } })
          }, 0)
        }),
        onload: null,
        onerror: null,
        result: 'data:image/jpeg;base64,test'
      }
      globalThis.FileReader = vi.fn(() => mockFileReader)
      
      const promise = imageHandling.createPreview(file)
      
      expect(promise).toBeInstanceOf(Promise)
    })

    it('should handle FileReader error', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockFileReader = {
        readAsDataURL: vi.fn(function() {
          setTimeout(() => {
            this.onerror(new Error('Read error'))
          }, 0)
        }),
        onload: null,
        onerror: null
      }
      globalThis.FileReader = vi.fn(() => mockFileReader)
      
      await expect(imageHandling.createPreview(file)).rejects.toThrow()
    })
  })

  describe('removeImage', () => {
    it('should handle out of bounds index', () => {
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      const initialLength = imageHandling.selectedImages.value.length
      
      imageHandling.removeImage(5)
      
      expect(imageHandling.selectedImages.value.length).toBe(initialLength)
    })

    it('should adjust current index when removing last image', () => {
      imageHandling.selectedImages.value = [
        new File([''], 'test1.jpg'),
        new File([''], 'test2.jpg')
      ]
      imageHandling.currentImageIndex.value = 1
      
      imageHandling.removeImage(1)
      
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })

    it('should revoke preview URL when removing', () => {
      globalThis.URL.revokeObjectURL = vi.fn()
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      imageHandling.imagePreviews.value = ['blob:url']
      
      imageHandling.removeImage(0)
      
      expect(globalThis.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url')
    })
  })

  describe('navigation edge cases', () => {
    it('should not navigate previous if at first', () => {
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      imageHandling.currentImageIndex.value = 0
      
      imageHandling.previousImage()
      
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })

    it('should not navigate next if at last', () => {
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      imageHandling.currentImageIndex.value = 0
      
      imageHandling.nextImage()
      
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })

    it('should not set invalid index', () => {
      imageHandling.selectedImages.value = [new File([''], 'test.jpg')]
      
      imageHandling.setCurrentImageIndex(-1)
      expect(imageHandling.currentImageIndex.value).toBe(0)
      
      imageHandling.setCurrentImageIndex(5)
      expect(imageHandling.currentImageIndex.value).toBe(0)
    })
  })

  describe('uploadImages', () => {
    it('should throw error if no upload function', async () => {
      await expect(imageHandling.uploadImages(null)).rejects.toThrow('Upload function is required')
    })

    it('should throw error if no images', async () => {
      const uploadFn = vi.fn()
      
      await expect(imageHandling.uploadImages(uploadFn)).rejects.toThrow('No images to upload')
    })

    it('should upload multiple images with progress', async () => {
      const file1 = new File([''], 'test1.jpg')
      const file2 = new File([''], 'test2.jpg')
      imageHandling.selectedImages.value = [file1, file2]
      
      const uploadFn = vi.fn().mockResolvedValue({ success: true })
      
      const results = await imageHandling.uploadImages(uploadFn)
      
      expect(uploadFn).toHaveBeenCalledTimes(2)
      expect(results).toHaveLength(2)
      expect(imageHandling.uploadProgress.value).toBe(100)
      expect(imageHandling.isUploading.value).toBe(false)
    })

    it('should handle upload errors', async () => {
      const file = new File([''], 'test.jpg')
      imageHandling.selectedImages.value = [file]
      
      const uploadFn = vi.fn().mockRejectedValue(new Error('Upload failed'))
      
      const results = await imageHandling.uploadImages(uploadFn)
      
      expect(results[0].success).toBe(false)
      expect(results[0].error).toBe('Upload failed')
    })

    it('should track upload progress', async () => {
      const file = new File([''], 'test.jpg')
      imageHandling.selectedImages.value = [file]
      
      let progressCallback
      const uploadFn = vi.fn((file, onProgress) => {
        progressCallback = onProgress
        return Promise.resolve({ success: true })
      })
      
      const uploadPromise = imageHandling.uploadImages(uploadFn)
      
      // Simulate progress
      progressCallback(50)
      
      await uploadPromise
      
      expect(imageHandling.uploadProgress.value).toBe(100)
    })
  })

  describe('getImageDimensions', () => {
    it('should get dimensions from URL string', async () => {
      const mockImage = {
        width: 800,
        height: 600,
        onload: null,
        onerror: null,
        src: ''
      }
      globalThis.Image = vi.fn(() => mockImage)
      
      const promise = imageHandling.getImageDimensions('http://example.com/image.jpg')
      
      mockImage.onload()
      
      const result = await promise
      
      expect(result.width).toBe(800)
      expect(result.height).toBe(600)
    })

    it('should get dimensions from File', async () => {
      const file = new File([''], 'test.jpg', { type: 'image/jpeg' })
      const mockImage = {
        width: 800,
        height: 600,
        onload: null,
        onerror: null,
        src: ''
      }
      globalThis.Image = vi.fn(() => mockImage)
      
      const mockFileReader = {
        readAsDataURL: vi.fn(function() {
          this.onload({ target: { result: 'data:image/jpeg;base64,test' } })
        }),
        onload: null,
        onerror: null
      }
      globalThis.FileReader = vi.fn(() => mockFileReader)
      
      const promise = imageHandling.getImageDimensions(file)
      
      mockImage.onload()
      
      const result = await promise
      
      expect(result.width).toBe(800)
      expect(result.height).toBe(600)
    })

    it('should handle image load error', async () => {
      const mockImage = {
        onload: null,
        onerror: null,
        src: ''
      }
      globalThis.Image = vi.fn(() => mockImage)
      
      const promise = imageHandling.getImageDimensions('http://example.com/image.jpg')
      
      mockImage.onerror(new Error('Load error'))
      
      await expect(promise).rejects.toThrow()
    })

    it('should reject invalid image source', async () => {
      await expect(imageHandling.getImageDimensions(123)).rejects.toThrow('Invalid image source')
    })
  })

  describe('computed properties', () => {
    it('should compute currentImage', () => {
      const file1 = new File([''], 'test1.jpg')
      const file2 = new File([''], 'test2.jpg')
      imageHandling.selectedImages.value = [file1, file2]
      imageHandling.currentImageIndex.value = 1
      
      expect(imageHandling.currentImage.value).toBe(file2)
    })

    it('should return null for currentImage if no images', () => {
      expect(imageHandling.currentImage.value).toBe(null)
    })

    it('should compute currentPreview', () => {
      imageHandling.imagePreviews.value = ['preview1', 'preview2']
      imageHandling.currentImageIndex.value = 1
      
      expect(imageHandling.currentPreview.value).toBe('preview2')
    })

    it('should return null for currentPreview if no previews', () => {
      expect(imageHandling.currentPreview.value).toBe(null)
    })
  })
})

