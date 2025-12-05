/**
 * Unit tests for useFileUpload composable
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useFileUpload } from '../useFileUpload.js'

// Mock imageValidationUtils
vi.mock('@/utils/imageValidationUtils', () => ({
  getImageValidationError: vi.fn(() => null)
}))

// Helper functions for FileReader mocks
function createSuccessFileReader() {
  return class {
    onload = null
    onerror = null
    readAsDataURL() {
      setTimeout(() => {
        if (this.onload) {
          this.onload({ target: { result: 'data:image/jpeg;base64,test' } })
        }
      }, 0)
    }
  }
}

function createErrorFileReader() {
  return class {
    onload = null
    onerror = null
    readAsDataURL() {
      setTimeout(() => {
        if (this.onerror) {
          this.onerror({ target: { error: { message: 'Read error' } } })
        }
      }, 0)
    }
  }
}

describe('useFileUpload', () => {
  let upload

  beforeEach(() => {
    vi.clearAllMocks()
    upload = useFileUpload()
  })

  describe('initial state', () => {
    it('should have initial state', () => {
      expect(upload.isDragging.value).toBe(false)
      expect(upload.selectedFile.value).toBe(null)
      expect(upload.imagePreview.value).toBe(null)
      expect(upload.error.value).toBe('')
      expect(upload.fileInput.value).toBe(null)
    })

    it('should compute hasFile correctly', () => {
      expect(upload.hasFile.value).toBe(false)
      
      upload.selectedFile.value = new File([''], 'test.jpg', { type: 'image/jpeg' })
      expect(upload.hasFile.value).toBe(true)
    })

    it('should compute canSubmit correctly', () => {
      expect(upload.canSubmit.value).toBe(false)
      
      upload.selectedFile.value = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.error.value = ''
      expect(upload.canSubmit.value).toBe(true)
    })

    it('should not allow submit when error exists', () => {
      upload.selectedFile.value = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.error.value = 'Validation error'
      expect(upload.canSubmit.value).toBe(false)
    })
  })

  describe('formatFileSize', () => {
    it('should format file size in bytes', () => {
      expect(upload.formatFileSize(512)).toContain('Bytes')
    })

    it('should format file size in KB', () => {
      expect(upload.formatFileSize(1024)).toContain('KB')
    })

    it('should format file size in MB', () => {
      expect(upload.formatFileSize(1024 * 1024)).toContain('MB')
    })

    it('should handle zero bytes', () => {
      expect(upload.formatFileSize(0)).toBe('0 Bytes')
    })
  })

  describe('handleDragOver', () => {
    it('should set isDragging to true', () => {
      const event = {
        preventDefault: vi.fn()
      }
      
      upload.handleDragOver(event)
      
      expect(event.preventDefault).toHaveBeenCalled()
      expect(upload.isDragging.value).toBe(true)
    })
  })

  describe('handleDragLeave', () => {
    it('should set isDragging to false when leaving area', () => {
      upload.isDragging.value = true
      const event = {
        preventDefault: vi.fn(),
        currentTarget: {
          contains: vi.fn(() => false)
        },
        relatedTarget: null
      }
      
      upload.handleDragLeave(event)
      
      expect(event.preventDefault).toHaveBeenCalled()
      expect(upload.isDragging.value).toBe(false)
    })

    it('should not change state when still in area', () => {
      upload.isDragging.value = true
      const event = {
        preventDefault: vi.fn(),
        currentTarget: {
          contains: vi.fn(() => true)
        },
        relatedTarget: {}
      }
      
      upload.handleDragLeave(event)
      
      expect(upload.isDragging.value).toBe(true)
    })
  })

  describe('removeSelectedFile', () => {
    it('should clear selected file and preview', () => {
      upload.selectedFile.value = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.imagePreview.value = 'preview-url'
      upload.error.value = 'Error'
      
      upload.removeSelectedFile()
      
      expect(upload.selectedFile.value).toBe(null)
      expect(upload.imagePreview.value).toBe(null)
      expect(upload.error.value).toBe('')
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      upload.selectedFile.value = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.imagePreview.value = 'preview-url'
      upload.isDragging.value = true
      upload.fileInput.value = { value: 'test' }
      
      upload.reset()
      
      expect(upload.selectedFile.value).toBe(null)
      expect(upload.imagePreview.value).toBe(null)
      expect(upload.isDragging.value).toBe(false)
    })

    it('should clear file input value if exists', () => {
      const mockInput = { value: 'test' }
      upload.fileInput.value = mockInput
      
      upload.reset()
      
      expect(mockInput.value).toBe('')
    })
  })

  describe('getFormData', () => {
    it('should create FormData with file', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.selectedFile.value = file
      
      const formData = upload.getFormData()
      
      expect(formData).toBeInstanceOf(FormData)
      expect(formData.get('image')).toBe(file)
    })

    it('should add metadata to FormData', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.selectedFile.value = file
      const metadata = { title: 'Test', description: 'Test image' }
      
      const formData = upload.getFormData(metadata)
      
      expect(formData.get('image')).toBe(file)
      expect(formData.get('title')).toBe('Test')
      expect(formData.get('description')).toBe('Test image')
    })

    it('should exclude null and empty metadata', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.selectedFile.value = file
      const metadata = { title: 'Test', empty: '', nullValue: null }
      
      const formData = upload.getFormData(metadata)
      
      expect(formData.get('title')).toBe('Test')
      expect(formData.has('empty')).toBe(false)
      expect(formData.has('nullValue')).toBe(false)
    })
  })

  describe('openFileSelector', () => {
    it('should click file input when available', () => {
      const mockClick = vi.fn()
      upload.fileInput.value = { click: mockClick }
      
      upload.openFileSelector()
      
      expect(mockClick).toHaveBeenCalled()
    })

    it('should not throw when file input is null', () => {
      upload.fileInput.value = null
      
      expect(() => upload.openFileSelector()).not.toThrow()
    })
  })

  describe('handleFileSelect', () => {
    it('should process selected file', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const event = {
        target: {
          files: [file],
          value: ''
        }
      }
      
      await upload.handleFileSelect(event)
      
      expect(upload.selectedFile.value).toBe(file)
      expect(event.target.value).toBe('')
    })

    it('should handle empty file list', async () => {
      const event = {
        target: {
          files: [],
          value: ''
        }
      }
      
      await upload.handleFileSelect(event)
      
      expect(upload.selectedFile.value).toBe(null)
    })
  })

  describe('processFile', () => {
    it('should process valid file successfully', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      
      const result = await upload.processFile(file)
      
      expect(result).toBe(true)
      expect(upload.selectedFile.value).toBe(file)
      expect(upload.error.value).toBe('')
    })

    it('should reject null file', async () => {
      const result = await upload.processFile(null)
      
      expect(result).toBe(false)
      expect(upload.error.value).toBe('Archivo requerido')
    })

    it('should handle validation error', async () => {
      const { getImageValidationError } = await import('@/utils/imageValidationUtils')
      getImageValidationError.mockReturnValueOnce('File too large')
      
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const result = await upload.processFile(file)
      
      expect(result).toBe(false)
      expect(upload.error.value).toBe('File too large')
    })

    it('should create preview when enabled', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      globalThis.FileReader = createSuccessFileReader()
      
      const result = await upload.processFile(file)
      
      expect(result).toBe(true)
      expect(upload.imagePreview.value).toBeTruthy()
    })

    it('should handle preview error gracefully', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      globalThis.FileReader = createErrorFileReader()
      
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const result = await upload.processFile(file)
      
      expect(result).toBe(true)
      expect(upload.imagePreview.value).toBe(null)
      expect(consoleWarn).toHaveBeenCalled()
      consoleWarn.mockRestore()
    })

    it('should not create preview when disabled', async () => {
      const uploadNoPreview = useFileUpload({ enablePreview: false })
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      
      const result = await uploadNoPreview.processFile(file)
      
      expect(result).toBe(true)
      expect(uploadNoPreview.imagePreview.value).toBe(null)
    })

    it('should not create preview for non-image files', async () => {
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      
      const result = await upload.processFile(file)
      
      expect(result).toBe(true)
      expect(upload.imagePreview.value).toBe(null)
    })
  })

  describe('handleDrop', () => {
    it('should process dropped file', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      const event = {
        preventDefault: vi.fn(),
        dataTransfer: {
          files: [file]
        }
      }
      
      await upload.handleDrop(event)
      
      expect(event.preventDefault).toHaveBeenCalled()
      expect(upload.isDragging.value).toBe(false)
      expect(upload.selectedFile.value).toBe(file)
    })

    it('should handle empty drop', async () => {
      const event = {
        preventDefault: vi.fn(),
        dataTransfer: {
          files: []
        }
      }
      
      await upload.handleDrop(event)
      
      expect(event.preventDefault).toHaveBeenCalled()
      expect(upload.isDragging.value).toBe(false)
    })
  })

  describe('createPreview', () => {
    it('should create preview for image file', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      globalThis.FileReader = createSuccessFileReader()
      
      const preview = await upload.processFile(file)
      expect(preview).toBe(true)
    })

    it('should reject preview on FileReader error', async () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      globalThis.FileReader = createErrorFileReader()
      
      const consoleWarn = vi.spyOn(console, 'warn').mockImplementation(() => {})
      await upload.processFile(file)
      consoleWarn.mockRestore()
    })

    it('should return null for non-image when preview disabled', async () => {
      const uploadNoPreview = useFileUpload({ enablePreview: false })
      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      
      const preview = await uploadNoPreview.processFile(file)
      expect(preview).toBe(true)
    })
  })

  describe('formatFileSize edge cases', () => {
    it('should format GB size', () => {
      expect(upload.formatFileSize(1024 * 1024 * 1024)).toContain('GB')
    })

    it('should handle very small sizes', () => {
      expect(upload.formatFileSize(1)).toContain('Bytes')
    })
  })

  describe('getFormData edge cases', () => {
    it('should return empty FormData when no file', () => {
      upload.selectedFile.value = null
      const formData = upload.getFormData()
      
      expect(formData).toBeInstanceOf(FormData)
      expect(formData.get('image')).toBe(null)
    })

    it('should exclude undefined metadata', () => {
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      upload.selectedFile.value = file
      const metadata = { title: 'Test', undefinedValue: undefined }
      
      const formData = upload.getFormData(metadata)
      
      expect(formData.get('title')).toBe('Test')
      expect(formData.has('undefinedValue')).toBe(false)
    })
  })
})

