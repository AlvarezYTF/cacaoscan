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
    for (let index = 0; index < this._files.length; index++) {
      fileList[index] = this._files[index]
    }
    fileList.item = (index) => this._files[index] || null
    return fileList
  }
}

// Make DataTransfer available globally
globalThis.DataTransfer = MockDataTransfer

describe('ImageUploader', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.unstubAllGlobals()
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

  it('should generate secure ID using crypto.randomUUID', () => {
    const mockRandomUUID = vi.fn().mockReturnValue('test-uuid')
    vi.stubGlobal('crypto', {
      randomUUID: mockRandomUUID
    })

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const id = wrapper.vm.generateSecureId()
    expect(id).toBe('test-uuid')
    expect(mockRandomUUID).toHaveBeenCalled()
  })

  it('should generate secure ID using crypto.getRandomValues as fallback', () => {
    const mockGetRandomValues = vi.fn().mockReturnValue(new Uint32Array([1, 2, 3, 4]))
    vi.stubGlobal('crypto', {
      getRandomValues: mockGetRandomValues,
      randomUUID: undefined
    })

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const id = wrapper.vm.generateSecureId()
    expect(id).toBeTruthy()
    expect(mockGetRandomValues).toHaveBeenCalled()
  })

  it('should get image key from File object', () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    Object.defineProperty(file, 'size', { value: 1000, writable: false })
    Object.defineProperty(file, 'lastModified', { value: 1234567890, writable: false })

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const key = wrapper.vm.getImageKey(file)
    expect(key).toContain('test.jpg')
  })

  it('should get image key from object with id', () => {
    const imageObj = { id: 'test-id', url: 'test.jpg' }

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const key = wrapper.vm.getImageKey(imageObj)
    expect(key).toBe('test-id')
  })

  it('should get image URL from File object', () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    globalThis.URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url')

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const url = wrapper.vm.getImageUrl(file)
    expect(url).toBe('blob:test-url')
  })

  it('should get image URL from object with url', () => {
    const imageObj = { url: 'https://example.com/image.jpg' }

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const url = wrapper.vm.getImageUrl(imageObj)
    expect(url).toBe('https://example.com/image.jpg')
  })

  it('should validate file type', () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const validFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const invalidFile = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    expect(wrapper.vm.validateFile(validFile)).toBe('')
    expect(wrapper.vm.validateFile(invalidFile)).toBeTruthy()
  })

  it('should validate file size', () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: [],
        maxFileSize: 5
      }
    })

    const smallFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    Object.defineProperty(smallFile, 'size', { value: 1024 * 1024, writable: false })

    const largeFile = new File(['test'], 'large.jpg', { type: 'image/jpeg' })
    Object.defineProperty(largeFile, 'size', { value: 10 * 1024 * 1024, writable: false })

    expect(wrapper.vm.validateFile(smallFile)).toBe('')
    expect(wrapper.vm.validateFile(largeFile)).toBeTruthy()
  })

  it('should handle file select and reset input', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const event = {
      target: {
        files: [file],
        value: 'test'
      }
    }

    wrapper.vm.fileInput = { value: 'test' }
    await wrapper.vm.handleFileSelect(event)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.fileInput.value).toBe('')
  })

  it('should handle drop event', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const event = {
      dataTransfer: {
        files: [file]
      }
    }

    wrapper.vm.isDragging = true
    await wrapper.vm.handleDrop(event)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isDragging).toBe(false)
  })

  it('should prevent adding files when maxFiles limit is reached', async () => {
    const existingFiles = Array.from({ length: 10 }, (_, i) => 
      new File(['test'], `test${i}.jpg`, { type: 'image/jpeg' })
    )

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: existingFiles,
        maxFiles: 10
      }
    })

    const newFile = new File(['test'], 'new.jpg', { type: 'image/jpeg' })
    await wrapper.vm.processFiles([newFile])
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.error).toBeTruthy()
    expect(wrapper.vm.error.includes('máximo de 10')).toBe(true)
  })

  it('should process valid files and add to images', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    await wrapper.vm.processFiles([file])
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.images.length).toBe(1)
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('should skip invalid files but add valid ones', async () => {
    wrapper = mount(ImageUploader, {
      props: {
        modelValue: []
      }
    })

    const validFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const invalidFile = new File(['test'], 'test.pdf', { type: 'application/pdf' })

    await wrapper.vm.processFiles([validFile, invalidFile])
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.images.length).toBe(1)
    expect(wrapper.vm.error).toBeTruthy()
  })

  it('should remove image from list', async () => {
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: [file]
      }
    })

    await wrapper.vm.removeImage(file)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.images.length).toBe(0)
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('should watch modelValue changes', async () => {
    const file1 = new File(['test'], 'test1.jpg', { type: 'image/jpeg' })
    const file2 = new File(['test'], 'test2.jpg', { type: 'image/jpeg' })

    wrapper = mount(ImageUploader, {
      props: {
        modelValue: [file1]
      }
    })

    await wrapper.setProps({ modelValue: [file1, file2] })
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.images.length).toBe(2)
  })
})

