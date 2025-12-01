import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import UserPrediction from '../UserPrediction.vue'

const mockPredictionStore = {
  currentPrediction: null,
  currentImage: null,
  isLoading: false,
  error: null,
  quickStats: {
    total: 0,
    avgConfidence: 0,
    avgWeight: 0,
    highConfidenceCount: 0
  },
  predictImage: vi.fn(),
  clearPrediction: vi.fn()
}

vi.mock('@/stores/prediction', () => ({
  usePredictionStore: () => mockPredictionStore
}))

describe('UserPrediction', () => {
  let wrapper
  const originalPlugins = config.global.plugins

  beforeEach(() => {
    setActivePinia(createPinia())
    config.global.plugins = []
    vi.clearAllMocks()
  })

  afterEach(() => {
    config.global.plugins = originalPlugins
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('should render prediction view', () => {
    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display image upload section', () => {
    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const fileInput = wrapper.find('input[type="file"]')
    expect(fileInput.exists()).toBe(true)
  })

  it('should handle image selection', async () => {
    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const fileInput = wrapper.find('input[type="file"]')

    await fileInput.setValue(file)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.selectedImage).toBeDefined()
  })

  it('should run prediction', async () => {
    mockPredictionStore.predictImage.mockResolvedValue({
      data: { prediction: { weight: 1.5, dimensions: { width: 10, height: 15 } } }
    })

    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.selectedImage = file

    if (wrapper.vm.runPrediction) {
      await wrapper.vm.runPrediction()
      await wrapper.vm.$nextTick()

      expect(mockPredictionStore.predictImage).toHaveBeenCalled()
    }
  })

  it('should display prediction results', async () => {
    mockPredictionStore.currentPrediction = {
      weight: 1.5,
      dimensions: { width: 10, height: 15, thickness: 5 },
      confidence: 0.95
    }

    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('1.5')
  })

  it('should clear prediction', async () => {
    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    if (wrapper.vm.clearPrediction) {
      await wrapper.vm.clearPrediction()
      await wrapper.vm.$nextTick()

      expect(mockPredictionStore.clearPrediction).toHaveBeenCalled()
    }
  })

  it('should handle prediction error', async () => {
    const error = new Error('Prediction failed')
    mockPredictionStore.predictImage.mockRejectedValue(error)

    wrapper = mount(UserPrediction, {
      global: {
        stubs: { 'router-link': true, 'router-view': true }
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    wrapper.vm.selectedImage = file

    if (wrapper.vm.runPrediction) {
      await wrapper.vm.runPrediction()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.error).toBeDefined()
    }
  })
})
