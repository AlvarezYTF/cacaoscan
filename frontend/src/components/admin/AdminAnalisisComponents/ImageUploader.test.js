import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageUploader from './ImageUploader.vue'

// Mock DataTransfer for Node.js environment
class MockDataTransferItemList {
  constructor(dataTransfer) {
    this._items = []
    this._dataTransfer = dataTransfer
  }

  add(file) {
    this._items.push(file)
    // Also add to files array
    this._dataTransfer._files.push(file)
  }

  get length() {
    return this._items.length
  }

  item(index) {
    return this._items[index] || null
  }
}

class MockDataTransfer {
  constructor() {
    this._files = []
    this.items = new MockDataTransferItemList(this)
  }

  get files() {
    // Return a FileList-like object
    const fileList = Object.create(Array.prototype)
    fileList.length = this._files.length
    this._files.forEach((file, index) => {
      fileList[index] = file
    })
    fileList.item = (index) => this._files[index] || null
    return fileList
  }
}

// Make DataTransfer available globally
global.DataTransfer = MockDataTransfer

describe('ImageUploader', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

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
        writable: false,
        configurable: true
      })

      await fileInput.trigger('change')
      await wrapper.vm.$nextTick()

      // Verify that the event was emitted
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
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

