/**
 * Unit tests for BaseImageModal component
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import BaseImageModal from '../BaseImageModal.vue'

describe('BaseImageModal', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    // Clean up teleported content from document.body
    document.body.innerHTML = ''
  })

  describe('Props validation', () => {
    it('should accept modelValue prop', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true
        }
      })
      expect(wrapper.exists()).toBe(true)
    })

    it('should accept imageSrc prop', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageSrc: 'test.jpg'
        }
      })
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('Rendering', () => {
    it('should render modal when modelValue is true', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const modalElement = document.body.querySelector('.fixed')
      expect(modalElement).toBeTruthy()
    })

    it('should not render modal when modelValue is false', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: false
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const modalElement = document.body.querySelector('.fixed')
      expect(modalElement).toBeFalsy()
    })

    it('should render title when provided', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          title: 'Test Title'
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const modalContent = document.body.querySelector('.fixed')
      expect(modalContent).toBeTruthy()
      expect(modalContent.textContent).toContain('Test Title')
    })

    it('should render image when imageSrc is provided', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageSrc: 'test.jpg'
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const img = document.body.querySelector('img[src="test.jpg"]')
      expect(img).toBeTruthy()
    })

    it('should show navigation buttons when multiple images', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageSrc: 'test.jpg',
          imageIndex: 1,
          totalImages: 3,
          showNavigation: true
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const navButtons = document.body.querySelectorAll('button[aria-label="Imagen anterior"], button[aria-label="Imagen siguiente"]')
      expect(navButtons.length).toBeGreaterThan(1)
    })

    it('should show loading state when loading is true', async () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          loading: true
        }
      })
      await nextTick() // Wait for teleported content to render

      const loadingElement = document.body.querySelector('.animate-spin')
      expect(loadingElement).toBeTruthy()
    })

    it('should show error state when error is provided', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          error: 'Test error'
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const modalContent = document.body.querySelector('.fixed')
      expect(modalContent).toBeTruthy()
      expect(modalContent.textContent).toContain('Test error')
    })
  })

  describe('Computed properties', () => {
    it('should compute canNavigatePrevious correctly', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageIndex: 1,
          totalImages: 3
        }
      })

      expect(wrapper.vm.canNavigatePrevious).toBe(true)
    })

    it('should compute canNavigateNext correctly', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageIndex: 1,
          totalImages: 3
        }
      })

      expect(wrapper.vm.canNavigateNext).toBe(true)
    })
  })

  describe('Events', () => {
    it('should emit update:modelValue when close button is clicked', async () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true
        },
        attachTo: document.body
      })

      // Since the component uses Teleport, button is rendered in body
      const closeButton = document.body.querySelector('button[aria-label="Cerrar"]')
      expect(closeButton).toBeTruthy()
      await closeButton.click()

      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toBe(false)
    })

    it('should emit previous event when previous button is clicked', async () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageSrc: 'test.jpg', // Added imageSrc to ensure navigation buttons are rendered
          imageIndex: 1,
          totalImages: 3,
          showNavigation: true
        }
      })

      await wrapper.vm.$nextTick()
      // Since the component uses Teleport, we need to find the button in the actual DOM
      const prevButton = document.body.querySelector('button[aria-label="Imagen anterior"]')
      expect(prevButton).toBeTruthy()
      prevButton.click() // Simulate click on the actual DOM element
      await wrapper.vm.$nextTick()

      expect(wrapper.emitted('previous')).toBeTruthy()
    })

    it('should emit next event when next button is clicked', async () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          imageIndex: 1,
          totalImages: 3,
          showNavigation: true
        },
        attachTo: document.body
      })

      await wrapper.vm.$nextTick()

      const nextButton = document.body.querySelector('button[aria-label="Imagen siguiente"]')
      expect(nextButton).toBeTruthy()
      await nextButton.click()

      expect(wrapper.emitted('next')).toBeTruthy()
    })
  })

  describe('Slots', () => {
    it('should render header-actions slot when provided', () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true
        },
        slots: {
          'header-actions': '<button>Action</button>'
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      const modalContent = document.body.querySelector('.fixed')
      expect(modalContent).toBeTruthy()
      expect(modalContent.textContent).toContain('Action')
    })

    it('should render footer slot when provided', async () => {
      wrapper = mount(BaseImageModal, {
        props: {
          modelValue: true,
          showActions: true
        },
        slots: {
          footer: '<div>Footer</div>'
        }
      })

      // Since the component uses Teleport, we need to check the actual DOM
      await wrapper.vm.$nextTick() // Wait for Teleport content to render
      const modalContent = document.body.querySelector('.fixed')
      expect(modalContent).toBeTruthy()
      expect(modalContent.textContent).toContain('Footer')
    })
  })
})

