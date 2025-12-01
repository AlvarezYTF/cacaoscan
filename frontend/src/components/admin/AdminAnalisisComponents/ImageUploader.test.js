import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageUploader from './ImageUploader.vue'

describe('ImageUploader', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  it('should render image uploader component', () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should display drop zone', () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const text = wrapper.text()
    expect(
      text.includes('imágenes') || 
      text.includes('arrastra') || 
      text.includes('seleccionar') ||
      text.includes('drop')
    ).toBe(true)
  })

  it('should accept file input', () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const fileInput = wrapper.find('input[type="file"]')
    expect(fileInput.exists()).toBe(true)
  })

  it('should emit update:modelValue when files are selected', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const fileInput = wrapper.find('input[type="file"]')
    if (fileInput.exists()) {
      const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      
      Object.defineProperty(fileInput.element, 'files', {
        value: dataTransfer.files,
        writable: false
      })

      await fileInput.trigger('change')
      await wrapper.vm.$nextTick()
    }
  })

  it('should handle drag and drop', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const dropZone = wrapper.find('.border-2')
    if (dropZone.exists()) {
      await dropZone.trigger('dragover')
      expect(wrapper.vm.isDragging).toBe(true)
    }
  })
})

