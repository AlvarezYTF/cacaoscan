import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageUploader from '../ImageUploader.vue'

// Mock URL.createObjectURL
globalThis.URL.createObjectURL = vi.fn(() => 'blob:mock-url')

describe('ImageUploader', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })
  it('should render image uploader', () => {
    const wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    expect(wrapper.find('input[type="file"]').exists()).toBe(true)
  })

  it('should emit update:modelValue when files are selected', async () => {
    const wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    // Simulate file selection
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false
    })
    
    await input.trigger('change')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })
})

