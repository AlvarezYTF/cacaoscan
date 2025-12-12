import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageModal from '../ImageModal.vue'

describe('ImageModal', () => {
  let wrapper

  const mockImage = {
    fullSizeUrl: 'https://example.com/image-full.jpg',
    defects: [
      { type: 'Defect Type 1', confidence: 85 },
      { type: 'Defect Type 2', confidence: 92 },
      { type: 'Defect Type 3', confidence: 78 }
    ]
  }

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component when show is true', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should not render when show is false', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: false,
          image: mockImage
        }
      })

      const dialog = wrapper.find('dialog')
      expect(dialog.exists()).toBe(false)
    })

    it('should render modal title', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      expect(wrapper.text()).toContain('Imagen Analizada')
    })

    it('should render image', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const img = wrapper.find('img')
      expect(img.exists()).toBe(true)
      expect(img.attributes('src')).toBe(mockImage.fullSizeUrl)
    })

    it('should render defects section', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      expect(wrapper.text()).toContain('Defectos Detectados')
      expect(wrapper.text()).toContain('(3)')
    })
  })

  describe('Image Display', () => {
    it('should display full size image URL', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const img = wrapper.find('img')
      expect(img.attributes('src')).toBe(mockImage.fullSizeUrl)
    })

    it('should apply correct image styling', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const img = wrapper.find('img')
      expect(img.classes()).toContain('w-full')
      expect(img.classes()).toContain('max-h-[70vh]')
      expect(img.classes()).toContain('object-contain')
    })
  })

  describe('Defects Display', () => {
    it('should render all defects', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const defectItems = wrapper.findAll('li')
      expect(defectItems.length).toBe(3)
    })

    it('should display defect type and confidence', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      expect(wrapper.text()).toContain('Defect Type 1')
      expect(wrapper.text()).toContain('85%')
      expect(wrapper.text()).toContain('Defect Type 2')
      expect(wrapper.text()).toContain('92%')
    })

    it('should display correct defect count', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      expect(wrapper.text()).toContain('Defectos Detectados (3)')
    })

    it('should handle image with no defects', () => {
      const imageNoDefects = {
        fullSizeUrl: 'https://example.com/image.jpg',
        defects: []
      }

      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: imageNoDefects
        }
      })

      expect(wrapper.text()).toContain('Defectos Detectados (0)')
      const defectItems = wrapper.findAll('li')
      expect(defectItems.length).toBe(0)
    })

    it('should handle single defect', () => {
      const imageSingleDefect = {
        fullSizeUrl: 'https://example.com/image.jpg',
        defects: [{ type: 'Single Defect', confidence: 90 }]
      }

      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: imageSingleDefect
        }
      })

      expect(wrapper.text()).toContain('Defectos Detectados (1)')
      const defectItems = wrapper.findAll('li')
      expect(defectItems.length).toBe(1)
    })
  })

  describe('User Interactions', () => {
    it('should emit close event when close button is clicked', async () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const closeButton = wrapper.find('button[aria-label="Cerrar modal"]')
      await closeButton.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should emit close event when close button at bottom is clicked', async () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const closeButtons = wrapper.findAll('button')
      const bottomCloseButton = closeButtons.find((btn) => btn.text().includes('Cerrar'))
      
      if (bottomCloseButton) {
        await bottomCloseButton.trigger('click')
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })

    it('should emit close event when backdrop is clicked', async () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const backdrop = wrapper.find('.bg-gray-500')
      await backdrop.trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
    })

    it('should have accessible close button', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const closeButton = wrapper.find('button[aria-label="Cerrar modal"]')
      expect(closeButton.exists()).toBe(true)
    })
  })

  describe('Modal Attributes', () => {
    it('should have correct ARIA attributes', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const dialog = wrapper.find('dialog')
      expect(dialog.attributes('aria-labelledby')).toBe('modal-title')
      expect(dialog.attributes('aria-modal')).toBe('true')
    })

    it('should have open attribute when show is true', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: mockImage
        }
      })

      const dialog = wrapper.find('dialog')
      expect(dialog.attributes('open')).toBeDefined()
    })
  })

  describe('Edge Cases', () => {
    it('should handle default image object when not provided', () => {
      wrapper = mount(ImageModal, {
        props: {
          show: true
        }
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Imagen Analizada')
    })

    it('should handle empty defects array', () => {
      const emptyDefectsImage = {
        fullSizeUrl: 'https://example.com/image.jpg',
        defects: []
      }

      wrapper = mount(ImageModal, {
        props: {
          show: true,
          image: emptyDefectsImage
        }
      })

      expect(wrapper.text()).toContain('Defectos Detectados (0)')
    })
  })
})




