import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ImageGallery from '../ImageGallery.vue'

describe('ImageGallery', () => {
  let wrapper

  const mockImages = [
    {
      thumbnailUrl: 'https://example.com/image1.jpg',
      fullSizeUrl: 'https://example.com/image1-full.jpg',
      defects: [
        { type: 'Defect 1', confidence: 85 },
        { type: 'Defect 2', confidence: 92 }
      ]
    },
    {
      thumbnailUrl: 'https://example.com/image2.jpg',
      fullSizeUrl: 'https://example.com/image2-full.jpg',
      defects: [
        { type: 'Defect 3', confidence: 78 }
      ]
    },
    {
      thumbnailUrl: 'https://example.com/image3.jpg',
      fullSizeUrl: 'https://example.com/image3-full.jpg',
      defects: []
    }
  ]

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should render title', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.text()).toContain('Imágenes Analizadas')
    })

    it('should render all images', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(3)
    })

    it('should render empty state when no images', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: []
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(0)
      expect(wrapper.text()).toContain('Imágenes Analizadas')
    })
  })

  describe('Image Display', () => {
    it('should display thumbnail URLs correctly', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const images = wrapper.findAll('img')
      expect(images[0].attributes('src')).toBe(mockImages[0].thumbnailUrl)
      expect(images[1].attributes('src')).toBe(mockImages[1].thumbnailUrl)
      expect(images[2].attributes('src')).toBe(mockImages[2].thumbnailUrl)
    })

    it('should set correct alt text for images', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const images = wrapper.findAll('img')
      expect(images[0].attributes('alt')).toBe('1')
      expect(images[1].attributes('alt')).toBe('2')
      expect(images[2].attributes('alt')).toBe('3')
    })

    it('should display defect count for each image', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      expect(wrapper.text()).toContain('2 defectos')
      expect(wrapper.text()).toContain('1 defecto')
      expect(wrapper.text()).toContain('0 defectos')
    })

    it('should use singular form for one defect', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: [mockImages[1]]
        }
      })

      expect(wrapper.text()).toContain('1 defecto')
      expect(wrapper.text()).not.toContain('1 defectos')
    })

    it('should use plural form for multiple defects', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: [mockImages[0]]
        }
      })

      expect(wrapper.text()).toContain('2 defectos')
    })
  })

  describe('User Interactions', () => {
    it('should emit image-click event when image is clicked', async () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThan(0)
      
      await buttons[0].trigger('click')

      expect(wrapper.emitted('image-click')).toBeTruthy()
      expect(wrapper.emitted('image-click')[0]).toEqual([mockImages[0]])
    })

    it('should show hover overlay on image hover', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const overlay = wrapper.find(String.raw`.group-hover\:opacity-100`)
      expect(overlay.exists()).toBe(true)
    })

    it('should have accessible button labels', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const button = wrapper.find('button[aria-label="Ver detalles de la imagen"]')
      expect(button.exists()).toBe(true)
    })
  })

  describe('Layout and Styling', () => {
    it('should render grid layout', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const grid = wrapper.find('.grid')
      expect(grid.exists()).toBe(true)
      expect(grid.classes()).toContain('grid-cols-2')
      expect(grid.classes()).toContain('sm:grid-cols-3')
      expect(grid.classes()).toContain('md:grid-cols-4')
    })

    it('should apply correct image styling', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const images = wrapper.findAll('img')
      for (const img of images) {
        expect(img.classes()).toContain('w-full')
        expect(img.classes()).toContain('h-32')
        expect(img.classes()).toContain('object-cover')
      }
    })

    it('should display defect count overlay', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: mockImages
        }
      })

      const overlays = wrapper.findAll('.bg-black.bg-opacity-70')
      expect(overlays.length).toBe(3)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty images array', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: []
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(0)
    })

    it('should handle images with no defects', () => {
      const imageWithoutDefects = [{
        thumbnailUrl: 'https://example.com/image.jpg',
        defects: []
      }]

      wrapper = mount(ImageGallery, {
        props: {
          images: imageWithoutDefects
        }
      })

      expect(wrapper.text()).toContain('0 defectos')
    })

    it('should handle single image', () => {
      wrapper = mount(ImageGallery, {
        props: {
          images: [mockImages[0]]
        }
      })

      const images = wrapper.findAll('img')
      expect(images.length).toBe(1)
    })
  })
})



