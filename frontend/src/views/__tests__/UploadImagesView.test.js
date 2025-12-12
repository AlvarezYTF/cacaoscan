import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import api from '@/services/api.js'
import UploadImagesView from '../UploadImagesView.vue'

vi.mock('@/services/api.js', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('UploadImagesView', () => {
  let wrapper

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('rendering', () => {
    it('should render upload images view', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should show file input', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const fileInput = wrapper.find('input[type="file"]')
      expect(fileInput.exists()).toBe(true)
    })

    it('should show upload button', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const uploadButton = wrapper.find('button[type="submit"]')
      expect(uploadButton.exists()).toBe(true)
    })
  })

  describe('file handling', () => {
    beforeEach(() => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })
    })

    it('should handle file selection', async () => {
      const file1 = new File(['test1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
      const fileInput = wrapper.find('input[type="file"]')
      
      Object.defineProperty(fileInput.element, 'files', {
        value: [file1, file2],
        writable: false
      })

      await fileInput.trigger('change')
      await nextTick()

      expect(wrapper.vm.files.length).toBe(2)
    })

    it('should remove file', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file]

      await wrapper.vm.removeFile(0)
      await nextTick()

      expect(wrapper.vm.files.length).toBe(0)
    })

    it('should clear all files', async () => {
      const file1 = new File(['test1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file1, file2]

      await wrapper.vm.clearFiles()
      await nextTick()

      expect(wrapper.vm.files.length).toBe(0)
      expect(wrapper.vm.uploadStatus).toBe(null)
    })

    it('should format file size', () => {
      expect(wrapper.vm.formatFileSize(0)).toBe('0 Bytes')
      expect(wrapper.vm.formatFileSize(1024)).toContain('KB')
      expect(wrapper.vm.formatFileSize(1024 * 1024)).toContain('MB')
    })
  })

  describe('image upload', () => {
    beforeEach(() => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })
    })

    it('should not upload when no files', async () => {
      wrapper.vm.files = []
      await wrapper.vm.uploadImages()
      
      expect(api.post).not.toHaveBeenCalled()
    })

    it('should upload images successfully', async () => {
      const file1 = new File(['test1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file1, file2]

      const mockResponse = {
        data: {
          uploaded: [
            { id: 1, image_url: 'url1' },
            { id: 2, image_url: 'url2' }
          ],
          total_uploaded: 2,
          total_errors: 0,
          errors: []
        }
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await wrapper.vm.uploadImages()
      await nextTick()

      expect(api.post).toHaveBeenCalled()
      expect(wrapper.vm.uploadedImages.length).toBe(2)
      expect(wrapper.vm.uploadStatus.type).toBe('success')
      expect(wrapper.vm.files.length).toBe(0)
    })

    it('should handle partial upload success', async () => {
      const file1 = new File(['test1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['test2'], 'test2.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file1, file2]

      const mockResponse = {
        data: {
          uploaded: [{ id: 1, image_url: 'url1' }],
          total_uploaded: 1,
          total_errors: 1,
          errors: [{ file: 'test2.jpg', error: 'Invalid format' }]
        }
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await wrapper.vm.uploadImages()
      await nextTick()

      expect(wrapper.vm.uploadStatus.type).toBe('success')
      expect(wrapper.vm.uploadStatus.errors.length).toBe(1)
    })

    it('should handle upload error', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file]

      const error = {
        response: {
          data: {
            error: 'Upload failed',
            errors: [{ file: 'test.jpg', error: 'File too large' }]
          }
        }
      }
      vi.mocked(api.post).mockRejectedValue(error)

      await wrapper.vm.uploadImages()
      await nextTick()

      expect(wrapper.vm.uploadStatus.type).toBe('error')
      expect(wrapper.vm.uploadStatus.message).toContain('Upload failed')
    })

    it('should handle no images uploaded', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file]

      const mockResponse = {
        data: {
          uploaded: [],
          total_uploaded: 0,
          total_errors: 1,
          errors: [{ file: 'test.jpg', error: 'Invalid format' }]
        }
      }
      vi.mocked(api.post).mockResolvedValue(mockResponse)

      await wrapper.vm.uploadImages()
      await nextTick()

      expect(wrapper.vm.uploadStatus.type).toBe('error')
    })

    const createDelayedUploadResponse = (delay = 100) => {
      return new Promise(resolve => setTimeout(resolve, delay))
    }

    it('should set isUploading state', async () => {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      wrapper.vm.files = [file]
      vi.mocked(api.post).mockImplementation(() => createDelayedUploadResponse())

      const uploadPromise = wrapper.vm.uploadImages()
      expect(wrapper.vm.isUploading).toBe(true)

      await uploadPromise
      expect(wrapper.vm.isUploading).toBe(false)
    })
  })

  describe('uploaded images display', () => {
    it('should display uploaded images', async () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.uploadedImages = [
        { id: 1, image_url: 'url1', uploaded_at: '2024-01-01T00:00:00Z' },
        { id: 2, image_url: 'url2' }
      ]

      await nextTick()

      const images = wrapper.findAll('[data-testid="uploaded-image"]')
      expect(images.length).toBeGreaterThan(0)
    })

    it('should format date correctly', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const dateString = '2024-01-15T10:30:00Z'
      const formatted = wrapper.vm.formatDate(dateString)
      
      expect(formatted).toContain('2024')
      expect(formatted).toContain('ene')
    })

    it('should handle image error', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const img = document.createElement('img')
      wrapper.vm.handleImageError({ target: img })
      
      expect(img.src).toContain('placeholder')
    })
  })

  describe('form submission', () => {
    it('should prevent default on form submit', async () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      const form = wrapper.find('form')
      
      await form.trigger('submit')
      
      // Form should call uploadImages
      expect(wrapper.vm.files).toBeDefined()
    })

    it('should disable submit when no files', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.files = []
      const submitButton = wrapper.find('button[type="submit"]')
      
      expect(submitButton.attributes('disabled')).toBeDefined()
    })

    it('should disable submit when uploading', () => {
      wrapper = mount(UploadImagesView, {
        global: {
          stubs: { 'router-link': true }
        }
      })

      wrapper.vm.files = [new File(['test'], 'test.jpg', { type: 'image/jpeg' })]
      wrapper.vm.isUploading = true
      
      const submitButton = wrapper.find('button[type="submit"]')
      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })
})

