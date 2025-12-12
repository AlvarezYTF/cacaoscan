import { describe, it, expect, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LegalLayout from '../LegalLayout.vue'

describe('LegalLayout', () => {
  let wrapper

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render component', () => {
      wrapper = mount(LegalLayout)

      expect(wrapper.exists()).toBe(true)
    })

    it('should render main section', () => {
      wrapper = mount(LegalLayout)

      const section = wrapper.find('section')
      expect(section.exists()).toBe(true)
    })

    it('should render container', () => {
      wrapper = mount(LegalLayout)

      const container = wrapper.find('.max-w-5xl')
      expect(container.exists()).toBe(true)
    })
  })

  describe('Slots', () => {
    it('should render header slot', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          header: '<div class="test-header">Header Content</div>'
        }
      })

      expect(wrapper.find('.test-header').exists()).toBe(true)
      expect(wrapper.text()).toContain('Header Content')
    })

    it('should render default header slot when provided', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          header: '<h1>Test Title</h1>'
        }
      })

      expect(wrapper.text()).toContain('Test Title')
    })

    it('should render index slot when provided', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          index: '<nav class="test-index">Index Content</nav>'
        }
      })

      expect(wrapper.find('.test-index').exists()).toBe(true)
      expect(wrapper.text()).toContain('Index Content')
    })

    it('should not render index slot when not provided', () => {
      wrapper = mount(LegalLayout)

      const allDivsWithMb8 = wrapper.findAll('div').filter(div => 
        div.classes().includes('mb-8')
      )
      
      const indexContainer = allDivsWithMb8.find(div => 
        !div.classes().includes('border-b') && 
        !div.classes().includes('bg-white') &&
        !div.classes().includes('rounded-2xl')
      )
      
      expect(indexContainer).toBeUndefined()
    })

    it('should render content slot', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          content: '<div class="test-content">Main Content</div>'
        }
      })

      expect(wrapper.find('.test-content').exists()).toBe(true)
      expect(wrapper.text()).toContain('Main Content')
    })

    it('should render actions slot when provided', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          actions: '<div class="test-actions">Actions Content</div>'
        }
      })

      expect(wrapper.find('.test-actions').exists()).toBe(true)
      expect(wrapper.text()).toContain('Actions Content')
    })

    it('should not render actions slot when not provided', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          content: '<p>Content only</p>'
        }
      })

      const actionsContainer = wrapper.find('.mt-8.pt-6')
      expect(actionsContainer.exists()).toBe(false)
    })
  })

  describe('Multiple Slots', () => {
    it('should render all slots together', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          header: '<h1>Header</h1>',
          index: '<nav>Index</nav>',
          content: '<p>Content</p>',
          actions: '<button>Action</button>'
        }
      })

      expect(wrapper.text()).toContain('Header')
      expect(wrapper.text()).toContain('Index')
      expect(wrapper.text()).toContain('Content')
      expect(wrapper.text()).toContain('Action')
    })
  })

  describe('Layout Structure', () => {
    it('should have correct section styling', () => {
      wrapper = mount(LegalLayout)

      const section = wrapper.find('section')
      expect(section.classes()).toContain('min-h-screen')
      expect(section.classes()).toContain('bg-gray-50')
    })

    it('should have correct container styling', () => {
      wrapper = mount(LegalLayout)

      const container = wrapper.find('.max-w-5xl')
      expect(container.classes()).toContain('mx-auto')
    })

    it('should have correct content container styling', () => {
      wrapper = mount(LegalLayout)

      const contentContainer = wrapper.find('.bg-white')
      expect(contentContainer.classes()).toContain('rounded-2xl')
      expect(contentContainer.classes()).toContain('shadow-lg')
    })
  })

  describe('Content Styling', () => {
    it('should apply prose classes to content', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          content: '<div>Content</div>'
        }
      })

      const prose = wrapper.find('.prose')
      expect(prose.exists()).toBe(true)
      expect(prose.classes()).toContain('max-w-none')
    })

    it('should have border separator for header', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          header: '<h1>Header</h1>'
        }
      })

      const headerBorder = wrapper.find('.border-b')
      expect(headerBorder.exists()).toBe(true)
    })

    it('should have border separator for actions', () => {
      wrapper = mount(LegalLayout, {
        slots: {
          actions: '<button>Action</button>'
        }
      })

      const actionsBorder = wrapper.find('.border-t')
      expect(actionsBorder.exists()).toBe(true)
    })
  })
})

