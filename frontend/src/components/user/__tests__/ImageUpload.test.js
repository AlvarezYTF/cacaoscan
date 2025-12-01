import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import ImageUpload from '../ImageUpload.vue'

// Mock predictionApi
const mockPredictionApi = {
  predictImage: vi.fn(),
  predictImageYolo: vi.fn(),
  predictImageSmart: vi.fn(),
  createImageFormData: vi.fn(),
  validateImageFile: vi.fn()
}

vi.mock('@/services/predictionApi.js', () => ({
  predictImage: (...args) => mockPredictionApi.predictImage(...args),
  predictImageYolo: (...args) => mockPredictionApi.predictImageYolo(...args),
  predictImageSmart: (...args) => mockPredictionApi.predictImageSmart(...args),
  createImageFormData: (...args) => mockPredictionApi.createImageFormData(...args),
  validateImageFile: (...args) => mockPredictionApi.validateImageFile(...args)
}))

// Mock api.js
vi.mock('@/services/api.js', () => ({
  default: {
    post: vi.fn()
  },
  predictImage: vi.fn(),
  createPredictionFormData: vi.fn()
}))

// Mock composables
const mockFileUpload = {
  isDragging: { value: false },
  selectedFile: { value: null },
  imagePreview: { value: null },
  error: { value: '' },
  fileInput: { value: null },
  hasFile: { value: false },
  canSubmit: { value: false },
  formatFileSize: vi.fn((bytes) => `${bytes} bytes`),
  processFile: vi.fn(),
  handleDragOver: vi.fn(),
  handleDragLeave: vi.fn(),
  handleDrop: vi.fn(),
  openFileSelector: vi.fn(),
  handleFileSelect: vi.fn(),
  removeSelectedFile: vi.fn(),
  reset: vi.fn(),
  getFormData: vi.fn()
}

const mockPrediction = {
  isLoading: { value: false },
  error: { value: null },
  result: { value: null },
  executePrediction: vi.fn().mockResolvedValue({}),
  reset: vi.fn()
}

vi.mock('@/composables/useFileUpload', () => ({
  useFileUpload: () => mockFileUpload
}))

vi.mock('@/composables/usePrediction', () => ({
  usePrediction: () => mockPrediction
}))

describe('ImageUpload', () => {
  let wrapper
  let router

  beforeEach(() => {
    setActivePinia(createPinia())
    router = createRouter({
      history: createWebHistory(),
      routes: [{ path: '/', component: { template: '<div>Home</div>' } }]
    })
    vi.clearAllMocks()
    mockPredictionApi.validateImageFile.mockReturnValue({ valid: true })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render component', () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Análisis de Grano de Cacao')
  })

  it('should show upload area when no file selected', () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const uploadArea = wrapper.find('[class*="border-dashed"]')
    expect(uploadArea.exists()).toBe(true)
  })

  it('should accept file selection', async () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false
    })

    await input.trigger('change')

    expect(wrapper.vm.selectedFile).toBeDefined()
  })

  it('should handle drag and drop', async () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const dropArea = wrapper.find('[class*="border-dashed"]')

    const dragOverEvent = {
      preventDefault: vi.fn(),
      dataTransfer: {
        files: [file]
      }
    }

    await dropArea.trigger('dragover', dragOverEvent)
    expect(wrapper.vm.isDragging).toBe(true)

    const dropEvent = {
      preventDefault: vi.fn(),
      dataTransfer: {
        files: [file]
      }
    }

    await dropArea.trigger('drop', dropEvent)
    expect(wrapper.vm.isDragging).toBe(false)
  })

  it('should show error for invalid file', async () => {
    // validateImageFile returns an array of error strings, not an object
    mockPredictionApi.validateImageFile.mockReturnValue(['Formato no válido. Use JPG, PNG, BMP, TIFF'])

    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false
    })

    await input.trigger('change')
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error).toBe('Formato no válido. Use JPG, PNG, BMP, TIFF')
  })

  it('should disable submit button when no file selected', () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  it('should enable submit button when file is selected', async () => {
    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.selectedFile = file

    await wrapper.vm.$nextTick()

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeUndefined()
  })

  it('should show loading state during prediction', async () => {
    mockPredictionApi.predictImage.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.selectedFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.isLoading = true

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Analizando...')
  })

  it('should emit prediction-result on success', async () => {
    const mockResult = {
      success: true,
      data: {
        prediction: { weight: 1.5, dimensions: { width: 10, height: 12 } }
      }
    }

    mockPredictionApi.predictImage.mockResolvedValue(mockResult)

    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.selectedFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

    await wrapper.vm.handleSubmit()
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.emitted('prediction-result')).toBeTruthy()
  })

  it('should emit prediction-error on failure', async () => {
    const error = new Error('Prediction failed')
    mockPredictionApi.predictImage.mockRejectedValue(error)

    wrapper = mount(ImageUpload, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    wrapper.vm.selectedFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

    await wrapper.vm.handleSubmit()

    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('prediction-error')).toBeTruthy()
    expect(wrapper.vm.error).toBeTruthy()
  })
})

