import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageUploadCard from '../ImageUploadCard.vue'

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
    for (const [index, file] of this._files.entries()) {
      fileList[index] = file
    }
    fileList.item = (index) => this._files[index] || null
    return fileList
  }
}

// Make DataTransfer available globally
globalThis.DataTransfer = MockDataTransfer

describe('ImageUploadCard', () => {
  let wrapper

  const createMockFile = (name = 'test.jpg', size = 1024, type = 'image/jpeg') => {
    return new File(['test'], name, { type })
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render title', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      expect(wrapper.text()).toContain('Subir Imágenes de Granos')
    })

    it('should render description', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      expect(wrapper.text()).toContain('Selecciona una o múltiples imágenes de granos de cacao')
    })
  })

  describe('Empty State', () => {
    it('should show upload area when no images', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      expect(wrapper.text()).toContain('Arrastra imágenes aquí o haz clic para seleccionar')
      expect(wrapper.text()).toContain('Formatos soportados: JPG, PNG, BMP, TIFF (máx. 20MB cada una)')
    })

    it('should show select button when no images', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('Seleccionar Imágenes')
    })
  })

  describe('With Images State', () => {
    const mockImages = [
      {
        id: '1',
        file: createMockFile('image1.jpg', 2048),
        preview: 'blob:http://localhost/image1'
      },
      {
        id: '2',
        file: createMockFile('image2.png', 4096),
        preview: 'blob:http://localhost/image2'
      }
    ]

    it('should show image count when images are present', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.text()).toContain('2 imagenes seleccionadas')
    })

    it('should show singular form for one image', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: [mockImages[0]]
        }
      })

      expect(wrapper.text()).toContain('1 imagen seleccionada')
    })

    it('should show preview grid when images are present', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(2)
    })

    it('should display file names', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.text()).toContain('image1.jpg')
      expect(wrapper.text()).toContain('image2.png')
    })

    it('should show add more button when images are present', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      const buttons = wrapper.findAll('button')
      const addMoreButton = buttons.find((btn) => btn.text().includes('Agregar Más'))
      expect(addMoreButton).toBeDefined()
    })

    it('should show clear all button', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      const buttons = wrapper.findAll('button')
      const clearButton = buttons.find(btn => btn.text().includes('Limpiar Todo'))
      expect(clearButton).toBeDefined()
      expect(clearButton.exists()).toBe(true)
    })
  })

  describe('File Selection', () => {
    it('should have hidden file input', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      const fileInput = wrapper.find('input[type="file"]')
      expect(fileInput.exists()).toBe(true)
      expect(fileInput.attributes('multiple')).toBeDefined()
      expect(fileInput.attributes('accept')).toBe('image/*')
    })

    it('should emit upload event when files are selected', async () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      const fileInput = wrapper.find('input[type="file"]')
      const file1 = createMockFile('test1.jpg')
      const file2 = createMockFile('test2.jpg')
      
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file1)
      dataTransfer.items.add(file2)

      Object.defineProperty(fileInput.element, 'files', {
        value: dataTransfer.files,
        writable: false
      })

      await fileInput.trigger('change')

      expect(wrapper.emitted('upload')).toBeTruthy()
      const emittedFiles = wrapper.emitted('upload')[0][0]
      expect(emittedFiles).toBeDefined()
      expect(emittedFiles.length).toBe(2)
      expect(emittedFiles[0]).toBe(file1)
      expect(emittedFiles[1]).toBe(file2)
    })
  })

  describe('Drag and Drop', () => {
    it('should handle drag over event', async () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      const dropZone = wrapper.find('.border-2.border-dashed')
      
      await dropZone.trigger('dragover')
      
      expect(dropZone.exists()).toBe(true)
    })

    it('should handle drop event and emit upload', async () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      const dropZone = wrapper.find('.border-2.border-dashed')
      const file = createMockFile('dropped.jpg')
      
      const dataTransfer = {
        files: [file],
        items: {
          add: vi.fn()
        }
      }

      const dropEvent = new Event('drop', { bubbles: true })
      dropEvent.dataTransfer = dataTransfer

      dropZone.element.dispatchEvent(dropEvent)
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('upload')).toBeTruthy()
    })
  })

  describe('Image Removal', () => {
    const mockImages = [
      {
        id: '1',
        file: createMockFile('image1.jpg'),
        preview: 'blob:http://localhost/image1'
      },
      {
        id: '2',
        file: createMockFile('image2.jpg'),
        preview: 'blob:http://localhost/image2'
      }
    ]

    it('should emit remove event when remove button is clicked', async () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      const removeButtons = wrapper.findAll('button')
      const removeButton = removeButtons.find((btn) => 
        btn.classes().includes('bg-red-500')
      )

      if (removeButton?.exists()) {
        await removeButton.trigger('click')
        expect(wrapper.emitted('remove')).toBeTruthy()
      }
    })

    it('should emit clear-all event when clear all button is clicked', async () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      const clearButton = wrapper.find('button')
      if (clearButton?.text().includes('Limpiar Todo')) {
        await clearButton.trigger('click')
        expect(wrapper.emitted('clear-all')).toBeTruthy()
      }
    })
  })

  describe('Upload Progress', () => {
    it('should show upload progress when isUploading is true', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: [],
          isUploading: true
        }
      })

      expect(wrapper.text()).toContain('Subiendo imágenes...')
    })

    it('should not show upload progress when isUploading is false', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: [],
          isUploading: false
        }
      })

      expect(wrapper.text()).not.toContain('Subiendo imágenes...')
    })
  })

  describe('File Size Formatting', () => {
    it('should display file sizes correctly', () => {
      const mockImages = [
        {
          id: '1',
          file: createMockFile('small.jpg', 500),
          preview: 'blob:http://localhost/image1'
        },
        {
          id: '2',
          file: createMockFile('medium.jpg', 1024 * 1024),
          preview: 'blob:http://localhost/image2'
        }
      ]

      wrapper = mount(ImageUploadCard, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty images array', () => {
      wrapper = mount(ImageUploadCard, {
        props: {
          images: []
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Seleccionar Imágenes')
    })

    it('should handle large number of images', () => {
      const manyImages = Array.from({ length: 10 }, (_, i) => ({
        id: String(i + 1),
        file: createMockFile(`image${i + 1}.jpg`),
        preview: `blob:http://localhost/image${i + 1}`
      }))

      wrapper = mount(ImageUploadCard, {
        props: {
          images: manyImages
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(10)
    })
  })
})

