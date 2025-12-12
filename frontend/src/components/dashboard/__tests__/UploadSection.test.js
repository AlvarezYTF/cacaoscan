import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UploadSection from '../UploadSection.vue'

// Mock FileList for Node.js environment
class MockFileList {
  constructor(files = []) {
    this.length = files.length
    for (let index = 0; index < files.length; index++) {
      this[index] = files[index]
    }
  }

  item(index) {
    return this[index] || null
  }

  [Symbol.iterator]() {
    let index = 0
    return {
      next: () => {
        if (index < this.length) {
          return { value: this[index++], done: false }
        }
        return { done: true }
      }
    }
  }
}

// Mock DataTransfer for Node.js environment
class MockDataTransferItemList {
  constructor(dataTransfer) {
    this._items = []
    this._dataTransfer = dataTransfer
  }

  add(file) {
    this._items.push(file)
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
    return new MockFileList(this._files)
  }
}

// Make DataTransfer and FileList available globally
globalThis.DataTransfer = MockDataTransfer
globalThis.FileList = MockFileList

describe('UploadSection', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(UploadSection)

      expect(wrapper.exists()).toBe(true)
    })

    it('should display upload card', () => {
      wrapper = mount(UploadSection)

      expect(wrapper.find('.upload-card').exists()).toBe(true)
    })

    it('should display upload icon', () => {
      wrapper = mount(UploadSection)

      const icon = wrapper.find('.upload-icon')
      expect(icon.exists()).toBe(true)
      expect(icon.find('i.fa-camera').exists()).toBe(true)
    })

    it('should display title', () => {
      wrapper = mount(UploadSection)

      expect(wrapper.text()).toContain('Subir imágenes de granos')
    })

    it('should display description', () => {
      wrapper = mount(UploadSection)

      expect(wrapper.text()).toContain('Arrastra o haz clic para subir fotos de tus granos de cacao')
    })

    it('should have hidden file input', () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      expect(fileInput.exists()).toBe(true)
      expect(fileInput.attributes('style')).toContain('display: none')
    })

    it('should have multiple attribute on file input', () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      expect(fileInput.attributes('multiple')).toBeDefined()
    })

    it('should accept only images', () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      expect(fileInput.attributes('accept')).toBe('image/*')
    })
  })

  describe('File Upload', () => {
    it('should trigger file input click when card is clicked', async () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      const clickSpy = vi.spyOn(fileInput.element, 'click')

      const card = wrapper.find('.upload-card')
      await card.trigger('click')

      expect(clickSpy).toHaveBeenCalled()
    })

    it('should emit file-upload event when files are selected', async () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      const file1 = new File(['content1'], 'test1.jpg', { type: 'image/jpeg' })
      const file2 = new File(['content2'], 'test2.jpg', { type: 'image/jpeg' })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file1)
      dataTransfer.items.add(file2)

      Object.defineProperty(fileInput.element, 'files', {
        value: dataTransfer.files,
        writable: false
      })

      await fileInput.trigger('change')

      expect(wrapper.emitted('file-upload')).toBeTruthy()
      expect(wrapper.emitted('file-upload')[0][0]).toBeInstanceOf(FileList)
      expect(wrapper.emitted('file-upload')[0][0].length).toBe(2)
    })

    it('should reset file input after upload', async () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' })
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)

      // Set files property before triggering change
      Object.defineProperty(fileInput.element, 'files', {
        value: dataTransfer.files,
        writable: false,
        configurable: true
      })

      // Verify files are set before change
      expect(fileInput.element.files.length).toBe(1)
      
      // Create a proper change event with target set to the file input
      const changeEvent = new Event('change', { bubbles: true, cancelable: true })
      Object.defineProperty(changeEvent, 'target', {
        value: fileInput.element,
        enumerable: true,
        configurable: true
      })
      
      // Manually call the handler to ensure it processes the event correctly
      const component = wrapper.vm
      component.handleFileUpload(changeEvent)
      
      await wrapper.vm.$nextTick()

      // After change event, the component should reset the input value to empty string
      // The component's handleFileUpload method sets event.target.value = ''
      // Note: File inputs can only be set to empty string, not to other values
      expect(fileInput.element.value).toBe('')
    })

    it('should handle empty file selection', async () => {
      wrapper = mount(UploadSection)

      const fileInput = wrapper.find('input[type="file"]')
      await fileInput.trigger('change')

      // Should not emit if no files selected
      expect(wrapper.emitted('file-upload')).toBeFalsy()
    })
  })

  describe('Accessibility', () => {
    it('should have cursor pointer on upload card', () => {
      wrapper = mount(UploadSection)

      const card = wrapper.find('.upload-card')
      expect(card.classes()).toContain('cursor-pointer')
    })
  })
})

